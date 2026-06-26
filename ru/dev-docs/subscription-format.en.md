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
| SOCKS5 | `socks://` | Proxying via SOCKS5 |
| WireGuard | `wireguard://` | WireGuard tunneling |

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
| `profile-web-page-url` | URL | Provider website link. Alternative: `homepage` |
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

> A full description of `premium-url`, `hide-url`, and banners (including display conditions and the "header → panel" priority) is in [App management](app-management.md).

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
