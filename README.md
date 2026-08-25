# Country Proxy PAC

[Русская версия](#русская-версия) · [English version](#english-version)

Автоматически обновляемые PAC-файлы с публичными HTTP/HTTPS-прокси, сгруппированными по стране выхода.

> **Важно:** проект использует публичные proxy-источники. Доступность, скорость и стабильность прокси не гарантируются.

## Поддерживаемые страны

| Страна | Код | PAC |
|---|---|---|
| 🇹🇷 Турция | `TR` | `pac/turkey.pac` |
| 🇮🇳 Индия | `IN` | `pac/india.pac` |
| 🇵🇱 Польша | `PL` | `pac/poland.pac` |
| 🇳🇱 Нидерланды | `NL` | `pac/netherlands.pac` |
| 🇩🇪 Германия | `DE` | `pac/germany.pac` |
| 🇺🇸 США | `US` | `pac/usa.pac` |
| 🇬🇧 Великобритания | `GB` | `pac/uk.pac` |

Для каждой страны также создаётся вариант `*-http.pac`.

## Готовые PAC URL

PAC-файлы можно подключать напрямую через `raw.githubusercontent.com`:

| Страна | PAC | HTTP PAC |
|---|---|---|
| Турция | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey-http.pac` |
| Индия | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india-http.pac` |
| Польша | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland-http.pac` |
| Нидерланды | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands-http.pac` |
| Германия | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany-http.pac` |
| США | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa-http.pac` |
| Великобритания | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk-http.pac` |

> URL выше указывают непосредственно на файлы в GitHub и не требуют GitHub Pages.

## Как это работает

1. GitHub Actions запускает обновление автоматически каждые 30 минут или вручную.
2. Скрипт загружает прокси из нескольких публичных источников.
3. Прокси нормализуются и удаляются дубликаты.
4. Проверяется корректность IPv4 и порта.
5. Выполняется быстрый TCP pre-check.
6. Рабочие кандидаты проверяются через HTTP/HTTPS/SOCKS4/SOCKS5.
7. Определяется внешний IP через HTTPS endpoints.
8. Внешний IP проверяется через GeoIP.
9. Прокси распределяются по странам выхода.
10. Для HTTP/HTTPS-прокси формируются PAC-файлы.
11. Результаты и статистика сохраняются в `data/`.
12. GitHub Actions автоматически коммитит изменения.

## Почему проверяется exit IP

Страна самого proxy-сервера не обязательно совпадает со страной фактического выхода в интернет. Поэтому проект определяет внешний IP через прокси и только после этого выполняет GeoIP-проверку.

Условно:

```text
Proxy IP:PORT
      ↓
  HTTPS request
      ↓
  External IP
      ↓
     GeoIP
      ↓
 Country code
      ↓
 ┌────┬────┬────┬────┬────┬────┬────┐
 │ TR │ IN │ PL │ NL │ DE │ US │ GB │
 └────┴────┴────┴────┴────┴────┴────┘
```

## Структура проекта

```text
.
├── .github/
│   └── workflows/
│       └── update.yml
├── data/
│   ├── proxies.json
│   └── stats.json
├── pac/
│   ├── turkey.pac
│   ├── turkey-http.pac
│   ├── india.pac
│   ├── india-http.pac
│   ├── poland.pac
│   ├── poland-http.pac
│   ├── netherlands.pac
│   ├── netherlands-http.pac
│   ├── germany.pac
│   ├── germany-http.pac
│   ├── usa.pac
│   ├── usa-http.pac
│   ├── uk.pac
│   └── uk-http.pac
├── src/
│   └── update.py
├── index.html
├── requirements.txt
└── README.md
```

## Формат `proxies.json`

Каждый найденный прокси содержит примерно такие данные:

```json
{
  "proxy": "1.2.3.4:8080",
  "type": "http",
  "ip": "1.2.3.4",
  "country": "TR",
  "city": "Istanbul",
  "latency_ms": 850
}
```

`data/proxies.json` содержит рабочие прокси, найденные в текущем запуске. `data/stats.json` содержит статистику проверки и сведения по странам.

## PAC

PAC-файлы используют стандартный формат JavaScript:

```javascript
function FindProxyForURL(url, host) {
    return "PROXY 1.2.3.4:8080; PROXY 5.6.7.8:3128; DIRECT";
}
```

В PAC включаются только HTTP/HTTPS-прокси, поскольку SOCKS4/SOCKS5 требуют другой схемы использования.

Прокси перечисляются по возрастанию измеренной HTTPS latency. После списка прокси добавляется `DIRECT` как fallback.

## Автоматическое обновление

Workflow находится в:

```text
.github/workflows/update.yml
```

Расписание:

```text
17 и 47 минута каждого часа
```

Также запуск можно выполнить вручную через **GitHub Actions → Update Country Proxy PACs → Run workflow**.

## Локальный запуск

Требуется Python 3.12+.

```bash
pip install -r requirements.txt
python src/update.py
```

Результаты будут записаны в:

```text
data/
pac/
```

## Ограничения

- Источники прокси являются публичными и могут изменяться или становиться недоступными.
- Публичные прокси часто нестабильны и могут иметь высокую задержку.
- Наличие прокси в списке не означает его безопасность или анонимность.
- GeoIP-базы могут ошибаться или обновляться с задержкой.
- Количество рабочих прокси для разных стран может существенно различаться.
- SOCKS-прокси проверяются для анализа, но не добавляются в стандартный HTTP PAC.

## Использование

Проект предназначен для тестирования сетевого доступа, разработки, автоматизации и других законных задач, где требуется выбрать прокси по стране выхода.

---

# English version

Automatically updated PAC files containing public HTTP/HTTPS proxies grouped by their exit country.

> **Important:** this project uses public proxy sources. Proxy availability, speed, stability, security, and anonymity are not guaranteed.

## Supported countries

| Country | Code | PAC |
|---|---|---|
| 🇹🇷 Turkey | `TR` | `pac/turkey.pac` |
| 🇮🇳 India | `IN` | `pac/india.pac` |
| 🇵🇱 Poland | `PL` | `pac/poland.pac` |
| 🇳🇱 Netherlands | `NL` | `pac/netherlands.pac` |
| 🇩🇪 Germany | `DE` | `pac/germany.pac` |
| 🇺🇸 United States | `US` | `pac/usa.pac` |
| 🇬🇧 United Kingdom | `GB` | `pac/uk.pac` |

A `*-http.pac` variant is also generated for each country.

## Ready-to-use PAC URLs

PAC files can be loaded directly from `raw.githubusercontent.com`:

| Country | PAC | HTTP PAC |
|---|---|---|
| Turkey | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey-http.pac` |
| India | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india-http.pac` |
| Poland | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland-http.pac` |
| Netherlands | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands-http.pac` |
| Germany | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany-http.pac` |
| United States | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa-http.pac` |
| United Kingdom | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk.pac` | `https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk-http.pac` |

> These URLs point directly to files in GitHub and do not require GitHub Pages.

## How it works

1. GitHub Actions runs the update automatically every 30 minutes or manually.
2. The updater downloads proxies from multiple public sources.
3. Proxies are normalized and deduplicated.
4. IPv4 addresses and ports are validated.
5. A fast TCP pre-check removes unreachable candidates.
6. Remaining candidates are tested using HTTP/HTTPS/SOCKS4/SOCKS5.
7. The external IP is determined through HTTPS endpoints.
8. The external IP is checked using GeoIP.
9. Working proxies are grouped by exit country.
10. PAC files are generated for HTTP/HTTPS proxies.
11. Results and statistics are saved under `data/`.
12. GitHub Actions commits updated data automatically.

## Why the exit IP is checked

The country of the proxy server itself does not necessarily match the country of its actual internet exit. The project therefore determines the external IP through the proxy and performs GeoIP detection on that IP.

Conceptually:

```text
Proxy IP:PORT
      ↓
  HTTPS request
      ↓
  External IP
      ↓
     GeoIP
      ↓
 Country code
      ↓
 ┌────┬────┬────┬────┬────┬────┬────┐
 │ TR │ IN │ PL │ NL │ DE │ US │ GB │
 └────┴────┴────┴────┴────┴────┴────┘
```

## Project structure

```text
.
├── .github/
│   └── workflows/
│       └── update.yml
├── data/
│   ├── proxies.json
│   └── stats.json
├── pac/
│   ├── turkey.pac
│   ├── turkey-http.pac
│   ├── india.pac
│   ├── india-http.pac
│   ├── poland.pac
│   ├── poland-http.pac
│   ├── netherlands.pac
│   ├── netherlands-http.pac
│   ├── germany.pac
│   ├── germany-http.pac
│   ├── usa.pac
│   ├── usa-http.pac
│   ├── uk.pac
│   └── uk-http.pac
├── src/
│   └── update.py
├── index.html
├── requirements.txt
└── README.md
```

## `proxies.json` format

Each detected proxy contains information similar to:

```json
{
  "proxy": "1.2.3.4:8080",
  "type": "http",
  "ip": "1.2.3.4",
  "country": "TR",
  "city": "Istanbul",
  "latency_ms": 850
}
```

`data/proxies.json` contains proxies that passed the current run. `data/stats.json` contains validation statistics and country-level results.

## PAC files

PAC files use the standard JavaScript format:

```javascript
function FindProxyForURL(url, host) {
    return "PROXY 1.2.3.4:8080; PROXY 5.6.7.8:3128; DIRECT";
}
```

Only HTTP/HTTPS proxies are included in PAC files because SOCKS4/SOCKS5 use a different proxy scheme.

Proxies are ordered by measured HTTPS latency. `DIRECT` is added as a fallback after the proxy list.

## Automatic updates

The workflow is located at:

```text
.github/workflows/update.yml
```

Schedule:

```text
17 and 47 minutes of every hour
```

It can also be started manually through **GitHub Actions → Update Country Proxy PACs → Run workflow**.

## Local usage

Python 3.12+ is required.

```bash
pip install -r requirements.txt
python src/update.py
```

Generated files are written to:

```text
data/
pac/
```

## Limitations

- Public proxy sources may change or become unavailable.
- Public proxies are often unstable and may have high latency.
- Being listed does not imply that a proxy is secure or anonymous.
- GeoIP databases can contain errors or become outdated.
- The number of working proxies varies significantly by country.
- SOCKS proxies are tested for analysis but are not included in standard HTTP PAC files.

## Usage

This project is intended for network testing, development, automation, and other legitimate use cases where selecting proxies by exit country is required.
