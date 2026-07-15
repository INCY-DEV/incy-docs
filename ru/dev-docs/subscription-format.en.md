# Subscription format

Description of subscription formats, supported protocols, and HTTP headers.

## Supported protocols

| Protocol | Scheme | Description |
|---|---|---|
| VLESS | `vless://` | Primary protocol |
| VMess | `vmess://` | JSON-based configuration in base64 |
| Trojan | `trojan://` | Password authentication |
| Shadowsocks | `ss://` | SIP002 and modern format |
| Hysteria2 | `hysteria2://`, `hy2://` | Multi-port support |
| SOCKS5 | `socks://`, `socks5://` | Proxying via SOCKS5 |
| HTTP proxy | `http://user:pass@host:port` | HTTP proxy (must contain `@` — otherwise the line is treated as a subscription URL) |
| WireGuard | `wireguard://`, `wg://` | WireGuard tunneling |
| AmneziaWG | `amneziawg://`, `awg://`, `.conf` in the body | Obfuscated WireGuard. A single `.conf` or several servers in one subscription — see the "AmneziaWG / WireGuard .conf in the body" section below |

> The schemes `ssr://`, `tuic://`, `hysteria://` are recognized by the app but **not parsed** — servers with these schemes will be skipped.

## Subscription body formats

### 1. Base64-encoded links

The most common format. The response body is base64, and when decoded contains links, one per line:

```
base64(
  vless://uuid@server1:443?security=tls#Server1
  vless://uuid@server2:443?security=tls#Server2
)
```

URL-safe Base64 is supported (`-` → `+`, `_` → `/`).

### 2. Plain links (plain text)

Links in plain form, one per line:

```
vless://uuid@server1:443?security=tls#Server1
vmess://eyJhZGQiOiJzZXJ2ZXIyIn0=
trojan://password@server3:443#Server3
socks://user:pass@server4:1080#Server4
wireguard://secretKey@server5:51820?publickey=KEY&address=10.0.0.2#Server5
amneziawg://<base64url-conf>#Server6
```

### 3. JSON formats

**Array of full xray configs:**
```json
[
    { "outbounds": [...], "routing": {...} },
    { "outbounds": [...], "routing": {...} }
]
```

**Full xray config** (single object with `inbounds` and `outbounds`):
```json
{
    "inbounds": [...],
    "outbounds": [...],
    "routing": {...},
    "dns": {...}
}
```

Read more: [full-xray-config.md](full-xray-config.md).

### 4. Mixed format

Server links + routing strings + metadata in a single body:

```text
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://autorouting/onadd/https://example.com/routing.json
#announce: Scheduled maintenance tomorrow
```

**Supported special strings in the body:**

| Pattern | Description |
|---|---|
| `://autorouting/onadd/{url}` | Auto-updated routing profile (URL, with `sourceURL`) |
| `://autorouting/onadd/{base64}` | Inline routing profile (base64) |
| `://autorouting/add/{url}` | Auto-updated routing profile (URL, with `sourceURL`) |
| `://routing/onadd/{url}` | One-time profile import by URL (no auto-update) |
| `://routing/onadd/{base64}` | Static routing profile |
| `://routing/add/{base64}` | Static routing profile |
| `://onadd/{url or base64}` | Short form (no auto-update) |
| `://routing/{base64}` | Short form |
| `#announce: text` | Announcement (supports `base64:...`) |
| `#profile-title: text` | Subscription name (supports `base64:...`) |
| `#support-url: URL` | Support link |
| `#profile-web-page-url: URL` | Provider website link |
| `#announce-url: URL` | Announcement link |
| `#profile-update-interval: number` | Update interval (hours) |

Special strings are extracted from the body and do not appear in the server list.

> **Priority:** values from HTTP headers take precedence over values from the body. Inline metadata in the body is used as a fallback when the corresponding header is absent.

### 5. AmneziaWG / WireGuard .conf in the body

The subscription body can be a **raw WireGuard or AmneziaWG `.conf` file** (a multi-line INI with `[Interface]` and `[Peer]` sections). The app recognizes it by the presence of `[Interface]` + `PrivateKey` and routes it to the same parser used for file import / paste. AmneziaWG is detected by its obfuscation parameters (`Jc`, `Jmin`, `Jmax`, `S1`–`S4`, `H1`–`H4`, `I1`–`I5`).

```ini
[Interface]
PrivateKey = <base64>
Address = 10.8.0.2/32
DNS = 1.1.1.1
Jc = 4
Jmin = 40
Jmax = 70
S1 = 86
S2 = 574
H1 = 1234567890

[Peer]
PublicKey = <base64>
PresharedKey = <base64>
AllowedIPs = 0.0.0.0/0
Endpoint = server.example.com:51820
```

The body may be plain text or base64-wrapped. The same payload can be delivered via the deep link `incy://import/{base64-conf}` — see [deep-links.md](deep-links.md).

> A raw `.conf` in the body is parsed as a **single** server entry; the AmneziaWG obfuscation is applied by the engine at connect time (the client stores the `.conf` verbatim).

#### Multiple AmneziaWG servers in one subscription

> **iOS and Android only.** The Desktop client does not support AmneziaWG — a `.conf` in the body is parsed there as plain WireGuard, and the `amneziawg://`/`awg://` schemes and the JSON container are ignored.

A single `.conf` = one server. To deliver several AmneziaWG locations in one subscription, use one of two formats. In both, each `.conf` is encoded as **url-safe base64** (`-`→`+`, `_`→`/`, padding optional), and the server name comes from the `#` fragment or the `name` field.

**Format 1 — line-per-server (`amneziawg://` / `awg://`).** One link per line; can be mixed with `vless://` and other protocols in the same body:

```
amneziawg://<base64url-conf>#Germany
awg://<base64url-conf>#Netherlands
```

`amneziawg://` is canonical, `awg://` is a short alias (equivalent). Everything after `#` is the display name.

**Format 2 — JSON container.** The body is a JSON object with `type: "amneziawg"`:

```json
{
  "type": "amneziawg",
  "version": 1,
  "servers": [
    { "name": "Germany",     "config": "<base64url-conf>" },
    { "name": "Netherlands", "config": "<base64url-conf>" }
  ]
}
```

Each `servers[]` entry → a separate server. `name` is optional (when absent, the name is taken from the `# Name=` comment inside the `.conf` or from the `Endpoint` host). The `version` field is reserved and is not currently validated.

> **Behavior in both formats:** a malformed base64 entry is **skipped** — the other servers still load (one bad location does not break the whole subscription). Duplicates with an identical `.conf` collapse into a single server. On a subscription refresh, servers are added/updated/removed without duplication. HTTP headers stay at the subscription level (shared by all servers).

---

## HTTP headers

### Subscription headers

| Header | Type | Description |
|---|---|---|
| `profile-title` | string | Subscription name (up to 25 characters). Supports base64 |
| `subscription-name` | string | Alternative to `profile-title` (fallback) |
| `profile-description` | string | Subscription description. Supports base64 |
| `profile-update-interval` | int | Update interval in hours |
| `subscription-userinfo` | string | Traffic statistics and expiration |
| `support-url` | URL | Support link |
| `support-email` | email | Support email — shows an "Email" button in the subscription card. Without the header the button is not shown |
| `profile-web-page-url` | URL | Provider website link. Alternative: `homepage` |
| `homepage` | URL | Fallback for `profile-web-page-url` |
| `announce-url` | URL | Announcement link |
| `announce` | string | Announcement text (up to 200 characters). Supports base64 |
| `autorouting` | URL | URL source of a routing profile with auto-update |
| `routing` | string | Routing profile (base64 or full link) |
| `sort-order` | string | Server sort order: `ping`, `name`, `none` |
| `content-disposition` | string | Fallback for the subscription name (`.txt`, `.yaml` extensions are stripped) |
| `premium-url` | URL | Link for the "Premium" button in the subscription card |
| `hide-url` | `1`/`0`/`true`/`false` | Hide the subscription URL from Share/Copy/QR/backup |
| `banner-text` | string | Banner text (base64). Overrides the panel |
| `banner-button-text` | string | Banner button text |
| `banner-button-url` | URL | Banner button link |
| `banner-bg-color` | hex | Banner background color (`#RRGGBB`) |
| `banner-button-color` | hex | Banner button color (`#RRGGBB`) |
| `fragmentation-enable` | `1`/`0` | TCP fragmentation |
| `fragmentation-length` | `min-max` | Fragment length range |
| `fragmentation-interval` | `min-max` | Delay range between fragments |
| `fragmentation-packets` | `tlshello` / `1-3` / `all` | Which packets to apply to |
| `noises-enable` | `1`/`0` | Send noise packets before the handshake |
| `noises-type` | `rand` / `str` / `hex` | Noise content type |
| `noises-packet` | string | Noise payload (format depends on `type`) |
| `noises-delay` | `min-max` ms | Delay range between noises |
| `server-address-resolve-enable` | `1`/`0` | Pre-resolve the server address via DoH |
| `server-address-resolve-dns-domain` | URL | DoH server URL |
| `server-address-resolve-dns-ip` | IP | DoH server IP (bootstrap) |
| `no-limit-enabled` | `1`/`0` | (iOS) Memory-saving Network Extension mode (keeps the background process under the iOS 50 MB cap). Only enables |
| `per-app-proxy-enable` | `1`/`0` | (Android only) Enable per-app mode |
| `per-app-proxy-mode` | `bypass` / `proxy` | (Android only) Per-app mode |
| `per-app-proxy-list` | CSV / URL | (Android only) List of package names |

> This is a reference of subscription headers. A full description of each (value formats, display conditions, "header → panel" priority, `#`-fragment support in the body) is in [App management](app-management.md), where the summary table is the authoritative source.

### Profile Title

Supports two formats:

**Plain text:**
```
profile-title: My VPN
```

**Base64 with description:**
```
profile-title: base64:TWVNdiBWUE4KV2VsY29tZSB0byBvdXIgc2VydmljZQ==
```

When base64-decoded: the first line is the name, the rest is the description.

### Subscription User Info

```
subscription-userinfo: upload=0;download=1073741824;total=10737418240;expire=1735689600
```

| Field | Type | Description |
|---|---|---|
| `upload` | int | Outbound traffic (bytes) |
| `download` | int | Inbound traffic (bytes) |
| `total` | int | Traffic limit (bytes) |
| `expire` | int | Expiration date (Unix timestamp, seconds) |

> If `expire` > 32000000000 — the value is interpreted as milliseconds and converted to seconds.

**Hiding the traffic block:**

If the server returns `subscription-userinfo: 0`, the traffic block on the home screen is hidden entirely. Use this when traffic statistics are not provided.

### Announce

The announcement text is shown on the home screen as a banner. Up to **5 lines** of text are supported, after which the text is truncated with an ellipsis.

```
announce: Server update on March 15
```

```
announce: base64:0J7QsdC90L7QstC70LXQvdC40LUg0YHQtdGA0LLQtdGA0L7Qsg==
```

### Sort Order

Sets the server sort order in the app. When the subscription is refreshed, the value is applied to the global sort setting.

```
sort-order: ping
```

| Value | Description |
|---|---|
| `none` | Default order (as in the subscription) |
| `ping` | By ping (fastest first) |
| `name` | Alphabetical |

---

## Request headers (client → server)

When refreshing a subscription, the app sends:

| Header | Description |
|---|---|
| `User-Agent` | `INCY/<version>/<platform>` |
| `Accept` | `*/*` |
| `Accept-Language` | Device language tag (e.g. `ru-RU`) |
| `Accept-Encoding` | iOS only: `gzip, deflate, br` |
| `x-app-version` | App version |
| `x-device-locale` | Device language |
| `x-client` | `INCY` |

When HWID sending is enabled, additionally:

| Header | Description |
|---|---|
| `x-hwid` | Hardware identifier ([read more](hwid.md)) |
| `X-Device-ID` | Alias for `x-hwid` on Android (some server stacks expect exactly this header) |
| `x-device-os` | Platform (`iOS`, `Android`, `Linux`, `Windows`) |
| `x-ver-os` | OS version |
| `x-device-model` | Device model |

> All HTTP headers are case-insensitive. The server can look at `x-hwid` or `X-HWID` — the same bytes will arrive.

---

## Fallback hosts

If the primary subscription host is unavailable (network/timeout/5xx/429), the client cycles through fallback hosts — the same path and token, only the host changes. On `404`/`410` (the provider deleted the subscription) no cycling happens. The fallback host list does not arrive via a header — it comes in the premium-config body (`settings.fallbackHosts`) — see [premium-api.md](premium-api.md).
