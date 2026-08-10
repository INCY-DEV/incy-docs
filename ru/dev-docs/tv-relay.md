# Передача подписки на ТВ

Перенос подписки на Apple TV / Android TV с телефона — из любой сети, даже
если устройства находятся на разных концах города.

Ключевое свойство: **релей не может прочитать то, что через него передаётся**.
Ссылка на подписку шифруется на телефоне и расшифровывается только на
телевизоре. Сервер видит лишь два непрозрачных блока байтов.

- **Адрес:** `https://check.incytv.com`
- **Исходный код:** [INCY-DEV/incy-tv-relay](https://github.com/INCY-DEV/incy-tv-relay)
- **Образ:** [ghcr.io/incy-dev/incy-tv-relay](https://github.com/orgs/INCY-DEV/packages/container/package/incy-tv-relay)

Код открыт целиком — можно убедиться, что сервер действительно ничего не
расшифровывает, и при желании поднять свой релей.

---

## Как это работает

На телевизоре появляется 8-значный код. Вы вводите его на телефоне (или
сканируете QR) — и подписка переезжает.

```
Телевизор                  Релей                    Телефон
    │                        │                        │
    │  занимает код          │                        │
    │───────────────────────>│                        │
    │                        │                        │
    │  показывает            │   читает параметры     │
    │  K7M2XQ4P + QR         │<───────────────────────│
    │                        │                        │
    │                        │   шифрует подписку     │
    │                        │   ключом из кода       │
    │                        │                        │
    │                        │<─── шифротекст ────────│
    │<─── шифротекст ────────│                        │
    │                        │                        │
    │  расшифровывает        │  запись удаляется      │
```

Обе стороны выводят общий ключ шифрования **из одного лишь кода** — по
протоколу CPace. Релей, наблюдая весь обмен целиком, этот ключ вывести не
может: он видит только публичные значения, из которых секрет не
восстанавливается.

!!! info "Почему 8 знаков — это достаточно"
    Обычно короткий код означает слабую защиту. Здесь иначе: перехватив
    трафик, злоумышленник **не может подбирать код у себя на компьютере**.
    Каждая попытка требует обращения к серверу, а там лимит — 5 попыток,
    после чего код уничтожается.

    Поэтому ручной ввод кода так же надёжен, как QR — в обоих случаях
    передаётся только код, а ключ вычисляется на устройствах.

---

## Что видит сервер

| Данные | Хранит | Комментарий |
|---|---|---|
| Ссылка на подписку | **нет** | зашифрована, ключа у сервера нет |
| Название провайдера | **нет** | внутри того же шифротекста |
| IP-адреса устройств | **нет** | не пишутся ни в базу, ни в логи |
| История переносов | **нет** | запись удаляется сразу после доставки |
| Два блока байтов | 5 минут | затем исчезают автоматически |

Тела запросов не логируются — там шифротекст, но логи имеют свойство утекать,
поэтому их просто нет.

---

## Локальный перенос без интернета

Если телефон и телевизор в одной сети Wi-Fi, приложение использует **прямое
соединение** (Bonjour, `_incy-tv._tcp`) — данные вообще не покидают домашнюю
сеть и не идут через сервер.

Релей включается только тогда, когда прямое соединение невозможно. Разница
пользователю не показывается — работает и так, и так.

---

## API для интеграции

Своим ботам и панелям можно передавать подписку на телевизор пользователя
тем же способом. Все тела — JSON, бинарные поля — base64url без паддинга.

### Занять код

Вызывает телевизор.

```http
POST /pair/init
Content-Type: application/json

{ "code": "K7M2XQ4P", "sid": "<16 байт>", "ya": "<32 байта>" }
```

| Ответ | Значение |
|---|---|
| `204` | принято |
| `409` | код занят — сгенерировать новый и повторить |
| `400` | неверный формат кода или точки |

### Прочитать параметры

Вызывает отправитель.

```http
GET /pair/K7M2XQ4P
```

```json
{ "sid": "<16 байт>", "ya": "<32 байта>" }
```

| Ответ | Значение |
|---|---|
| `200` | параметры получены |
| `404` | кода нет или истёк |
| `429` | превышен лимит попыток, код уничтожен |

!!! warning "Каждый вызов считается попыткой"
    Это и есть защита от перебора. После 5 обращений код сгорает —
    не опрашивайте эндпоинт в цикле.

### Отправить подписку

```http
POST /pair/K7M2XQ4P/send
Content-Type: application/json

{ "yb": "<32 байта>", "nonce": "<12 байт>", "ct": "<шифротекст+тег>" }
```

| Ответ | Значение |
|---|---|
| `204` | принято |
| `404` | кода нет или истёк |
| `409` | подписка уже отправлена (одноразово) |
| `413` | тело больше 64 КиБ |

### Забрать подписку

Вызывает телевизор. Запрос висит до 30 секунд, ожидая отправителя.

```http
GET /pair/K7M2XQ4P/result
```

| Ответ | Значение |
|---|---|
| `200` | `{ "yb": …, "nonce": …, "ct": … }`, запись сразу удаляется |
| `204` | пока ничего — повторить запрос |
| `404` | код истёк |

### Служебные

`GET /healthz` — жив ли сервис. `GET /readyz` — готов ли принимать запросы.

---

## Ограничения

| Что | Лимит |
|---|---|
| Попыток на один код | 5, дальше код уничтожается |
| Запросов с одного IP | 30 в минуту |
| Создание кодов с одного IP | 10 в час |
| Размер тела | 64 КиБ |
| Время жизни кода | 5 минут |

Лимит на код важнее лимита на IP: смена адреса от него не спасает, поэтому
перебор бессмыслен.

---

## Что передавать

Внутри шифротекста — JSON:

```json
{
  "v": 1,
  "type": "subscription",
  "url": "https://example.com/sub",
  "name": "Мой провайдер"
}
```

Передавайте **ссылку на подписку, а не развёрнутый конфиг**: телевизор сам её
загрузит и получит актуальный список серверов. Так объём на порядки меньше, и
конфигурация всегда свежая.

---

## Криптография

Для совместимости с приложением параметры должны совпадать байт в байт.

| Параметр | Значение |
|---|---|
| Группа | Ristretto255 |
| Протокол | CPace |
| Шифрование | ChaCha20-Poly1305 |
| Вывод ключа | HKDF-SHA256 |
| Алфавит кода | `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (без `I`, `O`, `0`, `1`) |

```
generator = ristretto255_from_hash( SHA-512(dsi ‖ code ‖ sid) )
scalar    = ristretto255_scalar_reduce( 64 случайных байта )
Y         = ristretto255_scalarmult( scalar, generator )
K         = ristretto255_scalarmult( scalar, Y_peer )
key       = HKDF-SHA256( K ‖ min(Ya,Yb) ‖ max(Ya,Yb), salt=sid, info=dsi, 32 )
dsi       = "CPace255-INCY-TVRELAY-v1"
```

Точки сортируются лексикографически — чтобы обе стороны хешировали их в одном
порядке, не договариваясь, кто «первый».

Контрольный вектор для проверки реализации:

```
generator("TESTCODE", sid = 000102…0f) =
def51453cb5cfdb7d78e667cf7575060841474e063f5e39ea28f14fd9340042f
```

Библиотеки: **libsodium** (iOS/tvOS — `swift-sodium`), **lazysodium**
(Android — `com.goterl:lazysodium-android`). Ristretto255 доступен в обеих
без рукописных биндингов.

!!! tip "Проверяйте совместимость тестом"
    Расхождение ключей между платформами означает, что перенос просто не
    сработает. Сверьте контрольный вектор выше — это быстрее, чем
    отлаживать «не расшифровывается».

---

## Пример: бот на Python

Отправка подписки на телевизор пользователя по введённому коду.

```python
import base64, json, secrets, httpx
from nacl.bindings import (
    crypto_core_ristretto255_from_hash,
    crypto_core_ristretto255_scalar_random,
    crypto_scalarmult_ristretto255,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import hashlib

BASE = "https://check.incytv.com"
DSI = b"CPace255-INCY-TVRELAY-v1"

b64d = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
b64e = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")


def send_subscription(code: str, url: str, name: str) -> None:
    # 1. Читаем параметры телевизора. Это считается попыткой —
    #    повторять при неудаче нельзя, после 5 раз код сгорит.
    r = httpx.get(f"{BASE}/pair/{code}", timeout=10)
    if r.status_code == 404:
        raise ValueError("код не найден или истёк")
    if r.status_code == 429:
        raise ValueError("код заблокирован из-за неверных попыток")
    r.raise_for_status()
    sid, ya = b64d(r.json()["sid"]), b64d(r.json()["ya"])

    # 2. Выводим общий ключ из кода — сервер этого сделать не может.
    generator = crypto_core_ristretto255_from_hash(
        hashlib.sha512(DSI + code.encode() + sid).digest()
    )
    scalar = crypto_core_ristretto255_scalar_random()
    yb = crypto_scalarmult_ristretto255(scalar, generator)
    shared = crypto_scalarmult_ristretto255(scalar, ya)

    lo, hi = sorted([ya, yb])          # порядок точек одинаков у обеих сторон
    key = HKDF(hashes.SHA256(), 32, sid, DSI).derive(shared + lo + hi)

    # 3. Шифруем и отправляем.
    payload = json.dumps(
        {"v": 1, "type": "subscription", "url": url, "name": name}
    ).encode()
    nonce = secrets.token_bytes(12)
    ct = ChaCha20Poly1305(key).encrypt(nonce, payload, None)

    resp = httpx.post(
        f"{BASE}/pair/{code}/send",
        json={"yb": b64e(yb), "nonce": b64e(nonce), "ct": b64e(ct)},
        timeout=10,
    )
    if resp.status_code == 409:
        raise ValueError("на этот код уже отправляли подписку")
    resp.raise_for_status()
```

Зависимости: `pynacl`, `cryptography`, `httpx`.

---

## Пример: бот на Node.js

```js
import sodium from 'libsodium-wrappers-sumo';
import { createHash, hkdfSync, randomBytes, createCipheriv } from 'node:crypto';

const BASE = 'https://check.incytv.com';
const DSI = Buffer.from('CPace255-INCY-TVRELAY-v1');

const b64e = (b) => Buffer.from(b).toString('base64url');
const b64d = (s) => Buffer.from(s, 'base64url');

export async function sendSubscription(code, url, name) {
  await sodium.ready;

  // 1. Параметры телевизора (одна попытка — лимит 5 на код).
  const r = await fetch(`${BASE}/pair/${code}`);
  if (r.status === 404) throw new Error('код не найден или истёк');
  if (r.status === 429) throw new Error('код заблокирован');
  if (!r.ok) throw new Error(`релей вернул ${r.status}`);
  const { sid: sidB64, ya: yaB64 } = await r.json();
  const sid = b64d(sidB64); const ya = b64d(yaB64);

  // 2. Общий ключ выводится из кода на устройствах, не на сервере.
  const generator = sodium.crypto_core_ristretto255_from_hash(
    createHash('sha512').update(Buffer.concat([DSI, Buffer.from(code), sid])).digest(),
  );
  const scalar = sodium.crypto_core_ristretto255_scalar_random();
  const yb = sodium.crypto_scalarmult_ristretto255(scalar, generator);
  const shared = sodium.crypto_scalarmult_ristretto255(scalar, ya);

  // Лексикографический порядок точек — одинаковый у обеих сторон.
  const [lo, hi] = [Buffer.from(ya), Buffer.from(yb)].sort(Buffer.compare);
  const key = Buffer.from(hkdfSync(
    'sha256', Buffer.concat([Buffer.from(shared), lo, hi]), sid, DSI, 32,
  ));

  // 3. Шифруем и отправляем.
  const payload = Buffer.from(JSON.stringify(
    { v: 1, type: 'subscription', url, name },
  ));
  const nonce = randomBytes(12);
  const cipher = createCipheriv('chacha20-poly1305', key, nonce, { authTagLength: 16 });
  const ct = Buffer.concat([cipher.update(payload), cipher.final(), cipher.getAuthTag()]);

  const resp = await fetch(`${BASE}/pair/${code}/send`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ yb: b64e(yb), nonce: b64e(nonce), ct: b64e(ct) }),
  });
  if (resp.status === 409) throw new Error('на этот код уже отправляли');
  if (!resp.ok) throw new Error(`релей вернул ${resp.status}`);
}
```

Зависимость: `libsodium-wrappers-sumo` (обычная сборка `libsodium-wrappers`
не содержит функций Ristretto255).

---

## Типичные ошибки

**`404` на все запросы.** Код истёк — он живёт 5 минут. Попросите пользователя
открыть экран добавления на телевизоре заново.

**`429` при первом же обращении.** Кто-то уже перебирал этот код, и он
уничтожен. Нужен новый код с телевизора.

**Телевизор пишет «неверный код».** MAC не сошёлся: либо код введён с ошибкой,
либо реализация криптографии расходится. Проверьте контрольный вектор.

**`409` при отправке.** На этот код уже отправляли подписку — она одноразовая.

**Пустой ответ `204` от `/result`.** Это норма: отправитель ещё не прислал
данные. Повторите запрос, соединение держится до 30 секунд.

---

## Свой релей

Сервер не хранит ничего постоянного, поэтому его легко поднять самостоятельно:

```bash
git clone https://github.com/INCY-DEV/incy-tv-relay
cd incy-tv-relay
npm install
REDIS_URL=redis://localhost:6379 npm start
```

Нужен только Redis. В репозитории есть готовые манифесты Kubernetes и
`Dockerfile`.

Приложение по умолчанию использует `check.incytv.com`; адрес своего релея
задаётся в настройках сборки.
