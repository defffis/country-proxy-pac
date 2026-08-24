from __future__ import annotations

import concurrent.futures
import ipaddress
import json
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
CONNECT_TIMEOUT = 2
READ_TIMEOUT = 4
MAX_CANDIDATES = 1500
MAX_WORKERS = 80
MAX_PAC_PROXIES = 40
USER_AGENT = "turkey-proxy-pac/3.0"

# Multiple HTTPS endpoints reduce false negatives caused by one endpoint being
# temporarily unavailable or blocked through a particular public proxy.
IP_CHECK_URLS = [
    "https://api.ipify.org?format=json",
    "https://api64.ipify.org?format=json",
    "https://ifconfig.me/ip",
]
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
            and ip.is_global
            and 1 <= port_number <= 65535
        )
    except (ValueError, TypeError):
        return False


def tcp_precheck(proxy: str) -> bool:
    """Cheap socket-level liveness check before expensive HTTPS validation."""
    import socket

    host, port = proxy.rsplit(":", 1)
    try:
        with socket.create_connection((host, int(port)), timeout=CONNECT_TIMEOUT):
            return True
    except (OSError, ValueError):
        return False


def parse_external_ip(response: requests.Response) -> str | None:
    content_type = response.headers.get("content-type", "").lower()
    try:
        if "json" in content_type:
            value = str(response.json().get("ip", "")).strip()
        else:
            value = response.text.strip().splitlines()[0]
        ipaddress.ip_address(value)
        return value
    except (ValueError, TypeError, KeyError, IndexError):
        return None


def check_proxy(proxy: str) -> dict | None:
    if not tcp_precheck(proxy):
        return None

    host, port = proxy.rsplit(":", 1)
    proxy_url = f"http://{host}:{port}"
    proxies = {"http": proxy_url, "https": proxy_url}
    started = time.perf_counter()

    try:
        external_ip = None
        last_error = None

        for url in IP_CHECK_URLS:
            try:
                response = requests.get(
                    url,
                    proxies=proxies,
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    headers={"User-Agent": USER_AGENT},
                )
                response.raise_for_status()
                external_ip = parse_external_ip(response)
                if external_ip:
                    break
            except (requests.RequestException, ValueError, TypeError) as exc:
                last_error = exc

        if not external_ip:
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
    candidates_list = list(candidates)[:MAX_CANDIDATES]

    print(f"Candidates after validation: {len(candidates_list)}")

    # Stage 1: cheap TCP pre-check, performed in parallel.
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tcp_results = list(executor.map(tcp_precheck, candidates_list))

    live_candidates = [
        proxy for proxy, is_alive in zip(candidates_list, tcp_results) if is_alive
    ]
    print(f"TCP-live candidates: {len(live_candidates)}")

    # Stage 2: HTTPS CONNECT + external IP + GeoIP.
    working: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {
            executor.submit(check_proxy, proxy): proxy
            for proxy in live_candidates
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
                print(f"[{index}/{len(live_candidates)}] ERROR {proxy}: {exc}")

            if result:
                working.append(result)
                print(
                    f"[{index}/{len(live_candidates)}] OK "
                    f"{proxy} -> {result['ip']} "
                    f"{result['city'] or '-'} "
                    f"{result['latency_ms']} ms"
                )

    working.sort(key=lambda item: (item["latency_ms"], item["proxy"]))
    working = working[:MAX_PAC_PROXIES]
    proxy_list = [item["proxy"] for item in working]

    updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    stats = {
        "updated_at": updated_at,
        "sources": len(SOURCES),
        "candidates": len(candidates_list),
        "tcp_live_candidates": len(live_candidates),
        "working_turkey_proxies": len(working),
        "max_workers": MAX_WORKERS,
        "https_validation": True,
        "ip_check_endpoints": len(IP_CHECK_URLS),
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
