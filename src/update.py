from __future__ import annotations

import concurrent.futures
import ipaddress
import json
import random
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PAC = ROOT / "pac"
DATA.mkdir(exist_ok=True)
PAC.mkdir(exist_ok=True)

SOURCES = [
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt",
    "https://raw.githubusercontent.com/mzyui/proxy-list/main/proxy-list/http.txt",
    "https://raw.githubusercontent.com/mzyui/proxy-list/main/proxy-list/https.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt",
]

SOURCE_TIMEOUT = 20
CONNECT_TIMEOUT = 3
READ_TIMEOUT = 5
MAX_CANDIDATES = 500
MAX_WORKERS = 40
MAX_PAC_PROXIES = 40
USER_AGENT = "turkey-proxy-pac/2.0"

# HTTPS endpoint: a proxy must successfully establish a TLS connection and
# return an externally visible IP. A plain TCP/open-port check is not enough.
IP_CHECK_URL = "https://api.ipify.org?format=json"
GEO_URL = "https://ipwho.is/{ip}"


def get_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=SOURCE_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


def extract_proxies(text: str) -> set[str]:
    return set(
        re.findall(
            r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}(?!\d)",
            text,
        )
    )


def ip_is_valid(proxy: str) -> bool:
    try:
        host, port = proxy.rsplit(":", 1)
        ip = ipaddress.ip_address(host)
        port_number = int(port)
        return (
            ip.version == 4
            and not ip.is_private
            and not ip.is_loopback
            and not ip.is_reserved
            and not ip.is_multicast
            and 1 <= port_number <= 65535
        )
    except (ValueError, TypeError):
        return False


def check_proxy(proxy: str) -> dict | None:
    host, port = proxy.rsplit(":", 1)
    proxy_url = f"http://{host}:{port}"
    proxies = {"http": proxy_url, "https": proxy_url}
    started = time.perf_counter()

    try:
        # This is deliberately HTTPS. requests will use HTTP CONNECT through
        # the candidate proxy, so a proxy that only accepts plain HTTP traffic
        # but cannot tunnel HTTPS is rejected.
        response = requests.get(
            IP_CHECK_URL,
            proxies=proxies,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        data = response.json()
        external_ip = str(data.get("ip", "")).strip()

        try:
            ipaddress.ip_address(external_ip)
        except ValueError:
            return None

        geo_response = requests.get(
            GEO_URL.format(ip=external_ip),
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            headers={"User-Agent": USER_AGENT},
        )
        geo_response.raise_for_status()
        geo = geo_response.json()

        if not geo.get("success") or geo.get("country_code") != "TR":
            return None

        elapsed = round((time.perf_counter() - started) * 1000)
        return {
            "proxy": proxy,
            "ip": external_ip,
            "country": "TR",
            "city": geo.get("city"),
            "latency_ms": elapsed,
        }
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None


def make_pac(proxies: list[str]) -> str:
    lines = [
        "// Auto-generated. Do not edit manually.",
        "// Verified Turkey HTTP proxies with HTTPS CONNECT support.",
        "function FindProxyForURL(url, host) {",
    ]

    if proxies:
        chain = "; ".join(f"PROXY {proxy}" for proxy in proxies)
        lines.append(f'    return "{chain}; DIRECT";')
    else:
        lines.append('    return "DIRECT";')

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    candidates: set[str] = set()

    for source in SOURCES:
        try:
            text = get_text(source)
            found = extract_proxies(text)
            candidates.update(found)
            print(f"SOURCE {source}: {len(found)} candidates")
        except Exception as exc:
            print(f"SOURCE FAILED {source}: {exc}")

    candidates = {proxy for proxy in candidates if ip_is_valid(proxy)}

    # Keep the candidate set bounded for GitHub Actions. Shuffling prevents
    # the same alphabetically early sources from monopolizing every run.
    candidates_list = list(candidates)
    random.SystemRandom().shuffle(candidates_list)
    candidates_list = candidates_list[:MAX_CANDIDATES]

    print(f"Candidates after validation: {len(candidates_list)}")

    working: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {
            executor.submit(check_proxy, proxy): proxy
            for proxy in candidates_list
        }

        for index, future in enumerate(
            concurrent.futures.as_completed(future_map),
            start=1,
        ):
            proxy = future_map[future]
            try:
                result = future.result()
            except Exception as exc:
                result = None
                print(f"[{index}/{len(candidates_list)}] ERROR {proxy}: {exc}")

            if result:
                working.append(result)
                print(
                    f"[{index}/{len(candidates_list)}] OK "
                    f"{proxy} -> {result['ip']} "
                    f"{result['city'] or '-'} "
                    f"{result['latency_ms']} ms"
                )
            else:
                print(f"[{index}/{len(candidates_list)}] FAIL {proxy}")

    # Fast proxies first. Add a small random tie-breaker so equal-latency
    # entries do not permanently occupy the same PAC positions.
    working.sort(key=lambda item: (item["latency_ms"], item["proxy"]))
    working = working[:MAX_PAC_PROXIES]

    proxy_list = [item["proxy"] for item in working]

    updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    stats = {
        "updated_at": updated_at,
        "sources": len(SOURCES),
        "candidates": len(candidates_list),
        "working_turkey_proxies": len(working),
        "max_workers": MAX_WORKERS,
        "https_validation": True,
        "geoip": "ipwho.is",
        "selection": "lowest HTTPS latency",
    }

    (DATA / "proxies.json").write_text(
        json.dumps(working, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (DATA / "stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (PAC / "turkey.pac").write_text(make_pac(proxy_list), encoding="utf-8")
    (PAC / "turkey-http.pac").write_text(make_pac(proxy_list), encoding="utf-8")

    print(f"Working Turkey proxies: {len(working)}")
    print("PAC files generated successfully.")


if __name__ == "__main__":
    main()
