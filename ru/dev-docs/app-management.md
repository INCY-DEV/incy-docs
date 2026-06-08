# Управление приложением

Параметры для управления поведением приложения через HTTP-заголовки подписки и строки в теле ответа.

## Способы передачи

Все параметры можно передавать двумя способами:

**1. HTTP-заголовок:**
```
HTTP/2 200
profile-title: Мой VPN
support-url: https://t.me/support
```

**2. Строка в теле подписки (комментарий с `#`):**
```
#profile-title: Мой VPN
#support-url: https://t.me/support
#profile-update-interval: 6
#announce: Текст объявления
vless://...
```

> **Приоритет:** HTTP-заголовки имеют приоритет. Строки в теле подписки используются как fallback, когда соответствующий заголовок отсутствует. Это особенно полезно при раздаче подписок через статические файлы (nginx), где нет возможности задать кастомные HTTP-заголовки.

---

## Стандартные параметры

### Имя подписки

Название профиля подписки. Максимум 25 символов. Можно передавать как текст или base64 (UTF-8).

**Заголовок:**
```
profile-title: Мой VPN
```

**В теле подписки:**
```
#profile-title: Мой VPN
```

**Base64 с описанием** (первая строка — имя, остальные — описание):
```
profile-title: base64:0JzQvtC5IFZQTgrQlNC+0LHRgNC+INC/0L7QttCw0LvQvtCy0LDRgtGM
```

**Альтернативные заголовки** (fallback, если `profile-title` отсутствует):
- `subscription-name` — альтернативное имя подписки
- `content-disposition` — имя файла из заголовка (расширения `.txt`, `.yaml`, `.yml` удаляются автоматически)

### Описание подписки

Отдельный заголовок для описания, если оно не включено в `profile-title`:

```
profile-description: Быстрые серверы в Европе
```

Поддерживает base64: `profile-description: base64:...`

### Интервал обновления подписки

Интервал автоматического обновления подписки в часах. Значение должно быть кратно одному часу.

**Заголовок:**

```
profile-update-interval: 6
```

**В теле подписки:**

```
#profile-update-interval: 6
```

### Статус подписки

Информация о балансе, объёме использованного трафика и сроке действия подписки. Поля разделяются точкой с запятой.

```
subscription-userinfo: upload=0;download=1073741824;total=10737418240;expire=1700000000
```

| Поле | Описание |
|---|---|
| `upload` | Исходящий трафик (байт) |
| `download` | Входящий трафик (байт) |
| `total` | Лимит трафика (байт) |
| `expire` | Дата истечения (Unix timestamp, секунды) |

> Если `expire` > 32 000 000 000 — значение интерпретируется как миллисекунды и конвертируется в секунды.

### Ссылка на поддержку

Кнопка перехода на страницу поддержки. Если ссылка ведёт в Telegram — отображается иконка Telegram.

**Заголовок:**

```
support-url: https://t.me/your_support_bot
```

**В теле подписки:**

```
#support-url: https://t.me/your_support_bot
```

### Ссылка на сайт

Кнопка перехода на сайт подписки.

**Заголовок:**

```
profile-web-page-url: https://your-site.com
```

**В теле подписки:**

```
#profile-web-page-url: https://your-site.com
```

Альтернативный заголовок: `homepage`

### Объявление

Текстовое объявление (до 200 символов). Можно передавать как текст или base64.

**Заголовок:**
```
announce: Плановое обслуживание 15 марта с 03:00 до 05:00 MSK
```

**Base64:**
```
announce: base64:0J/Qu9Cw0L3QvtCy0L7QtSDQvtCx0YHQu9GD0LbQuNCy0LDQvdC40LU=
```

**URL объявления** (ссылка, не текст):

```
announce-url: https://example.com/news
```

**В теле подписки:**

```
#announce: Плановое обслуживание 15 марта
#announce-url: https://example.com/news
vless://uuid@server:443#Server
```

---

## Сводная таблица параметров

| Заголовок | Альтернативы | Формат | Body (`#`) | Описание |
| --- | --- | --- | --- | --- |
| `profile-title` | `subscription-name`, `content-disposition` | текст / `base64:...` | ✅ | Имя подписки |
| `profile-description` | — | текст / `base64:...` | — | Описание подписки |
| `profile-update-interval` | — | число (часы) | ✅ | Интервал обновления |
| `subscription-userinfo` | — | `key=value;...` | — | Статистика трафика |
| `support-url` | — | URL | ✅ | Ссылка на поддержку |
| `profile-web-page-url` | `homepage` | URL | ✅ | Ссылка на сайт |
| `announce` | — | текст / `base64:...` | ✅ | Текст объявления |
| `announce-url` | — | URL | ✅ | Ссылка на объявление |
| `autorouting` | — | URL | ✅ | Автообновляемый профиль маршрутизации |
| `routing` | — | base64 / ссылка | ✅ | Статический профиль маршрутизации |
| `premium-url` | — | URL | — | Ссылка «Премиум» (в карточке подписки, см. ниже) |
| `hide-url` | — | `1` / `0` / `true` / `false` | ✅ | Скрыть URL подписки от Share/Copy/QR/backup (см. ниже) |
| `per-app-proxy-enable` | — | `1` / `0` | — | Включить per-app режим (только Android) |
| `per-app-proxy-mode` | — | `bypass` / `proxy` | — | Режим per-app |
| `per-app-proxy-list` | — | CSV / URL | — | Список package names |
| `fragmentation-enable` | — | `1` / `0` | — | TCP-фрагментация |
| `fragmentation-length` | — | `min-max` | — | Диапазон длины фрагмента |
| `fragmentation-interval` | — | `min-max` | — | Диапазон задержки между фрагментами |
| `fragmentation-packets` | — | `tlshello` / `1-3` / `all` | — | На какие пакеты применять |
| `noises-enable` | — | `1` / `0` | — | Отправка шумовых пакетов до handshake |
| `noises-type` | — | `rand` / `str` / `hex` | — | Тип шумового контента |
| `noises-packet` | — | строка | — | Payload шума (формат зависит от `type`) |
| `noises-delay` | — | `min-max` мс | — | Диапазон задержки между шумами |
| `server-address-resolve-enable` | — | `1` / `0` | — | Предварительный DNS-резолв адреса сервера через DoH |
| `server-address-resolve-dns-domain` | — | URL | — | URL DoH-сервера |
| `server-address-resolve-dns-ip` | — | IP | — | IP DoH-сервера (bootstrap) |

> Все заголовки регистронезависимы (`profile-title` = `Profile-Title`).
>
> Параметры из тела подписки (body) используются как fallback — HTTP-заголовки всегда имеют приоритет.
>
> Все заголовки со значениями поддерживают префикс `base64:` для передачи UTF-8 данных без проблем с Latin-1 / non-ASCII (применяется к `announce`, `profile-title`, `profile-description`, `per-app-proxy-list`).

---

## Маршрутизация

### Профиль маршрутизации

Статический профиль в base64. Подробнее — [routing.md](routing.md).

```
routing: ://routing/onadd/ewog...base64...
```

### Автообновляемый профиль маршрутизации

URL-источник профиля маршрутизации с периодическим обновлением. Подробнее — [autorouting.md](autorouting.md).

```
autorouting: https://raw.githubusercontent.com/user/repo/main/profile.json
```

### Приоритет источников маршрутизации

Если профиль маршрутизации указан в нескольких местах, используется **первый найденный** по приоритету:

| Приоритет | Источник |
|---|---|
| 1 (высший) | Заголовок `autorouting` |
| 2 | Body — строка с URL (`://autorouting/onadd/`, `://autorouting/add/`) |
| 3 | Заголовок `routing` |
| 4 (низший) | Body — строка с base64 (`://routing/onadd/`, `://routing/add/`, `://routing/`) |

> **Важно:** только `://autorouting/` устанавливает `sourceURL` и включает автообновление. Строки `://routing/onadd/{url}` в теле подписки импортируют профиль одноразово, без привязки к источнику.

---

## Описание сервера

Дополнительная подпись, отображаемая под именем сервера (максимум 30 символов). Добавляется после `title` через разделитель `?`:

```
vless://uuid@server:443#Сервер1?serverDescription=base64-text
```

---

## Per-app proxy (только Android)

Android VpnService позволяет пропускать через VPN только **выбранные приложения** либо наоборот — **исключать** их из туннеля. Провайдер может форсировать этот режим через три заголовка:

```
per-app-proxy-enable: 1
per-app-proxy-mode: bypass
per-app-proxy-list: com.android.chrome,org.telegram.messenger
```

### Параметры

| Заголовок | Значение | Описание |
| --- | --- | --- |
| `per-app-proxy-enable` | `1` / `0` | Включить режим per-app |
| `per-app-proxy-mode` | `bypass` \| `proxy` | `bypass` — указанные приложения **обходят** VPN. `proxy` — **только** они идут через VPN |
| `per-app-proxy-list` | CSV или URL | Список package names через запятую, перенос строки, или URL до текстового файла |

### Формат списка

**Inline (CSV или строчный):**

```
per-app-proxy-list: com.android.chrome,org.telegram.messenger,com.google.android.youtube
```

**Base64 (для длинных списков):**

```
per-app-proxy-list: base64:Y29tLmFuZHJvaWQuY2hyb21lCm9yZy50ZWxlZ3JhbS5tZXNzZW5nZXI=
```

**Удалённый URL:**

```
per-app-proxy-list: https://example.com/myapps.txt
```

Файл по URL — обычный plain text с package names по одному на строку или через запятую. Клиент скачивает его при применении подписки и при каждом обновлении.

### Поведение

- Если ни одно из трёх полей не задано — настройки пользователя в приложении **не переопределяются**.
- Если `per-app-proxy-enable` задан в `0` — per-app режим выключается, даже если пользователь его включил локально.
- Платформы кроме Android **игнорируют** эти заголовки.

---

## TCP-фрагментация

Перезаписывает глобальные настройки фрагментации пользователя для данной подписки.

```
fragmentation-enable: 1
fragmentation-packets: tlshello
fragmentation-length: 10-30
fragmentation-interval: 10-30
```

| Заголовок | Значение | Описание |
| --- | --- | --- |
| `fragmentation-enable` | `1` / `0` | Включить фрагментацию |
| `fragmentation-packets` | `tlshello` \| `1-3` \| `1` \| `all` | На какие TCP-пакеты применять фрагментацию |
| `fragmentation-length` | `min-max` | Диапазон длины фрагмента в байтах |
| `fragmentation-interval` | `min-max` | Диапазон задержки между фрагментами в мс |

Те же параметры доступны через [Premium API](premium-api.md#domain-fronting-и-фрагментация) как `fragmentEnabled / fragmentPackets / fragmentLength / fragmentInterval` — при Premium-подписке HTTP-заголовки игнорируются в пользу API-значений.

---

## Шумовые пакеты (noises)

Отправка случайных UDP-пакетов перед VPN-handshake'ом для маскировки. Актуально в первую очередь для WireGuard и Hysteria2 в сетях с глубокой инспекцией трафика.

```
noises-enable: 1
noises-type: rand
noises-packet: 10-20
noises-delay: 10-50
```

| Заголовок | Значение | Описание |
| --- | --- | --- |
| `noises-enable` | `1` / `0` | Включить шумы |
| `noises-type` | `rand` \| `str` \| `hex` | Формат payload'а |
| `noises-packet` | строка | Содержимое шумового пакета; для `rand` — диапазон длины `min-max` |
| `noises-delay` | `min-max` мс | Диапазон задержки между шумовыми пакетами |

---

## Резолв адреса сервера через DoH

Bootstrap-резолв домена сервера через DNS-over-HTTPS до установки туннеля. Полезно когда провайдерский DNS подменяет адрес VPN-сервера.

```
server-address-resolve-enable: 1
server-address-resolve-dns-domain: https://common.dot.dns.yandex.net/dns-query
server-address-resolve-dns-ip: 77.88.8.8
```

| Заголовок | Значение | Описание |
| --- | --- | --- |
| `server-address-resolve-enable` | `1` / `0` | Включить DoH-резолв |
| `server-address-resolve-dns-domain` | URL | DoH endpoint (обычно `/dns-query`) |
| `server-address-resolve-dns-ip` | IP | IP DoH-сервера для bootstrap'а — используется до резолва его домена |

Те же поля передаются через Premium API как `serverAddressResolveEnable` / `serverAddressResolveDnsDomain` / `serverAddressResolveDnsIp`.

---

## Ссылка «Премиум»

Дополнительная кнопка в карточке подписки — ведёт на страницу покупки или личный кабинет провайдера.

```
premium-url: https://example.com/pricing
```

| Заголовок | Значение | Описание |
| --- | --- | --- |
| `premium-url` | URL | URL кнопки «Премиум» в карточке подписки |

Если не задан — кнопка скрыта.

---

## Скрытие URL подписки от пользователя

Параметр `hide-url` блокирует «утечку» URL подписки за пределы устройства: при включении приложение **не показывает и не разрешает экспортировать** URL ни через Share, ни через Copy URL, ни через QR-код, ни в резервные копии. Имя подписки, серверы и весь остальной UX работают как обычно — скрывается только сам URL.

**Заголовок:**

```
hide-url: 1
```

**В теле подписки:**

```
#hide-url: 1
vless://...
```

**Premium API (JSON):**

```json
{
  "hide_url": true,
  "settings": { ... }
}
```

### Принимаемые значения

| Что прислано | Поведение |
| --- | --- |
| `1`, `true`, `yes` (без учёта регистра) | URL скрыт |
| `0`, `false`, `no`, пустая строка | URL открыт (по умолчанию) |
| Любое другое значение в заголовке | Игнорируется, URL открыт |

### Приоритет источников

1. HTTP-заголовок `hide-url` имеет наивысший приоритет
2. Строка `#hide-url:` в теле подписки используется как fallback при отсутствии заголовка
3. Поле `hide_url` в Premium API JSON — независимый источник, применяется параллельно

> Если хотя бы один источник говорит «скрыть» — URL скрывается. Чтобы снять скрытие, отключите его **во всех** источниках (либо обновите подписку с обновлённым значением).

### Что блокируется

- Кнопка **Share** в карточке подписки
- Кнопка **Copy URL**
- Показ **QR-кода** подписки
- Включение подписки в **резервную копию** (даже зашифрованную паролем)
- Кнопка экспорта в редакторе серверов подписки

### Что НЕ блокируется

- Просмотр и редактирование настроек серверов внутри подписки (на устройствах с **admin HWID** — см. [admin-hwids.md](admin-hwids.md))
- Подключение к серверам, ping, traffic stats, обновление подписки
- Резервные копии **отдельных серверов** (если они импортированы вручную, вне этой подписки)

### Правила для Premium-провайдеров

| Premium | Admin HWID | `hide-url` | Видит URL | URL в backup |
| --- | --- | --- | --- | --- |
| нет | — | нет | да | да |
| нет | — | да | нет | нет |
| да | да | нет | да | да |
| да | да | да | да | **нет** (admin видит, но экспортировать через backup нельзя) |
| да | нет | — | нет | нет |

Без `hide-url` обычные (не-premium) подписки всегда экспортируются и копируются — `hide-url` это **единственный** способ запретить это у не-premium.

---

## Настройки, которые подписка **не может** задать HTTP-заголовками

Эти параметры хранятся в [Premium API](premium-api.md) конфигурации провайдера и применяются клиентом только если домен подписки принадлежит Premium-провайдеру. Включить их «через подписку без аккаунта в панели» нельзя — это by design.

| Группа                | Что настраивается                                                                 | Ссылка                                                   |
|-----------------------|-----------------------------------------------------------------------------------|----------------------------------------------------------|
| Lite Mode             | Упрощённый интерфейс, ссылки на бот/канал/поддержку + [пресет-иконки](icon-presets.md) | [premium-api.md § Lite Mode](premium-api.md#lite-mode)          |
| Баннер подписки       | Текст + цвета + кнопка в карточке подписки                                        | [premium-api.md § Баннер подписки](premium-api.md#баннер-подписки) |
| Кастомная тема        | Плоские цвета и градиенты для аккаунта / фона                                     | [premium-api.md § Кастомная тема](premium-api.md#кастомная-тема-theme) |
| Force-настройки       | `forceConnectionStyle`: классическая круглая кнопка vs compact-toggle             | [premium-api.md § Принудительные настройки](premium-api.md#принудительные-настройки) |
| Ping и сортировка     | `defaultPingProtocol`, `defaultSortOrder`, `pingOnUpdate`                         | [premium-api.md § Ping и сортировка](premium-api.md#ping-и-сортировка) |
| Domain fronting       | `resolveAddress` / `hostHeader` (связка SNI ↔ Host для маскировки)                | [premium-api.md § Domain fronting и фрагментация](premium-api.md#domain-fronting-и-фрагментация) |
| Админ-доступ по HWID  | `adminHwids` + auto-approve пушей                                                  | [admin-hwids.md](admin-hwids.md)                         |
| Push-уведомления      | Модерация, таргетинг, отмена                                                      | [provider-notifications.md](provider-notifications.md)   |

> **Фрагментация, шумы и DoH-резолв** доступны через **оба** канала: HTTP-заголовками подписки (см. выше) или через Premium API. При Premium-подписке API-значения приоритетнее заголовков.
