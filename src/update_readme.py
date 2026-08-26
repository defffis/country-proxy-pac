from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
STATS = ROOT / "data" / "stats.json"

START = "<!-- AUTO-STATS:START -->"
END = "<!-- AUTO-STATS:END -->"

COUNTRY_FLAGS = {
    "TR": "🇹🇷",
    "IN": "🇮🇳",
    "PL": "🇵🇱",
    "NL": "🇳🇱",
    "DE": "🇩🇪",
    "US": "🇺🇸",
    "GB": "🇬🇧",
}

COUNTRY_NAMES_RU = {
    "TR": "Турция",
    "IN": "Индия",
    "PL": "Польша",
    "NL": "Нидерланды",
    "DE": "Германия",
    "US": "США",
    "GB": "Великобритания",
}

COUNTRY_NAMES_EN = {
    "TR": "Turkey",
    "IN": "India",
    "PL": "Poland",
    "NL": "Netherlands",
    "DE": "Germany",
    "US": "United States",
    "GB": "United Kingdom",
}


def fmt(value: int | float | None) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return f"{value:,}".replace(",", " ")


def build_stats_block(stats: dict) -> str:
    countries = stats.get("countries", {})
    diagnostics = stats.get("diagnostics", {})
    source_stats = stats.get("source_stats", {})

    total_working = sum(int(v.get("working", 0)) for v in countries.values())
    total_http_https = sum(int(v.get("pac_http_https", 0)) for v in countries.values())
    total_socks = sum(int(v.get("socks_pac", 0)) for v in countries.values())
    total_found = sum(int(v.get("found", 0)) for v in source_stats.values())
    total_valid = sum(int(v.get("valid", 0)) for v in source_stats.values())

    lines = [
        START,
        "## Текущая статистика",
        "",
        f"> Последнее обновление: **{stats.get('updated_at', '—')}**",
        "",
        "### Общая статистика сбора",
        "",
        "| Показатель | Значение |",
        "|---|---:|",
        f"| Источников | {fmt(stats.get('sources'))} |",
        f"| Найдено proxy в источниках | {fmt(total_found)} |",
        f"| Валидных `IP:PORT` | {fmt(total_valid)} |",
        f"| Кандидатов обработано | {fmt(stats.get('candidates'))} |",
        f"| TCP-live кандидатов | {fmt(stats.get('tcp_live_candidates'))} |",
        f"| HTTP проверено | {fmt(diagnostics.get('http_tested'))} |",
        f"| HTTPS proxy проверено | {fmt(diagnostics.get('https_proxy_tested'))} |",
        f"| SOCKS4 проверено | {fmt(diagnostics.get('socks4_tested'))} |",
        f"| SOCKS5 проверено | {fmt(diagnostics.get('socks5_tested'))} |",
        f"| Найден внешний IP | {fmt(diagnostics.get('external_ip_found'))} |",
        f"| Успешный HTTPS probe | {fmt(diagnostics.get('https_ok'))} |",
        f"| Успешный GeoIP | {fmt(diagnostics.get('geoip_ok'))} |",
        f"| Рабочих proxy по целевым странам | {fmt(total_working)} |",
        f"| HTTP/HTTPS endpoints для PAC | {fmt(total_http_https)} |",
        f"| SOCKS endpoints для PAC | {fmt(total_socks)} |",
        f"| Максимум кандидатов | {fmt(stats.get('max_candidates', stats.get('candidates')))} |",
        f"| Параллельных workers | {fmt(stats.get('max_workers'))} |",
        "",
        "### Статистика PAC по странам",
        "",
        "| Страна | Working | HTTP | HTTPS | SOCKS4 | SOCKS5 | PAC HTTP/HTTPS | PAC SOCKS | Best latency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for code in COUNTRY_NAMES_RU:
        c = countries.get(code, {})
        latency = c.get("best_latency_ms")
        latency_text = f"{fmt(latency)} ms" if latency is not None else "—"
        lines.append(
            f"| {COUNTRY_FLAGS[code]} {COUNTRY_NAMES_RU[code]} (`{code}`) "
            f"| {fmt(c.get('working', 0))} | {fmt(c.get('http', 0))} "
            f"| {fmt(c.get('https', 0))} | {fmt(c.get('socks4', 0))} "
            f"| {fmt(c.get('socks5', 0))} | {fmt(c.get('pac_http_https', 0))} "
            f"| {fmt(c.get('socks_pac', 0))} | {latency_text} |"
        )

    lines += [
        "",
        "### PAC files",
        "",
        "| PAC | Рабочих endpoints | Ссылка |",
        "|---|---:|---|",
    ]

    for code, name in stats.get("target_countries", {}).items():
        c = countries.get(code, {})
        lines.append(
            f"| `{name}.pac` | {fmt(c.get('pac_http_https', 0))} | "
            f"[`{name}.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/{name}.pac) |"
        )
        lines.append(
            f"| `{name}-socks.pac` | {fmt(c.get('socks_pac', 0))} | "
            f"[`{name}-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/{name}-socks.pac) |"
        )

    lines += [
        "",
        "### Источники",
        "",
        "| Источник | Найдено | Валидных |",
        "|---|---:|---:|",
    ]
    for key, value in source_stats.items():
        source_type, _, url = key.partition(":")
        short = url.replace("https://raw.githubusercontent.com/", "")
        lines.append(f"| `{source_type}` `{short}` | {fmt(value.get('found', 0))} | {fmt(value.get('valid', 0))} |")

    lines += [
        "",
        "<details>",
        "<summary>English statistics</summary>",
        "",
        f"> Last update: **{stats.get('updated_at', '—')}**",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Sources | {fmt(stats.get('sources'))} |",
        f"| Proxies found in sources | {fmt(total_found)} |",
        f"| Valid `IP:PORT` | {fmt(total_valid)} |",
        f"| Candidates processed | {fmt(stats.get('candidates'))} |",
        f"| TCP-live candidates | {fmt(stats.get('tcp_live_candidates'))} |",
        f"| Working target-country proxies | {fmt(total_working)} |",
        f"| HTTP/HTTPS PAC endpoints | {fmt(total_http_https)} |",
        f"| SOCKS PAC endpoints | {fmt(total_socks)} |",
        "",
        "| Country | Working | HTTP | HTTPS | SOCKS4 | SOCKS5 | PAC HTTP/HTTPS | PAC SOCKS | Best latency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for code in COUNTRY_NAMES_EN:
        c = countries.get(code, {})
        latency = c.get("best_latency_ms")
        latency_text = f"{fmt(latency)} ms" if latency is not None else "—"
        lines.append(
            f"| {COUNTRY_FLAGS[code]} {COUNTRY_NAMES_EN[code]} (`{code}`) "
            f"| {fmt(c.get('working', 0))} | {fmt(c.get('http', 0))} "
            f"| {fmt(c.get('https', 0))} | {fmt(c.get('socks4', 0))} "
            f"| {fmt(c.get('socks5', 0))} | {fmt(c.get('pac_http_https', 0))} "
            f"| {fmt(c.get('socks_pac', 0))} | {latency_text} |"
        )

    lines += ["", "</details>", END]
    return "\n".join(lines)


def main() -> None:
    stats = json.loads(STATS.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")
    block = build_stats_block(stats)

    if START in readme and END in readme:
        prefix = readme.split(START, 1)[0]
        suffix = readme.split(END, 1)[1]
        readme = prefix + block + suffix
    else:
        marker = "## Поддерживаемые страны"
        if marker not in readme:
            raise RuntimeError(f"README marker not found: {marker}")
        readme = readme.replace(marker, block + "\n\n" + marker, 1)

    README.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
