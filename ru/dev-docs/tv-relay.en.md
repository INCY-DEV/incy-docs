# Sending a subscription to TV

Move a subscription to Apple TV / Android TV from a phone — from any network,
even when the devices are in different parts of the city.

The key property: **the relay cannot read what passes through it**. The
subscription link is encrypted on the phone and decrypted only on the TV. The
server sees just two opaque blobs of bytes.

- **Endpoint:** `https://check.incytv.com`
- **Source code:** [INCY-DEV/incy-tv-relay](https://github.com/INCY-DEV/incy-tv-relay)
- **Image:** [ghcr.io/incy-dev/incy-tv-relay](https://github.com/orgs/INCY-DEV/packages/container/package/incy-tv-relay)

The code is fully open — you can verify the server really decrypts nothing, and
run your own relay if you prefer.

---

## How it works

An 8-character code appears on the TV. You type it on the phone (or scan the
QR) — and the subscription moves across.

```
TV                        Relay                     Phone
 │                          │                         │
 │  claims a code           │                         │
 │─────────────────────────>│                         │
 │                          │                         │
 │  shows                   │   reads parameters      │
 │  K7M2XQ4P + QR           │<────────────────────────│
 │                          │                         │
 │                          │   encrypts subscription │
 │                          │   with key from code    │
 │                          │                         │
 │                          │<─── ciphertext ─────────│
 │<─── ciphertext ──────────│                         │
 │                          │                         │
 │  decrypts                │  record is deleted      │
```

Both sides derive a shared encryption key **from the code alone**, using the
CPace protocol. The relay, observing the entire exchange, cannot derive that
key: it only sees public values from which the secret cannot be recovered.

!!! info "Why 8 characters is enough"
    Short codes usually mean weak protection. Not here: even with the traffic
    captured, an attacker **cannot brute-force the code on their own machine**.
    Every attempt requires contacting the server, and the server allows only
    5 attempts before destroying the code.

    That is why typing the code manually is as safe as scanning the QR — in
    both cases only the code travels, and the key is computed on the devices.

---

## What the server sees

| Data | Stored | Note |
|---|---|---|
| Subscription link | **no** | encrypted, server has no key |
| Provider name | **no** | inside the same ciphertext |
| Device IP addresses | **no** | not written to storage or logs |
| Transfer history | **no** | record deleted right after delivery |
| Two blobs of bytes | 5 minutes | then removed automatically |

Request bodies are not logged — they contain ciphertext, but logs tend to leak,
so they simply do not exist.

---

## Local transfer without the internet

When the phone and TV are on the same Wi-Fi, the app uses a **direct connection**
(Bonjour, `_incy-tv._tcp`) — the data never leaves the home network and never
touches the server.

The relay kicks in only when a direct connection is impossible. The user is not
shown the difference — it just works either way.

---

## API for integrations

Your bots and panels can push a subscription to a user's TV the same way. All
bodies are JSON; binary fields are base64url without padding.

### Claim a code

Called by the TV.

```http
POST /pair/init
Content-Type: application/json

{ "code": "K7M2XQ4P", "sid": "<16 bytes>", "ya": "<32 bytes>" }
```

| Response | Meaning |
|---|---|
| `204` | accepted |
| `409` | code taken — generate a new one and retry |
| `400` | malformed code or point |

### Read parameters

Called by the sender.

```http
GET /pair/K7M2XQ4P
```

```json
{ "sid": "<16 bytes>", "ya": "<32 bytes>" }
```

| Response | Meaning |
|---|---|
| `200` | parameters retrieved |
| `404` | code missing or expired |
| `429` | attempt limit exceeded, code destroyed |

!!! warning "Every call counts as an attempt"
    This is the brute-force protection. After 5 calls the code burns —
    do not poll this endpoint in a loop.

### Send the subscription

```http
POST /pair/K7M2XQ4P/send
Content-Type: application/json

{ "yb": "<32 bytes>", "nonce": "<12 bytes>", "ct": "<ciphertext+tag>" }
```

| Response | Meaning |
|---|---|
| `204` | accepted |
| `404` | code missing or expired |
| `409` | subscription already sent (one-shot) |
| `413` | body larger than 64 KiB |

### Collect the subscription

Called by the TV. The request hangs up to 30 seconds waiting for the sender.

```http
GET /pair/K7M2XQ4P/result
```

| Response | Meaning |
|---|---|
| `200` | `{ "yb": …, "nonce": …, "ct": … }`, record deleted immediately |
| `204` | nothing yet — repeat the request |
| `404` | code expired |

### Service endpoints

`GET /healthz` — is the service alive. `GET /readyz` — is it ready to serve.

---

## Limits

| What | Limit |
|---|---|
| Attempts per code | 5, then the code is destroyed |
| Requests per IP | 30 per minute |
| Code creation per IP | 10 per hour |
| Body size | 64 KiB |
| Code lifetime | 5 minutes |

The per-code limit matters more than the per-IP one: switching addresses does
not help, which is what makes brute force pointless.

---

## What to send

Inside the ciphertext — JSON:

```json
{
  "v": 1,
  "type": "subscription",
  "url": "https://example.com/sub",
  "name": "My Provider"
}
```

Send the **subscription link, not an expanded config**: the TV will fetch it
itself and get the current server list. That is orders of magnitude smaller and
always up to date.

---

## Cryptography

For compatibility with the app the parameters must match byte for byte.

| Parameter | Value |
|---|---|
| Group | Ristretto255 |
| Protocol | CPace |
| Encryption | ChaCha20-Poly1305 |
| Key derivation | HKDF-SHA256 |
| Code alphabet | `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (no `I`, `O`, `0`, `1`) |

```
generator = ristretto255_from_hash( SHA-512(dsi ‖ code ‖ sid) )
scalar    = ristretto255_scalar_reduce( 64 random bytes )
Y         = ristretto255_scalarmult( scalar, generator )
K         = ristretto255_scalarmult( scalar, Y_peer )
key       = HKDF-SHA256( K ‖ min(Ya,Yb) ‖ max(Ya,Yb), salt=sid, info=dsi, 32 )
dsi       = "CPace255-INCY-TVRELAY-v1"
```

Points are sorted lexicographically so both sides hash them in the same order
without negotiating who goes "first".

Test vector for verifying an implementation:

```
generator("TESTCODE", sid = 000102…0f) =
def51453cb5cfdb7d78e667cf7575060841474e063f5e39ea28f14fd9340042f
```

Libraries: **libsodium** (iOS/tvOS — `swift-sodium`), **lazysodium**
(Android — `com.goterl:lazysodium-android`). Ristretto255 is available in both
without hand-written bindings.

!!! tip "Verify compatibility with a test"
    A key mismatch between platforms means the transfer simply will not work.
    Check the test vector above — that is faster than debugging
    "it won't decrypt".

---

## Example: Python bot

Sending a subscription to a user's TV by the code they typed.

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
    # 1. Read the TV parameters. This counts as an attempt — do not retry
    #    on failure, the code burns after 5 of them.
    r = httpx.get(f"{BASE}/pair/{code}", timeout=10)
    if r.status_code == 404:
        raise ValueError("code not found or expired")
    if r.status_code == 429:
        raise ValueError("code locked after failed attempts")
    r.raise_for_status()
    sid, ya = b64d(r.json()["sid"]), b64d(r.json()["ya"])

    # 2. Derive the shared key from the code — the server cannot do this.
    generator = crypto_core_ristretto255_from_hash(
        hashlib.sha512(DSI + code.encode() + sid).digest()
    )
    scalar = crypto_core_ristretto255_scalar_random()
    yb = crypto_scalarmult_ristretto255(scalar, generator)
    shared = crypto_scalarmult_ristretto255(scalar, ya)

    lo, hi = sorted([ya, yb])          # same point order on both sides
    key = HKDF(hashes.SHA256(), 32, sid, DSI).derive(shared + lo + hi)

    # 3. Encrypt and send.
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
        raise ValueError("a subscription was already sent to this code")
    resp.raise_for_status()
```

Dependencies: `pynacl`, `cryptography`, `httpx`.

---

## Example: Node.js bot

```js
import sodium from 'libsodium-wrappers-sumo';
import { createHash, hkdfSync, randomBytes, createCipheriv } from 'node:crypto';

const BASE = 'https://check.incytv.com';
const DSI = Buffer.from('CPace255-INCY-TVRELAY-v1');

const b64e = (b) => Buffer.from(b).toString('base64url');
const b64d = (s) => Buffer.from(s, 'base64url');

export async function sendSubscription(code, url, name) {
  await sodium.ready;

  // 1. TV parameters (one attempt — the per-code limit is 5).
  const r = await fetch(`${BASE}/pair/${code}`);
  if (r.status === 404) throw new Error('code not found or expired');
  if (r.status === 429) throw new Error('code locked');
  if (!r.ok) throw new Error(`relay returned ${r.status}`);
  const { sid: sidB64, ya: yaB64 } = await r.json();
  const sid = b64d(sidB64); const ya = b64d(yaB64);

  // 2. The shared key is derived on the devices, not on the server.
  const generator = sodium.crypto_core_ristretto255_from_hash(
    createHash('sha512').update(Buffer.concat([DSI, Buffer.from(code), sid])).digest(),
  );
  const scalar = sodium.crypto_core_ristretto255_scalar_random();
  const yb = sodium.crypto_scalarmult_ristretto255(scalar, generator);
  const shared = sodium.crypto_scalarmult_ristretto255(scalar, ya);

  // Lexicographic point order — identical on both sides.
  const [lo, hi] = [Buffer.from(ya), Buffer.from(yb)].sort(Buffer.compare);
  const key = Buffer.from(hkdfSync(
    'sha256', Buffer.concat([Buffer.from(shared), lo, hi]), sid, DSI, 32,
  ));

  // 3. Encrypt and send.
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
  if (resp.status === 409) throw new Error('already sent to this code');
  if (!resp.ok) throw new Error(`relay returned ${resp.status}`);
}
```

Dependency: `libsodium-wrappers-sumo` (the regular `libsodium-wrappers` build
does not include Ristretto255 functions).

---

## Common errors

**`404` on every request.** The code expired — it lives 5 minutes. Ask the user
to reopen the add-subscription screen on the TV.

**`429` on the very first call.** Someone was already guessing this code and it
was destroyed. A fresh code from the TV is needed.

**TV says "invalid code".** The MAC did not match: either the code was mistyped,
or your crypto implementation diverges. Check the test vector.

**`409` when sending.** A subscription was already sent to this code — it is
one-shot.

**Empty `204` from `/result`.** That is normal: the sender has not posted yet.
Repeat the request; the connection is held for up to 30 seconds.

---

## Running your own relay

The server stores nothing persistent, so it is easy to self-host:

```bash
git clone https://github.com/INCY-DEV/incy-tv-relay
cd incy-tv-relay
npm install
REDIS_URL=redis://localhost:6379 npm start
```

Redis is the only dependency. The repository ships Kubernetes manifests and a
`Dockerfile`.

The app uses `check.incytv.com` by default; your own relay address is set in the
build configuration.
