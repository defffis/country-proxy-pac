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
PROXIES = ROOT / "proxies"
for directory in (DATA, PAC, PROXIES):
    directory.mkdir(exist_ok=True)

TARGET_COUNTRIES = {
    "TR": "turkey",
    "IN": "india",
    "PL": "poland",
    "NL": "netherlands",
    "DE": "germany",
    "US": "usa",
    "GB": "uk",
}

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
MAX_PAC_PROXIES_PER_COUNTRY = 40
MAX_LIST_PROXIES_PER_COUNTRY = 100
USER_AGENT = "country-proxy-pac/6.0"

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
    response = requests.get(url, timeout=SOURCE_TIMEOUT, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.text


def extract_proxies(text: str) -> set[str]:
    return set(re.findall(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}(?!\d)", text))


def ip_is_valid(proxy: str) -> bool:
    try:
        host, port = proxy.rsplit(":", 1)
        ip = ipaddress.ip_address(host)
        return ip.version == 4 and ip.is_global and 1 <= int(port) <= 65535
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
            response = session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), headers={"User-Agent": USER_AGENT})
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
            response = session.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), headers={"User-Agent": USER_AGENT})
            if response.status_code < 500:
                return url
        except requests.RequestException:
            continue
    return None


def check_candidate(candidate: tuple[str, str]) -> dict:
    proxy_type, original_proxy = candidate
    started = time.perf_counter()
    session = requests.Session()
    proxy = proxy_url(proxy_type, original_proxy)
    session.proxies.update({"http": proxy, "https": proxy})

    try:
        external_ip, ip_endpoint = get_external_ip(session)
        if not external_ip:
            return {"status": "external_ip_failed"}

        https_endpoint = https_probe(session)
        if not https_endpoint:
            return {"status": "https_failed", "ip": external_ip}

        geo_response = requests.get(
            GEO_URL.format(ip=external_ip),
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            headers={"User-Agent": USER_AGENT},
        )
        geo_response.raise_for_status()
        geo = geo_response.json()
        if not geo.get("success"):
            return {"status": "geoip_failed", "ip": external_ip}

        elapsed = round((time.perf_counter() - started) * 1000)
        return {
            "status": "ok",
            "proxy": original_proxy,
            "type": proxy_type,
            "ip": external_ip,
            "country_code": geo.get("country_code"),
            "country": geo.get("country"),
            "city": geo.get("city"),
            "latency_ms": elapsed,
            "ip_check": ip_endpoint,
            "https_check": https_endpoint,
        }
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return {"status": "request_failed"}
    finally:
        session.close()


def make_http_pac(proxies: list[str], country_name: str) -> str:
    lines = [
        "// Auto-generated. Do not edit manually.",
        f"// Verified {country_name} HTTP/HTTPS proxies with HTTPS support.",
        "function FindProxyForURL(url, host) {",
    ]
    chain = "; ".join(f"PROXY {proxy}" for proxy in proxies)
    lines.append(f'    return "{chain + "; " if chain else ""}DIRECT";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def make_socks_pac(proxies: list[str], country_name: str) -> str:
    lines = [
        "// Auto-generated. Do not edit manually.",
        f"// SOCKS PAC for {country_name}: SOCKS4 and SOCKS5 endpoints.",
        "// PAC has no standard SOCKS4/SOCKS5 selector; SOCKS entries are intentionally combined.",
        "function FindProxyForURL(url, host) {",
    ]
    chain = "; ".join(f"SOCKS {proxy}" for proxy in proxies)
    lines.append(f'    return "{chain + "; " if chain else ""}DIRECT";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_proxy_lists(filename: str, items: list[dict]) -> None:
    for proxy_type in ("http", "https", "socks4", "socks5"):
        typed = [item["proxy"] for item in items if item["type"] == proxy_type][:MAX_LIST_PROXIES_PER_COUNTRY]
        (PROXIES / f"{filename}-{proxy_type}.txt").write_text(
            "\n".join(typed) + ("\n" if typed else ""),
            encoding="utf-8",
        )


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
    live_candidates = [candidate for candidate, alive in zip(candidates_list, tcp_results) if alive]
    print(f"TCP-live candidates: {len(live_candidates)}")

    diagnostics = {
        "http_tested": 0,
        "https_proxy_tested": 0,
        "socks4_tested": 0,
        "socks5_tested": 0,
        "external_ip_found": 0,
        "external_ip_failed": 0,
        "https_ok": 0,
        "https_failed": 0,
        "geoip_ok": 0,
        "geoip_failed": 0,
        "request_failed": 0,
    }
    protocol_counter_keys = {
        "http": "http_tested",
        "https": "https_proxy_tested",
        "socks4": "socks4_tested",
        "socks5": "socks5_tested",
    }
    for proxy_type, _ in live_candidates:
        diagnostics[protocol_counter_keys[proxy_type]] += 1

    working: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_candidate, candidate): candidate for candidate in live_candidates}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            status = result.get("status")
            if status == "external_ip_failed":
                diagnostics["external_ip_failed"] += 1
                continue
            if status == "https_failed":
                diagnostics["external_ip_found"] += 1
                diagnostics["https_failed"] += 1
                continue
            if status == "geoip_failed":
                diagnostics["external_ip_found"] += 1
                diagnostics["https_ok"] += 1
                diagnostics["geoip_failed"] += 1
                continue
            if status == "request_failed":
                diagnostics["request_failed"] += 1
                continue
            diagnostics["external_ip_found"] += 1
            diagnostics["https_ok"] += 1
            diagnostics["geoip_ok"] += 1
            working.append(result)

    by_country: dict[str, list[dict]] = {code: [] for code in TARGET_COUNTRIES}
    for item in working:
        code = item.get("country_code")
        if code in TARGET_COUNTRIES:
            by_country[code].append(item)

    country_stats: dict[str, dict] = {}
    for code, filename in TARGET_COUNTRIES.items():
        items = by_country[code]
        items.sort(key=lambda item: (item["latency_ms"], item["proxy"]))
        pac_items = [item for item in items if item["type"] in {"http", "https"}][:MAX_PAC_PROXIES_PER_COUNTRY]
        socks_items = [item for item in items if item["type"] in {"socks4", "socks5"}][:MAX_LIST_PROXIES_PER_COUNTRY]

        country_stats[code] = {
            "name": filename,
            "country": items[0].get("country") if items else None,
            "working": len(items),
            "http": sum(item["type"] == "http" for item in items),
            "https": sum(item["type"] == "https" for item in items),
            "socks4": sum(item["type"] == "socks4" for item in items),
            "socks5": sum(item["type"] == "socks5" for item in items),
            "pac_http_https": len(pac_items),
            "socks_pac": len(socks_items),
            "best_latency_ms": pac_items[0]["latency_ms"] if pac_items else None,
        }

        (DATA / f"{filename}.json").write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_proxy_lists(filename, items)

        country_display = filename.replace("-", " ").title()
        http_list = [item["proxy"] for item in pac_items]
        (PAC / f"{filename}.pac").write_text(make_http_pac(http_list, country_display), encoding="utf-8")
        (PAC / f"{filename}-http.pac").write_text(make_http_pac(http_list, country_display), encoding="utf-8")

        socks_list = [item["proxy"] for item in socks_items]
        (PAC / f"{filename}-socks.pac").write_text(make_socks_pac(socks_list, country_display), encoding="utf-8")

        print(f"COUNTRY {code} {filename}: working={len(items)}, http_https_pac={len(pac_items)}, socks={len(socks_items)}")

    updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    stats = {
        "updated_at": updated_at,
        "target_countries": TARGET_COUNTRIES,
        "sources": len(SOURCES),
        "candidates": len(candidates_list),
        "tcp_live_candidates": len(live_candidates),
        "working_target_country_proxies": sum(len(items) for items in by_country.values()),
        "max_workers": MAX_WORKERS,
        "max_pac_proxies_per_country": MAX_PAC_PROXIES_PER_COUNTRY,
        "max_list_proxies_per_country": MAX_LIST_PROXIES_PER_COUNTRY,
        "https_validation": True,
        "ip_check_endpoints": len(IP_CHECK_URLS),
        "https_test_endpoints": len(HTTPS_TEST_URLS),
        "geoip": "ipwho.is",
        "selection": "lowest HTTPS latency per country",
        "diagnostics": diagnostics,
        "countries": country_stats,
        "source_stats": source_stats,
        "publication": {
            "http_https_pac": True,
            "combined_socks_pac": True,
            "separate_protocol_lists": True,
        },
    }
    (DATA / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    working.sort(key=lambda item: (item["country_code"], item["latency_ms"], item["proxy"]))
    (DATA / "proxies.json").write_text(json.dumps([item for item in working if item.get("country_code") in TARGET_COUNTRIES], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("All country proxy lists and PAC files generated successfully.")


if __name__ == "__main__":
    main()
