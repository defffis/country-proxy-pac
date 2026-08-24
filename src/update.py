from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

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
]

TIMEOUT = 6
MAX_CANDIDATES = 250
MAX_PAC_PROXIES = 40


def get_text(url: str) -> str:
    r = requests.get(url, timeout=20, headers={"User-Agent": "turkey-proxy-pac/1.0"})
    r.raise_for_status()
    return r.text


def extract_proxies(text: str) -> set[str]:
    return set(re.findall(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}(?!\d)", text))


def ip_is_valid(proxy: str) -> bool:
    host, port = proxy.rsplit(":", 1)
    octets = host.split(".")
    return len(octets) == 4 and all(0 <= int(x) <= 255 for x in octets) and 1 <= int(port) <= 65535


def check_proxy(proxy: str) -> dict | None:
    host, port = proxy.rsplit(":", 1)
    proxies = {"http": f"http://{host}:{port}", "https": f"http://{host}:{port}"}
    started = time.perf_counter()
    try:
        r = requests.get("http://ip-api.com/json/?fields=status,countryCode,query", proxies=proxies, timeout=TIMEOUT)
        elapsed = round((time.perf_counter() - started) * 1000)
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("status") != "success" or data.get("countryCode") != "TR":
            return None
        return {"proxy": proxy, "ip": data.get("query"), "country": "TR", "latency_ms": elapsed}
    except Exception:
        return None


def make_pac(proxies: list[str]) -> str:
    lines = [
        "// Auto-generated. Do not edit manually.",
        "// Turkey HTTP proxy pool.",
        "function FindProxyForURL(url, host) {",
    ]
    for proxy in proxies:
        lines.append(f'    // {proxy}')
    if proxies:
        chain = "; ".join(f"PROXY {p}" for p in proxies)
        lines.append(f'    return "{chain}; DIRECT";')
    else:
        lines.append('    return "DIRECT";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    candidates: set[str] = set()
    for source in SOURCES:
        try:
            candidates |= extract_proxies(get_text(source))
        except Exception as exc:
            print(f"source failed: {source}: {exc}")

    candidates = {p for p in candidates if ip_is_valid(p)}
    candidates = set(sorted(candidates)[:MAX_CANDIDATES])
    print(f"Candidates: {len(candidates)}")

    working = []
    for i, proxy in enumerate(candidates, 1):
        result = check_proxy(proxy)
        if result:
            working.append(result)
            print(f"[{i}/{len(candidates)}] OK {proxy} {result['latency_ms']} ms")
        else:
            print(f"[{i}/{len(candidates)}] FAIL {proxy}")

    working.sort(key=lambda x: x["latency_ms"])
    working = working[:MAX_PAC_PROXIES]

    (DATA / "proxies.json").write_text(json.dumps(working, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA / "stats.json").write_text(json.dumps({
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": len(SOURCES),
        "candidates": len(candidates),
        "working_turkey_proxies": len(working),
    }, indent=2) + "\n", encoding="utf-8")
    (PAC / "turkey.pac").write_text(make_pac([x["proxy"] for x in working]), encoding="utf-8")
    (PAC / "turkey-http.pac").write_text(make_pac([x["proxy"] for x in working]), encoding="utf-8")


if __name__ == "__main__":
    main()
