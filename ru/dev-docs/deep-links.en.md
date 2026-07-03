# Deep Links

The application supports deep links for controlling the VPN, importing configurations, and configuring routing.

## Supported schemes

The application handles links with any registered scheme (`incy://`, etc.). Direct protocol links are also supported.

## VPN control

| Link | Description |
|---|---|
| `://connect` or `://open` | Connect the VPN |
| `://disconnect` or `://close` | Disconnect the VPN |
| `://toggle` | Toggle the VPN state |
| `://status` | Open the application (show status) |

## Importing configurations

| Link | Description |
| --- | --- |
| `://import/{data}` | Auto-detects the data type (subscription URL, server configuration, multiple URLs, raw WireGuard/AmneziaWG `.conf`) |
| `://add/{url}` | Add a subscription or configuration directly |
| `://crypt1/{payload}` | Encrypted (obfuscated) variant of `://add/` — see [Encrypted crypt1 links](#encrypted-crypt1-links) below |

`://import/{data}` also accepts a **raw `.conf`** for WireGuard/AmneziaWG (a multi-line INI with `[Interface]`/`[Peer]`). For reliable delivery, base64-encode the `.conf`: `incy://import/{base64-conf}` (plain text is also supported). AmneziaWG is detected by its obfuscation parameters (`Jc`, `S1`–`S4`, `H1`–`H4`, `I1`–`I5`). More on `.conf` — [subscription-format.md](subscription-format.md).

### Protocol links

Adding servers directly via protocol links:

```
vless://uuid@server:443?security=tls&type=ws&sni=example.com#Server Name
vmess://eyJhZGQiOiJzZXJ2ZXIiLCJwb3J0Ijo0NDN9
trojan://password@server:443?security=tls&sni=example.com#Server Name
ss://method:password@server:8388#Server Name
hysteria2://password@server:443?sni=example.com#Server Name
socks://user:pass@server:1080#Server Name
wireguard://secretKey@server:51820?publickey=KEY&address=10.0.0.2#Server Name
```

## Routing

| Link | Description |
|---|---|
| `://routing/add/{base64}` | Add a routing profile |
| `://routing/onadd/{base64}` | Add and immediately activate the profile |
| `://routing/onadd/{url}` | Download the profile from a URL (one-time import, no auto-updates) |
| `://autorouting/onadd/{url}` | Download the profile from a URL and set up auto-updates |
| `://autorouting/add/{url}` | Download the profile from a URL and set up auto-updates |
| `://onadd/{url}` | Short form (one-time import, no auto-updates) |

More details: [routing.md](routing.md), [autorouting.md](autorouting.md).

### Query parameter

For compatibility, passing data via the `data` query parameter is supported (Android, iOS):

```
://routing/add?data={base64}
://routing/onadd?data={base64}
```

### Data type detection

The type is determined **by the link scheme**:

- `://autorouting/` — auto-updates (`sourceURL` is set)
- `://routing/` — one-time import (no `sourceURL`, no auto-updates)

If the data after `onadd/` is a URL (`http://`/`https://`), the profile is downloaded from that URL. If it is base64 — it is decoded directly.

## Examples

### Connecting the VPN
```
incy://connect
```

### Importing a subscription
```
incy://import/https://example.com/api/subscription/abc123
```

### Adding a server
```
incy://add/vless://uuid@server:443?security=tls#MyServer
```

### Adding routing from GitHub

```text
incy://autorouting/onadd/https://github.com/user/repo/blob/main/profile.json
```

---

## Encrypted crypt1 links

`incy://crypt1/<payload>` is an obfuscated (encrypted) variant of `://add/<url>`. Inside is the same subscription link as in a regular `://add/`, but the outer base64url payload prevents regexes and scanners from recognizing the VPN URL.

### When to use

| Scenario | Recommendation |
| --- | --- |
| Sending a link to a Telegram chat / channel | crypt1 — Telegram moderation does not recognize the VPN pattern |
| Publishing on a website / in an FAQ | crypt1 — reduces the chance of content-based auto-blocking |
| Internal link exchange in the admin panel | plain `://add/` — no point in encrypting |
| Screenshots / documentation / service messages | crypt1 — the user does not "leak" the URL even by accident |

### Wire format

```text
incy://crypt1/<base64url(iv(12) || ciphertext || tag(16))>
```

The decrypted payload is compact UTF-8 JSON:

```json
{
  "url": "https://sub.example.com/abc123token",
  "v": 1,
  "n": "MyProvider VPN"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `url` | string | Subscription URL (the same as in `://add/{url}`) |
| `v` | integer | Payload schema version, currently `1` |
| `n` | string? | Optional provider name — the application shows it in the import confirmation dialog and prefills the "Name" field |

### Encryption

- **AES-256-GCM**
- The K1 key is "baked into" the iOS / Android / Desktop clients and published as the [NPM package `@incy/link-encoder`](https://www.npmjs.com/package/@incy/link-encoder) — this lets providers build crypt1 links from their bots and websites
- If the key is compromised, a new client version will introduce `crypt2/` with fresh keymat. **Existing `crypt1/` links keep working indefinitely** — old schemes are never removed from the decoder.

> ⚠️ **This is obfuscation, not cryptography.** The goal is to keep automated scanners from recognizing the VPN URL. A reverse engineer with Frida will extract the key from the client in about an hour. Do not use crypt1 for tasks that require real secret protection.

### How to generate links

#### Browser / online tool

The [incy.cc/encrypt](https://incy.cc/encrypt) landing page does crypt1 entirely on the client via the Web Crypto API — nothing is sent to the server.

#### NPM package (Node.js, backend, bots)

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

More details — [package README](https://github.com/INCY-DEV/incy-link-encoder).

### Application behavior on import

| Step | What the client does |
| --- | --- |
| 1 | The user taps / scans / pastes `incy://crypt1/<payload>` |
| 2 | The client decodes the payload, recovers the `url` |
| 3 | The import confirmation dialog opens (like for `://add/`), the subscription URL is **hidden** behind `••••` so it does not "leak" in a screenshot |
| 4 | If the payload has `n` — it is shown as the provider name in this dialog and prefilled into the "Name" field |
| 5 | After confirmation — the usual subscription import flow |
| 6 | The internal `importedViaCrypt1=true` flag is stored on the created subscription. On a subsequent Share/Copy/QR the client emits crypt1 **again**, without exposing the URL |

### Preserving the wire format when sharing

When **Share** / **Copy URL** / **Show QR** is pressed on a subscription card, the client emits the same format the subscription was added in:

- Added via `https://...` → Share emits `https://...`
- Added via `incy://crypt1/...` → Share emits `incy://crypt1/...`

This guarantees the obfuscation is not lost along the forwarding chain: if a provider originally published a crypt1 link, all forwards of its copy in Telegram chats stay crypt1.

### Compatibility

| INCY version | Support |
| --- | --- |
| iOS / Android / Desktop ≥ June 2026 | Yes, native `incy://crypt1/` handler |
| Older versions | The link does not open — the user needs to update |
| Third-party VPN clients (V2Box, Shadowrocket, Happ) | Not supported, the scheme is registered for INCY only |

### crypt1 examples

#### Simple link

```text
incy://crypt1/FZEVXuV39UEX1yHB3nkrgdPdrJ3syVxcQm_Y-lY0oKWAT5yRn00xe6ohg06aVWjWRrGJ7BAeEzuoFzv8XBosLnqnqqCMbnAJmR7EN2hII4Yyql1FtWlLlLs
```

#### With provider branding in the QR code

A QR code generated from a crypt1 link with the `n` field, when scanned in INCY, shows the user "MyProvider VPN — Confirm import?" — the provider is branded in the confirmation dialog without a server round-trip.
