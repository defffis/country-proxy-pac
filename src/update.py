from __future__ import annotations

import concurrent.futures
import ipaddress
import json
import re
import socket
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PAC = ROOT / "pac"
DATA.mkdir(exist_ok=True)
PAC.mkdir(exist_ok=True)

# Sources are tagged with the protocol advertised by the list. This matters:
# an address on a SOCKS list must not be tested as an HTTP proxy, and HTTPS
# proxy lists need an HTTPS proxy URL when tested by requests.
SOURCES = [
    ("http", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"),
    ("http", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"),
    ("http", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt"),
    ("https", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt"),
    ("socks4", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt"),
    ("socks5", "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt"),
]

SOURCE_TIMEOUT = 20
CONNECT_TIMEOUT = 2
READ_TIMEOUT = 5
MAX_CANDIDATES = 4000
MAX_WORKERS = 80
MAX_PAC_PROXIES = 40
USER_AGENT = "turkey-proxy-pac/4.0"

IP_CHECK_URLS = [
    "https://api.ipify.org?format=json",
    "https://api64.ipify.org?format=json",
    "https://ifconfig.me/ip",
    "https://icanhazip.com/",
]
HTTPS_TEST_URLS = [
    "https://www.google.com/generate_204",
    "https://www.cloudflare.com/cdn-cgi/trace",
    "https://example.com/",
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
        return ip.version == 4 and ip.is_global and 1 <= port_number <= 65535
    except (ValueError, TypeError):
        return False


def tcp_precheck(candidate: tuple[str, str]) -> bool:
    _, proxy = candidate
    host, port = proxy.rsplit(":", 1)
    try:
        with socket.create_connection((host, int(port)), timeout=CONNECT_TIMEOUT):
            return True
    except (OSError, ValueError):
        return False


def proxy_url(proxy_type: str, proxy: str) -> str:
    host, port = proxy.rsplit(":", 1)
    if proxy_type == "https":
        return f"https://{host}:{port}"
    if proxy_type == "socks4":
        return f"socks4://{host}:{port}"
    if proxy_type == "socks5":
        return f"socks5h://{host}:{port}"
    return f"http://{host}:{port}"


def parse_external_ip(response: requests.Response) -> str | None:
    try:
        content_type = response.headers.get("content-type", "").lower()
        if "json" in content_type:
            value = str(response.json().get("ip", "")).strip()
        else:
            value = response.text.strip().splitlines()[0]
        ipaddress.ip_address(value)
        return value
    except (ValueError, TypeError, KeyError, IndexError):
        return None


def get_external_ip(session: requests.Session) -> tuple[str | None, str | None]:
    for url in IP_CHECK_URLS:
        try:
            response = session.get(
                url,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            external_ip = parse_external_ip(response)
            if external_ip:
                return external_ip, url
        except (requests.RequestException, ValueError, TypeError):
            continue
    return None, None


def https_probe(session: requests.Session) -> str | None:
    for url in HTTPS_TEST_URLS:
        try:
            response = session.get(
                url,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                headers={"User-Agent": USER_AGENT},
            )
            if response.status_code < 500:
                return url
        except requests.RequestException:
            continue
    return None


def check_candidate(candidate: tuple[str, str]) -> dict | None:
    proxy_type, proxy = candidate
    started = time.perf_counter()
    session = requests.Session()
    url = proxy_url(proxy_type, proxy)
    session.proxies.update({"http": url, "https": url})

    try:
        external_ip, ip_endpoint = get_external_ip(session)
        if not external_ip:
            return None

        https_endpoint = https_probe(session)
        if not https_endpoint:
            return None

        # GeoIP is intentionally queried directly, not through the candidate.
        geo_response = requests.get(
            GEO_URL.format(ip=external_ip),
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            headers={"User-Agent": USER_AGENT},
        )
        geo_response.raise_for_status()
        geo = geo_response.json()

        if not geo.get("success"):
            return None

        elapsed = round((time.perf_counter() - started) * 1000)
        return {
            "proxy": proxy,
            "type": proxy_type,
            "ip": external_ip,
            "country": geo.get("country_code"),
            "city": geo.get("city"),
            "latency_ms": elapsed,
            "ip_check": ip_endpoint,
            "https_check": https_endpoint,
        }
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None
    finally:
        session.close()


def make_pac(proxies: list[str]) -> str:
    lines = [
        "// Auto-generated. Do not edit manually.",
        "// Verified Turkish HTTP/HTTPS proxies with HTTPS support.",
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
    candidates: set[tuple[str, str]] = set()
    source_stats: dict[str, dict] = {}

    for proxy_type, source in SOURCES:
        key = f"{proxy_type}:{source}"
        try:
            found = extract_proxies(get_text(source))
            valid = {proxy for proxy in found if ip_is_valid(proxy)}
            candidates.update((proxy_type, proxy) for proxy in valid)
            source_stats[key] = {"found": len(found), "valid": len(valid)}
            print(f"SOURCE {proxy_type} {source}: {len(valid)} valid")
        except Exception as exc:
            source_stats[key] = {"found": 0, "valid": 0, "error": str(exc)}
            print(f"SOURCE FAILED {proxy_type} {source}: {exc}")

    candidates_list = list(candidates)[:MAX_CANDIDATES]
    print(f"Candidates after validation: {len(candidates_list)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tcp_results = list(executor.map(tcp_precheck, candidates_list))

    live_candidates = [
        candidate for candidate, alive in zip(candidates_list, tcp_results) if alive
    ]
    print(f"TCP-live candidates: {len(live_candidates)}")

    diagnostics = {
        "http_tested": 0,
        "https_proxy_tested": 0,
        "socks4_tested": 0,
        "socks5_tested": 0,
        "external_ip_found": 0,
        "https_ok": 0,
        "geoip_ok": 0,
        "turkey": 0,
    }
    for proxy_type, _ in live_candidates:
        diagnostics[f"{proxy_type}_tested"] += 1

    working: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_candidate, candidate): candidate for candidate in live_candidates}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception:
                result = None
            if not result:
                continue

            diagnostics["external_ip_found"] += 1
            diagnostics["https_ok"] += 1
            diagnostics["geoip_ok"] += 1
            if result["country"] == "TR":
                diagnostics["turkey"] += 1
                working.append(result)
                print(
                    f"TR {result['type']} {result['proxy']} -> "
                    f"{result['ip']} {result['city'] or '-'} "
                    f"{result['latency_ms']} ms"
                )

    working.sort(key=lambda item: (item["latency_ms"], item["proxy"]))

    # PAC supports the HTTP proxy scheme. SOCKS results remain available in
    # proxies.json for diagnostics, but are deliberately not inserted into PAC.
    pac_candidates = [item for item in working if item["type"] in {"http", "https"}]
    pac_candidates = pac_candidates[:MAX_PAC_PROXIES]
    pac_proxy_list = [item["proxy"] for item in pac_candidates]

    updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    stats = {
        "updated_at": updated_at,
        "sources": len(SOURCES),
        "candidates": len(candidates_list),
        "tcp_live_candidates": len(live_candidates),
        "working_turkey_proxies": len(working),
        "pac_http_proxies": len(pac_candidates),
        "max_workers": MAX_WORKERS,
        "https_validation": True,
        "ip_check_endpoints": len(IP_CHECK_URLS),
        "https_test_endpoints": len(HTTPS_TEST_URLS),
        "geoip": "ipwho.is",
        "selection": "lowest HTTPS latency",
        "diagnostics": diagnostics,
        "source_stats": source_stats,
    }

    (DATA / "proxies.json").write_text(
        json.dumps(working, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DATA / "stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (PAC / "turkey.pac").write_text(make_pac(pac_proxy_list), encoding="utf-8")
    (PAC / "turkey-http.pac").write_text(make_pac(pac_proxy_list), encoding="utf-8")

    print(f"Working Turkey proxies: {len(working)}")
    print(f"HTTP/HTTPS proxies for PAC: {len(pac_candidates)}")
    print("PAC files generated successfully.")


if __name__ == "__main__":
    main()
