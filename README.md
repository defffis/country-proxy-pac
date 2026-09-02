# Country Proxy PAC

[Русская версия](#русская-версия) · [English version](#english-version)

Автоматически обновляемые списки и PAC-файлы публичных прокси, сгруппированных по стране фактического выхода в интернет.

> **Важно:** проект использует публичные proxy-источники. Доступность, скорость, безопасность и стабильность прокси не гарантируются.

<!-- AUTO-STATS:START -->
## Текущая статистика

> Последнее обновление: **2026-09-02T19:04:19Z**

### Общая статистика сбора

| Показатель | Значение |
|---|---:|
| Источников | 20 |
| Кандидатов обработано | 12 336 |
| TCP-live кандидатов | 5 646 |
| HTTP проверено | 2 012 |
| HTTPS proxy проверено | 1 258 |
| SOCKS4 проверено | 1 244 |
| SOCKS5 проверено | 1 132 |
| Найден внешний IP | 493 |
| Успешный HTTPS probe | 351 |
| Успешный GeoIP | 351 |
| Рабочих proxy по целевым странам | 101 |
| HTTP/HTTPS endpoints для PAC | 44 |
| SOCKS endpoints для PAC | 57 |
| Максимум кандидатов | 12 336 |
| Параллельных workers | 100 |

### Статистика PAC по странам

| Страна | Working | HTTP | HTTPS | SOCKS4 | SOCKS5 | PAC HTTP/HTTPS | PAC SOCKS | Best latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 🇹🇷 Турция (`TR`) | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 2 600 ms |
| 🇮🇳 Индия (`IN`) | 12 | 6 | 0 | 5 | 1 | 6 | 6 | 2 571 ms |
| 🇵🇱 Польша (`PL`) | 1 | 0 | 0 | 1 | 0 | 0 | 1 | — |
| 🇳🇱 Нидерланды (`NL`) | 26 | 7 | 0 | 3 | 16 | 7 | 19 | 1 985 ms |
| 🇩🇪 Германия (`DE`) | 13 | 6 | 0 | 2 | 5 | 6 | 7 | 1 852 ms |
| 🇺🇸 США (`US`) | 43 | 21 | 0 | 9 | 13 | 21 | 22 | 319 ms |
| 🇬🇧 Великобритания (`GB`) | 5 | 3 | 0 | 0 | 2 | 3 | 2 | 1 758 ms |

### PAC files

| PAC | Рабочих endpoints | Ссылка |
|---|---:|---|
| `turkey.pac` | 1 | [`turkey.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey.pac) |
| `turkey-socks.pac` | 0 | [`turkey-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey-socks.pac) |
| `india.pac` | 6 | [`india.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india.pac) |
| `india-socks.pac` | 6 | [`india-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india-socks.pac) |
| `poland.pac` | 0 | [`poland.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland.pac) |
| `poland-socks.pac` | 1 | [`poland-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland-socks.pac) |
| `netherlands.pac` | 7 | [`netherlands.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands.pac) |
| `netherlands-socks.pac` | 19 | [`netherlands-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands-socks.pac) |
| `germany.pac` | 6 | [`germany.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany.pac) |
| `germany-socks.pac` | 7 | [`germany-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany-socks.pac) |
| `usa.pac` | 21 | [`usa.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa.pac) |
| `usa-socks.pac` | 22 | [`usa-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa-socks.pac) |
| `uk.pac` | 3 | [`uk.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk.pac) |
| `uk-socks.pac` | 2 | [`uk-socks.pac`](https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk-socks.pac) |

<details>
<summary>English statistics</summary>

> Last update: **2026-09-02T19:04:19Z**

| Metric | Value |
|---|---:|
| Sources | 20 |
| Candidates processed | 12 336 |
| TCP-live candidates | 5 646 |
| Working target-country proxies | 101 |
| HTTP/HTTPS PAC endpoints | 44 |
| SOCKS PAC endpoints | 57 |

| Country | Working | HTTP | HTTPS | SOCKS4 | SOCKS5 | PAC HTTP/HTTPS | PAC SOCKS | Best latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 🇹🇷 Turkey (`TR`) | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 2 600 ms |
| 🇮🇳 India (`IN`) | 12 | 6 | 0 | 5 | 1 | 6 | 6 | 2 571 ms |
| 🇵🇱 Poland (`PL`) | 1 | 0 | 0 | 1 | 0 | 0 | 1 | — |
| 🇳🇱 Netherlands (`NL`) | 26 | 7 | 0 | 3 | 16 | 7 | 19 | 1 985 ms |
| 🇩🇪 Germany (`DE`) | 13 | 6 | 0 | 2 | 5 | 6 | 7 | 1 852 ms |
| 🇺🇸 United States (`US`) | 43 | 21 | 0 | 9 | 13 | 21 | 22 | 319 ms |
| 🇬🇧 United Kingdom (`GB`) | 5 | 3 | 0 | 0 | 2 | 3 | 2 | 1 758 ms |

</details>
<!-- AUTO-STATS:END -->

## Поддерживаемые страны

| Страна | Код | HTTP/HTTPS PAC | SOCKS PAC |
|---|---|---|---|
| 🇹🇷 Турция | `TR` | `pac/turkey.pac` | `pac/turkey-socks.pac` |
| 🇮🇳 Индия | `IN` | `pac/india.pac` | `pac/india-socks.pac` |
| 🇵🇱 Польша | `PL` | `pac/poland.pac` | `pac/poland-socks.pac` |
| 🇳🇱 Нидерланды | `NL` | `pac/netherlands.pac` | `pac/netherlands-socks.pac` |
| 🇩🇪 Германия | `DE` | `pac/germany.pac` | `pac/germany-socks.pac` |
| 🇺🇸 США | `US` | `pac/usa.pac` | `pac/usa-socks.pac` |
| 🇬🇧 Великобритания | `GB` | `pac/uk.pac` | `pac/uk-socks.pac` |

## Готовые ссылки

Все файлы доступны напрямую через `raw.githubusercontent.com` и не требуют GitHub Pages.

### HTTP/HTTPS PAC

```text
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk.pac
```

### Комбинированный SOCKS PAC

```text
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk-socks.pac
```

### Отдельные списки протоколов

Для каждой страны публикуются четыре обычных текстовых списка:

```text
proxies/<country>-http.txt
proxies/<country>-https.txt
proxies/<country>-socks4.txt
proxies/<country>-socks5.txt
```

Например:

```text
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-http.txt
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-https.txt
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-socks4.txt
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-socks5.txt
```

## Важный нюанс SOCKS4/SOCKS5 в PAC

Стандартный PAC использует директиву:

```javascript
SOCKS 1.2.3.4:1080
```

В стандартном формате PAC **нет отдельной директивы `SOCKS4` и `SOCKS5`**. Поэтому проект создаёт единый `*-socks.pac`, в который входят проверенные SOCKS4 и SOCKS5 endpoints.

Точный протокол сохраняется в отдельных файлах `*-socks4.txt` и `*-socks5.txt`.

Если конкретный клиент PAC интерпретирует `SOCKS` только как SOCKS5 или вообще не поддерживает SOCKS PAC, следует использовать соответствующий `.txt` список или нативную конфигурацию клиента.

## Как это работает

```text
Public proxy sources
        ↓
  Normalize + deduplicate
        ↓
      IPv4:PORT
        ↓
     TCP pre-check
        ↓
 HTTP / HTTPS / SOCKS4 / SOCKS5
        ↓
    External IP check
        ↓
       GeoIP
        ↓
  Actual exit country
        ↓
 ┌────┬────┬────┬────┬────┬────┬────┐
 │ TR │ IN │ PL │ NL │ DE │ US │ GB │
 └────┴────┴────┴────┴────┴────┴────┘
        ↓
   Country datasets
        ↓
 PAC + protocol-specific lists
```

Страна определяется по **внешнему IP, полученному через прокси**, а не по IP самого proxy-сервера.

## Форматы публикации

Для каждой страны создаются:

```text
pac/<country>.pac          # HTTP/HTTPS PAC
pac/<country>-http.pac     # HTTP/HTTPS PAC, explicit name
pac/<country>-socks.pac    # combined SOCKS4 + SOCKS5 PAC

proxies/<country>-http.txt
proxies/<country>-https.txt
proxies/<country>-socks4.txt
proxies/<country>-socks5.txt
```

Также в `data/<country>.json` сохраняются расширенные сведения о проверенных прокси, включая тип, exit IP, страну, город и latency.

## Проверка прокси

Кандидат проходит несколько этапов:

1. Проверка формата IPv4:PORT.
2. TCP pre-check.
3. Подключение через заявленный протокол.
4. Определение внешнего IP через несколько HTTPS endpoints.
5. Реальный HTTPS probe.
6. GeoIP-проверка внешнего IP.
7. Отбор только целевых стран.
8. Сортировка по измеренной latency.

Для HTTP/HTTPS PAC выбираются лучшие HTTP/HTTPS endpoints. SOCKS4 и SOCKS5 публикуются отдельно и дополнительно объединяются в SOCKS PAC.

## Автоматическое обновление

GitHub Actions запускает сборщик каждые 30 минут и поддерживает ручной запуск через `workflow_dispatch`.

Workflow:

```text
.github/workflows/update.yml
```

Расписание:

```text
17 и 47 минута каждого часа
```

После успешного запуска изменения автоматически коммитятся в репозиторий.

## Структура проекта

```text
.
├── .github/workflows/update.yml
├── data/
│   ├── proxies.json
│   ├── stats.json
│   └── <country>.json
├── pac/
│   ├── <country>.pac
│   ├── <country>-http.pac
│   └── <country>-socks.pac
├── proxies/
│   ├── <country>-http.txt
│   ├── <country>-https.txt
│   ├── <country>-socks4.txt
│   └── <country>-socks5.txt
├── src/update.py
├── index.html
├── requirements.txt
└── README.md
```

## Локальный запуск

Требуется Python 3.12+:

```bash
pip install -r requirements.txt
python src/update.py
```

Результаты будут записаны в `data/`, `pac/` и `proxies/`.

## Ограничения

- Публичные proxy-листы нестабильны и постоянно меняются.
- Количество рабочих прокси сильно различается между странами.
- GeoIP может ошибаться или обновляться с задержкой.
- Наличие прокси в списке не означает безопасность или анонимность.
- SOCKS PAC использует стандартную директиву `SOCKS`, поэтому не гарантирует отдельное различение SOCKS4/SOCKS5 на стороне клиента.

## Использование

Проект предназначен для сетевого тестирования, разработки, автоматизации и других законных задач, где требуется выбирать прокси по стране выхода.

---

# English version

Automatically updated proxy lists and PAC files containing public proxies grouped by their actual internet exit country.

> **Important:** this project uses public proxy sources. Availability, speed, security, and stability are not guaranteed.

## Supported countries

| Country | Code | HTTP/HTTPS PAC | SOCKS PAC |
|---|---|---|---|
| 🇹🇷 Turkey | `TR` | `pac/turkey.pac` | `pac/turkey-socks.pac` |
| 🇮🇳 India | `IN` | `pac/india.pac` | `pac/india-socks.pac` |
| 🇵🇱 Poland | `PL` | `pac/poland.pac` | `pac/poland-socks.pac` |
| 🇳🇱 Netherlands | `NL` | `pac/netherlands.pac` | `pac/netherlands-socks.pac` |
| 🇩🇪 Germany | `DE` | `pac/germany.pac` | `pac/germany-socks.pac` |
| 🇺🇸 United States | `US` | `pac/usa.pac` | `pac/usa-socks.pac` |
| 🇬🇧 United Kingdom | `GB` | `pac/uk.pac` | `pac/uk-socks.pac` |

## Ready-to-use files

All files are available directly through `raw.githubusercontent.com`; GitHub Pages is not required.

### HTTP/HTTPS PAC

```text
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk.pac
```

### Combined SOCKS PAC

```text
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/turkey-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/india-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/poland-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/netherlands-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/germany-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/usa-socks.pac
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/pac/uk-socks.pac
```

### Separate protocol lists

Each country also publishes four plain-text lists:

```text
proxies/<country>-http.txt
proxies/<country>-https.txt
proxies/<country>-socks4.txt
proxies/<country>-socks5.txt
```

Example:

```text
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-http.txt
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-https.txt
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-socks4.txt
https://raw.githubusercontent.com/defffis/country-proxy-pac/main/proxies/turkey-socks5.txt
```

## SOCKS4/SOCKS5 in PAC

Standard PAC uses the directive:

```javascript
SOCKS 1.2.3.4:1080
```

There is **no separate standard `SOCKS4` or `SOCKS5` PAC directive**. Therefore the project generates one combined `*-socks.pac` containing verified SOCKS4 and SOCKS5 endpoints.

The exact protocol is preserved in the separate `*-socks4.txt` and `*-socks5.txt` files.

If a particular PAC client interprets `SOCKS` as SOCKS5 only, or does not support SOCKS PAC, use the corresponding text list or native client configuration instead.

## How it works

```text
Public proxy sources
        ↓
  Normalize + deduplicate
        ↓
      IPv4:PORT
        ↓
     TCP pre-check
        ↓
 HTTP / HTTPS / SOCKS4 / SOCKS5
        ↓
    External IP check
        ↓
       GeoIP
        ↓
  Actual exit country
        ↓
 ┌────┬────┬────┬────┬────┬────┬────┐
 │ TR │ IN │ PL │ NL │ DE │ US │ GB │
 └────┴────┴────┴────┴────┴────┴────┘
        ↓
   Country datasets
        ↓
 PAC + protocol-specific lists
```

The country is determined from the **external IP obtained through the proxy**, not from the proxy server's own IP.

## Published formats

For every country:

```text
pac/<country>.pac          # HTTP/HTTPS PAC
pac/<country>-http.pac     # HTTP/HTTPS PAC, explicit name
pac/<country>-socks.pac    # combined SOCKS4 + SOCKS5 PAC

proxies/<country>-http.txt
proxies/<country>-https.txt
proxies/<country>-socks4.txt
proxies/<country>-socks5.txt
```

Extended information is also stored in `data/<country>.json`, including proxy type, exit IP, country, city, and latency.

## Proxy validation

Candidates pass several stages:

1. IPv4:PORT format validation.
2. TCP pre-check.
3. Connection through the declared protocol.
4. External IP detection through multiple HTTPS endpoints.
5. Real HTTPS probe.
6. GeoIP lookup of the external IP.
7. Filtering to target countries.
8. Sorting by measured latency.

HTTP/HTTPS PAC files use the best HTTP/HTTPS endpoints. SOCKS4 and SOCKS5 are published separately and also combined into a SOCKS PAC.

## Automatic updates

GitHub Actions runs the updater every 30 minutes and also supports manual `workflow_dispatch` runs.

Workflow:

```text
.github/workflows/update.yml
```

Schedule:

```text
17 and 47 minutes of every hour
```

Successful runs automatically commit updated data to the repository.

## Project structure

```text
.
├── .github/workflows/update.yml
├── data/
│   ├── proxies.json
│   ├── stats.json
│   └── <country>.json
├── pac/
│   ├── <country>.pac
│   ├── <country>-http.pac
│   └── <country>-socks.pac
├── proxies/
│   ├── <country>-http.txt
│   ├── <country>-https.txt
│   ├── <country>-socks4.txt
│   └── <country>-socks5.txt
├── src/update.py
├── index.html
├── requirements.txt
└── README.md
```

## Local usage

Python 3.12+ is required:

```bash
pip install -r requirements.txt
python src/update.py
```

Generated files are written to `data/`, `pac/`, and `proxies/`.

## Limitations

- Public proxy lists are unstable and constantly changing.
- The number of working proxies varies significantly by country.
- GeoIP databases may contain errors or become outdated.
- Being listed does not imply security or anonymity.
- SOCKS PAC uses the standard `SOCKS` directive, so separate SOCKS4/SOCKS5 semantics are not guaranteed by every client.

## Usage

This project is intended for network testing, development, automation, and other legitimate use cases where proxies need to be selected by exit country.
