# Формат подписки

Описание форматов подписок, поддерживаемых протоколов и HTTP-заголовков.

## Поддерживаемые протоколы

| Протокол | Схема | Описание |
|---|---|---|
| VLESS | `vless://` | Основной протокол |
| VMess | `vmess://` | JSON-based конфигурация в base64 |
| Trojan | `trojan://` | Парольная аутентификация |
| Shadowsocks | `ss://` | SIP002 и современный формат |
| Hysteria2 | `hysteria2://`, `hy2://` | Мульти-портовая поддержка |
| SOCKS5 | `socks://` | Проксирование через SOCKS5 |
| WireGuard | `wireguard://` | Туннелирование WireGuard |

> Схемы `ssr://`, `tuic://`, `hysteria://` распознаются приложением, но **не парсятся** — серверы с этими схемами будут пропущены.

## Форматы тела подписки

### 1. Base64-закодированные ссылки

Наиболее распространённый формат. Тело ответа — base64, при декодировании содержит ссылки по одной на строку:

```
base64(
  vless://uuid@server1:443?security=tls#Server1
  vless://uuid@server2:443?security=tls#Server2
)
```

Поддерживается URL-safe Base64 (`-` → `+`, `_` → `/`).

### 2. Открытые ссылки (plain text)

Ссылки в открытом виде, по одной на строку:

```
vless://uuid@server1:443?security=tls#Server1
vmess://eyJhZGQiOiJzZXJ2ZXIyIn0=
trojan://password@server3:443#Server3
socks://user:pass@server4:1080#Server4
wireguard://secretKey@server5:51820?publickey=KEY&address=10.0.0.2#Server5
```

### 3. JSON-форматы

**Массив полных xray-конфигов:**
```json
[
    { "outbounds": [...], "routing": {...} },
    { "outbounds": [...], "routing": {...} }
]
```

**Полный xray-конфиг** (одиночный объект с `inbounds` и `outbounds`):
```json
{
    "inbounds": [...],
    "outbounds": [...],
    "routing": {...},
    "dns": {...}
}
```

Подробнее: [full-xray-config.md](full-xray-config.md).

### 4. Смешанный формат

Ссылки серверов + строки маршрутизации + метаданные в одном теле:

```text
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://autorouting/onadd/https://example.com/routing.json
#announce: Плановое обслуживание завтра
```

**Поддерживаемые специальные строки в теле:**

| Паттерн | Описание |
|---|---|
| `://autorouting/onadd/{url}` | Автообновляемый профиль маршрутизации (URL, с `sourceURL`) |
| `://autorouting/add/{url}` | Автообновляемый профиль маршрутизации (URL, с `sourceURL`) |
| `://routing/onadd/{url}` | Одноразовый импорт профиля по URL (без автообновления) |
| `://routing/onadd/{base64}` | Статический профиль маршрутизации |
| `://routing/add/{base64}` | Статический профиль маршрутизации |
| `://onadd/{url или base64}` | Сокращённая форма (без автообновления) |
| `://routing/{base64}` | Сокращённая форма |
| `#announce: текст` | Объявление (поддерживает `base64:...`) |
| `#profile-title: текст` | Имя подписки (поддерживает `base64:...`) |
| `#support-url: URL` | Ссылка на поддержку |
| `#profile-web-page-url: URL` | Ссылка на сайт провайдера |
| `#announce-url: URL` | Ссылка на объявление |
| `#profile-update-interval: число` | Интервал обновления (часы) |

Специальные строки извлекаются из тела и не попадают в список серверов.

> **Приоритет:** значения из HTTP-заголовков имеют приоритет над значениями из тела. Inline-метаданные в теле используются как fallback, если соответствующий заголовок отсутствует.

---

## HTTP-заголовки

### Заголовки подписки

| Заголовок | Тип | Описание |
|---|---|---|
| `profile-title` | string | Имя подписки (до 25 символов). Поддерживает base64 |
| `subscription-name` | string | Альтернатива `profile-title` (fallback) |
| `profile-description` | string | Описание подписки. Поддерживает base64 |
| `profile-update-interval` | int | Интервал обновления в часах |
| `subscription-userinfo` | string | Статистика трафика и срок действия |
| `support-url` | URL | Ссылка на поддержку |
| `profile-web-page-url` | URL | Ссылка на сайт провайдера. Альтернатива: `homepage` |
| `announce-url` | URL | Ссылка на объявление |
| `announce` | string | Текст объявления (до 200 символов). Поддерживает base64 |
| `autorouting` | URL | URL-источник профиля маршрутизации с автообновлением |
| `routing` | string | Профиль маршрутизации (base64 или полная ссылка) |
| `sort-order` | string | Порядок сортировки серверов: `ping`, `name`, `none` |
| `content-disposition` | string | Fallback для имени подписки (расширения `.txt`, `.yaml` удаляются) |

### Profile Title

Поддерживает два формата:

**Открытый текст:**
```
profile-title: My VPN
```

**Base64 с описанием:**
```
profile-title: base64:TWVNdiBWUE4KV2VsY29tZSB0byBvdXIgc2VydmljZQ==
```

При base64-декодировании: первая строка — имя, остальные — описание.

### Subscription User Info

```
subscription-userinfo: upload=0;download=1073741824;total=10737418240;expire=1735689600
```

| Поле | Тип | Описание |
|---|---|---|
| `upload` | int | Исходящий трафик (байт) |
| `download` | int | Входящий трафик (байт) |
| `total` | int | Лимит трафика (байт) |
| `expire` | int | Дата истечения (Unix timestamp, секунды) |

> Если `expire` > 32000000000 — значение интерпретируется как миллисекунды и конвертируется в секунды.

**Скрытие блока трафика:**

Если сервер возвращает `subscription-userinfo: 0`, блок трафика на главном экране полностью скрывается. Используйте это, когда статистика трафика не предоставляется.

### Announce

Текст объявления отображается на главном экране в виде баннера. Поддерживается до **5 строк** текста, после чего текст обрезается с многоточием.

```
announce: Обновление серверов 15 марта
```

```
announce: base64:0J7QsdC90L7QstC70LXQvdC40LUg0YHQtdGA0LLQtdGA0L7Qsg==
```

### Sort Order

Задаёт порядок сортировки серверов в приложении. При обновлении подписки значение применяется к глобальной настройке сортировки.

```
sort-order: ping
```

| Значение | Описание |
|---|---|
| `none` | Порядок по умолчанию (как в подписке) |
| `ping` | По пингу (самые быстрые первыми) |
| `name` | По алфавиту |

---

## Заголовки запроса (клиент → сервер)

При обновлении подписки приложение отправляет:

| Заголовок | Описание |
|---|---|
| `User-Agent` | `INCY/<version>/<platform>` |
| `Accept` | `*/*` |
| `Accept-Language` | Language-tag устройства (напр. `ru-RU`) |
| `Accept-Encoding` | Только iOS: `gzip, deflate, br` |
| `x-app-version` | Версия приложения |
| `x-device-locale` | Язык устройства |
| `x-client` | `INCY` |

При включённой отправке HWID дополнительно:

| Заголовок | Описание |
|---|---|
| `x-hwid` | Аппаратный идентификатор ([подробнее](hwid.md)) |
| `X-Device-ID` | Alias для `x-hwid` на Android (некоторые сервер-стеки ожидают именно этот заголовок) |
| `x-device-os` | Платформа (`iOS`, `Android`, `Linux`, `Windows`) |
| `x-ver-os` | Версия ОС |
| `x-device-model` | Модель устройства |

> Все заголовки HTTP регистронезависимы. Сервер может смотреть на `x-hwid` либо `X-HWID` — придут одни и те же байты.
