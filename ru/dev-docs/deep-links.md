# Deep Links

Приложение поддерживает deep link ссылки для управления VPN, импорта конфигураций и настройки маршрутизации.

## Поддерживаемые схемы

Приложение обрабатывает ссылки с любой зарегистрированной схемой (`incy://`, и др.). Также поддерживаются прямые протокольные ссылки.

## Управление VPN

| Ссылка | Описание |
|---|---|
| `://connect` или `://open` | Подключить VPN |
| `://disconnect` или `://close` | Отключить VPN |
| `://toggle` | Переключить состояние VPN |
| `://status` | Открыть приложение (показать статус) |

## Импорт конфигураций

| Ссылка | Описание |
| --- | --- |
| `://import/{data}` | Автоопределение типа данных (URL подписки, конфигурация сервера, несколько URL) |
| `://add/{url}` | Добавить подписку или конфигурацию напрямую |
| `://crypt1/{payload}` | Зашифрованный (обфусцированный) вариант `://add/` — см. [Шифрованные ссылки crypt1](#шифрованные-ссылки-crypt1) ниже |

### Протокольные ссылки

Прямое добавление серверов через протокольные ссылки:

```
vless://uuid@server:443?security=tls&type=ws&sni=example.com#Server Name
vmess://eyJhZGQiOiJzZXJ2ZXIiLCJwb3J0Ijo0NDN9
trojan://password@server:443?security=tls&sni=example.com#Server Name
ss://method:password@server:8388#Server Name
hysteria2://password@server:443?sni=example.com#Server Name
socks://user:pass@server:1080#Server Name
wireguard://secretKey@server:51820?publickey=KEY&address=10.0.0.2#Server Name
```

## Маршрутизация

| Ссылка | Описание |
|---|---|
| `://routing/add/{base64}` | Добавить профиль маршрутизации |
| `://routing/onadd/{base64}` | Добавить и сразу активировать профиль |
| `://routing/onadd/{url}` | Скачать профиль по URL (одноразовый импорт, без автообновления) |
| `://autorouting/onadd/{url}` | Скачать профиль по URL и установить автообновление |
| `://autorouting/add/{url}` | Скачать профиль по URL и установить автообновление |
| `://onadd/{url}` | Сокращённая форма (одноразовый импорт, без автообновления) |

Подробнее: [routing.md](routing.md), [autorouting.md](autorouting.md).

### Query-параметр

Для совместимости поддерживается передача данных через query-параметр `data` (Android, iOS):

```
://routing/add?data={base64}
://routing/onadd?data={base64}
```

### Определение типа данных

Тип определяется **по схеме ссылки**:

- `://autorouting/` — автообновление (`sourceURL` устанавливается)
- `://routing/` — одноразовый импорт (без `sourceURL`, без автообновления)

Если данные после `onadd/` — URL (`http://`/`https://`), профиль скачивается по этому URL. Если base64 — декодируется напрямую.

## Примеры

### Подключение VPN
```
incy://connect
```

### Импорт подписки
```
incy://import/https://example.com/api/subscription/abc123
```

### Добавление сервера
```
incy://add/vless://uuid@server:443?security=tls#MyServer
```

### Добавление маршрутизации из GitHub

```text
incy://autorouting/onadd/https://github.com/user/repo/blob/main/profile.json
```

---

## Шифрованные ссылки crypt1

`incy://crypt1/<payload>` — обфусцированный (зашифрованный) вариант `://add/<url>`. Внутри лежит та же ссылка на подписку, что в обычном `://add/`, но base64url-payload снаружи не позволяет регэкспам и сканерам распознать VPN-URL.

### Когда использовать

| Сценарий | Рекомендация |
| --- | --- |
| Отправка ссылки в Telegram-чат / канал | crypt1 — Telegram-модерация не распознаёт VPN-паттерн |
| Публикация на сайте / в FAQ | crypt1 — снижает вероятность авто-блокировки по содержимому |
| Внутренний обмен ссылками в админ-панели | plain `://add/` — нет смысла шифровать |
| Скриншоты / документация / служебные сообщения | crypt1 — пользователь не «выдаёт» URL даже случайно |

### Wire format

```text
incy://crypt1/<base64url(iv(12) || ciphertext || tag(16))>
```

Расшифрованный payload — компактный UTF-8 JSON:

```json
{
  "url": "https://sub.example.com/abc123token",
  "v": 1,
  "n": "MyProvider VPN"
}
```

| Поле | Тип | Описание |
| --- | --- | --- |
| `url` | string | URL подписки (тот же, что в `://add/{url}`) |
| `v` | integer | Версия схемы payload'а, сейчас `1` |
| `n` | string? | Опциональное имя провайдера — приложение покажет его в окне подтверждения импорта и предзаполнит поле «Имя» |

### Шифрование

- **AES-256-GCM**
- Ключ K1 «зашит» в клиенты iOS / Android / Desktop и публикуется в виде [NPM-пакета `@incy/link-encoder`](https://www.npmjs.com/package/@incy/link-encoder) — благодаря этому провайдеры могут собирать crypt1-ссылки из своих ботов и сайтов
- При компрометации ключа в новой версии клиентов будет введён `crypt2/` со свежей keymat. **Существующие `crypt1/` ссылки продолжают работать неограниченно долго** — старые схемы из декодера никогда не удаляются.

> ⚠️ **Это обфускация, а не криптография.** Цель — не дать автоматическим сканерам распознать VPN-URL. Реверс-инженер с Frida извлечёт ключ из клиента примерно за час. Не используйте crypt1 в задачах, где нужна реальная защита секрета.

### Как генерировать ссылки

#### Браузер / онлайн-инструмент

Лендинг [incy.cc/encrypt](https://incy.cc/encrypt) делает crypt1 полностью на клиенте через Web Crypto API — ничего не отправляется на сервер.

#### NPM-пакет (Node.js, бэкенд, боты)

```bash
npm install @incy/link-encoder
```

```js
import { encryptLink } from '@incy/link-encoder';

const link = encryptLink('https://sub.your-provider.example/abc123token', {
  name: 'My Provider VPN',
});

console.log(link);
// → incy://crypt1/AAECAwQFBgcICQoLNyIQL3rDwRZqnyoD8pGK…
```

API:

```ts
encryptLink(url: string, opts?: { name?: string }): string
decryptLink(link: string): { url: string; name?: string }
```

Подробнее — [README пакета](https://github.com/INCY-DEV/incy-link-encoder).

### Поведение приложения при импорте

| Шаг | Что делает клиент |
| --- | --- |
| 1 | Пользователь тапает / сканирует / вставляет `incy://crypt1/<payload>` |
| 2 | Клиент декодирует payload, восстанавливает `url` |
| 3 | Открывается окно подтверждения импорта (как у `://add/`), URL подписки **скрыт** под `••••` чтобы не «утечь» в скриншоте |
| 4 | Если в payload есть `n` — отображается как имя провайдера в этом окне и пред-заполняется в поле «Имя» |
| 5 | После подтверждения — обычный flow импорта подписки |
| 6 | Внутренний флаг `importedViaCrypt1=true` сохраняется у созданной подписки. При последующем Share/Copy/QR клиент **снова** выдаёт crypt1, не обнажая URL |

### Сохранение wire-format'а при шеринге

При нажатии **Share** / **Copy URL** / **Show QR** на карточке подписки клиент эмитит тот же формат, в котором подписка была добавлена:

- Добавлена через `https://...` → Share выдаёт `https://...`
- Добавлена через `incy://crypt1/...` → Share выдаёт `incy://crypt1/...`

Это гарантирует, что обфускация не теряется по цепочке пересылок: если провайдер изначально опубликовал crypt1-ссылку, все пересылки её копии в Telegram-чатах остаются crypt1-овыми.

### Совместимость

| Версия INCY | Поддержка |
| --- | --- |
| iOS / Android / Desktop ≥ июнь 2026 | Да, нативный handler `incy://crypt1/` |
| Более старые версии | Ссылка не открывается — пользователю нужно обновиться |
| Сторонние VPN-клиенты (V2Box, Shadowrocket, Happ) | Не поддерживается, scheme зарегистрирован только для INCY |

### Примеры crypt1

#### Простая ссылка

```text
incy://crypt1/FZEVXuV39UEX1yHB3nkrgdPdrJ3syVxcQm_Y-lY0oKWAT5yRn00xe6ohg06aVWjWRrGJ7BAeEzuoFzv8XBosLnqnqqCMbnAJmR7EN2hII4Yyql1FtWlLlLs
```

#### С брендингом провайдера в QR-коде

QR-код, сгенерированный из crypt1-ссылки с полем `n`, при сканировании в INCY покажет пользователю «MyProvider VPN — Подтвердить импорт?» — провайдер брендится в окне подтверждения без серверного round-trip.
