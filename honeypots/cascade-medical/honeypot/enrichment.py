"""
IP Enrichment — GeoIP + AbuseIPDB + rDNS with async caching.
"""

import asyncio
import aiohttp
import socket
import logging
from functools import lru_cache

logger = logging.getLogger("enrichment")

_cache: dict = {}


async def enrich_ip(ip: str) -> dict:
    if ip in _cache:
        return _cache[ip]

    result = {"ip": ip, "country": None, "city": None, "asn": None,
              "isp": None, "is_vpn": False, "is_cloud": False,
              "abuse_confidence": 0, "rdns": None}

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            # GeoIP via ip-api.com (free, no key)
            async with session.get(
                f"http://ip-api.com/json/{ip}?fields=country,city,isp,org,as,hosting"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result["country"] = data.get("country")
                    result["city"] = data.get("city")
                    result["isp"] = data.get("isp") or data.get("org")
                    result["asn"] = data.get("as")
                    result["is_cloud"] = bool(data.get("hosting"))
    except Exception as e:
        logger.debug(f"GeoIP lookup failed for {ip}: {e}")

    # rDNS
    try:
        loop = asyncio.get_running_loop()
        rdns = await loop.run_in_executor(None, socket.gethostbyaddr, ip)
        result["rdns"] = rdns[0] if rdns else None
    except Exception:
        pass

    # AbuseIPDB (requires API key in environment)
    import os
    abuseipdb_key = os.environ.get("ABUSEIPDB_API_KEY")
    if abuseipdb_key:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    headers={"Key": abuseipdb_key, "Accept": "application/json"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result["abuse_confidence"] = data.get("data", {}).get("abuseConfidenceScore", 0)
                        result["is_vpn"] = data.get("data", {}).get("usageType", "") in (
                            "VPN Service", "Tor Exit Node", "Anonymous Proxy"
                        )
        except Exception as e:
            logger.debug(f"AbuseIPDB lookup failed for {ip}: {e}")

    _cache[ip] = result
    return result
