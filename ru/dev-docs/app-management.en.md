# App Management

Parameters for controlling app behavior via subscription HTTP headers and lines in the response body.

## Delivery Methods

All parameters can be delivered in two ways:

**1. HTTP header:**
```
HTTP/2 200
profile-title: Мой VPN
support-url: https://t.me/support
```

**2. Line in the subscription body (a `#` comment):**
```
#profile-title: Мой VPN
#support-url: https://t.me/support
#profile-update-interval: 6
#announce: Текст объявления
vless://...
```

> **Priority:** HTTP headers take precedence. Body lines are used as a fallback when the corresponding header is absent. This is especially useful when serving subscriptions via static files (nginx), where custom HTTP headers cannot be set.

---

## Standard Parameters

### Subscription Name

The subscription profile name. Maximum 25 characters. Can be passed as text or base64 (UTF-8).

**Header:**
```
profile-title: Мой VPN
```

**In the subscription body:**
```
#profile-title: Мой VPN
```

**Base64 with a description** (the first line is the name, the rest is the description):
```
profile-title: base64:0JzQvtC5IFZQTgrQlNC+0LHRgNC+INC/0L7QttCw0LvQvtCy0LDRgtGM
```

**Alternative headers** (fallback when `profile-title` is absent):
- `subscription-name` — alternative subscription name
- `content-disposition` — file name from the header (extensions `.txt`, `.yaml`, `.yml` are stripped automatically)

### Subscription Description

A separate header for the description if it is not included in `profile-title`:

```
profile-description: Быстрые серверы в Европе
```

Supports base64: `profile-description: base64:...`

### Subscription Update Interval

The automatic subscription update interval in hours. The value must be a multiple of one hour.

**Header:**

```
profile-update-interval: 6
```

**In the subscription body:**

```
#profile-update-interval: 6
```

### Subscription Status

Information about the balance, the amount of traffic used, and the subscription expiration date. Fields are separated by semicolons.

```
subscription-userinfo: upload=0;download=1073741824;total=10737418240;expire=1700000000
```

| Field | Description |
|---|---|
| `upload` | Outgoing traffic (bytes) |
| `download` | Incoming traffic (bytes) |
| `total` | Traffic limit (bytes) |
| `expire` | Expiration date (Unix timestamp, seconds) |

> If `expire` > 32,000,000,000, the value is interpreted as milliseconds and converted to seconds.

### Support Link

A button to open the support page. If the link points to Telegram, the Telegram icon is shown.

**Header:**

```
support-url: https://t.me/your_support_bot
```

**In the subscription body:**

```
#support-url: https://t.me/your_support_bot
```

### Website Link

A button to open the subscription website.

**Header:**

```
profile-web-page-url: https://your-site.com
```

**In the subscription body:**

```
#profile-web-page-url: https://your-site.com
```

Alternative header: `homepage`

### Announcement

A text announcement (up to 200 characters). Can be passed as text or base64.

**Header:**
```
announce: Плановое обслуживание 15 марта с 03:00 до 05:00 MSK
```

**Base64:**
```
announce: base64:0J/Qu9Cw0L3QvtCy0L7QtSDQvtCx0YHQu9GD0LbQuNCy0LDQvdC40LU=
```

**Announcement URL** (a link, not text):

```
announce-url: https://example.com/news
```

**In the subscription body:**

```
#announce: Плановое обслуживание 15 марта
#announce-url: https://example.com/news
vless://uuid@server:443#Server
```

---

## Parameter Summary Table

| Header | Alternatives | Format | Body (`#`) | Description |
| --- | --- | --- | --- | --- |
| `profile-title` | `subscription-name`, `content-disposition` | text / `base64:...` | ✅ | Subscription name |
| `profile-description` | — | text / `base64:...` | — | Subscription description |
| `profile-update-interval` | — | number (hours) | ✅ | Update interval |
| `subscription-userinfo` | — | `key=value;...` | — | Traffic statistics |
| `support-url` | — | URL | ✅ | Support link |
| `profile-web-page-url` | `homepage` | URL | ✅ | Website link |
| `announce` | — | text / `base64:...` | ✅ | Announcement text |
| `announce-url` | — | URL | ✅ | Announcement link |
| `autorouting` | — | URL | ✅ | Auto-updated routing profile |
| `routing` | — | base64 / link | ✅ | Static routing profile |
| `premium-url` | — | URL | — | "Premium" link (in the subscription card, see below) |
| `banner-text` | — | text / `base64:...` | — | Banner text (overrides the panel, see below) |
| `banner-button-text` | — | text | — | Banner button text |
| `banner-button-url` | — | URL | — | Banner button link |
| `banner-bg-color` | — | hex (`#RRGGBB`) | — | Banner background color |
| `banner-button-color` | — | hex (`#RRGGBB`) | — | Banner button color |
| `hide-url` | — | `1` / `0` / `true` / `false` | ✅ | Hide the subscription URL from Share/Copy/QR/backup (see below) |
| `per-app-proxy-enable` | — | `1` / `0` | — | Enable per-app mode (Android only) |
| `per-app-proxy-mode` | — | `bypass` / `proxy` | — | Per-app mode |
| `per-app-proxy-list` | — | CSV / URL | — | List of package names |
| `fragmentation-enable` | — | `1` / `0` | — | TCP fragmentation |
| `fragmentation-length` | — | `min-max` | — | Fragment length range |
| `fragmentation-interval` | — | `min-max` | — | Range of delay between fragments |
| `fragmentation-packets` | — | `tlshello` / `1-3` / `all` | — | Which packets to apply to |
| `noises-enable` | — | `1` / `0` | — | Send noise packets before the handshake |
| `noises-type` | — | `rand` / `str` / `hex` | — | Noise content type |
| `noises-packet` | — | string | — | Noise payload (format depends on `type`) |
| `noises-delay` | — | `min-max` ms | — | Range of delay between noise packets |
| `server-address-resolve-enable` | — | `1` / `0` | — | Pre-resolve the server address via DoH |
| `server-address-resolve-dns-domain` | — | URL | — | DoH server URL |
| `server-address-resolve-dns-ip` | — | IP | — | DoH server IP (bootstrap) |

> All headers are case-insensitive (`profile-title` = `Profile-Title`).
>
> Body parameters are used as a fallback — HTTP headers always take precedence.
>
> All headers with values support the `base64:` prefix for passing UTF-8 data without Latin-1 / non-ASCII issues (applies to `announce`, `profile-title`, `profile-description`, `per-app-proxy-list`).

---

## Routing

### Routing Profile

A static profile in base64. See [routing.md](routing.md) for details.

```
routing: ://routing/onadd/ewog...base64...
```

### Auto-Updated Routing Profile

A URL source of the routing profile with periodic updates. See [autorouting.md](autorouting.md) for details.

```
autorouting: https://raw.githubusercontent.com/user/repo/main/profile.json
```

### Routing Source Priority

If a routing profile is specified in several places, the **first one found** by priority is used:

| Priority | Source |
|---|---|
| 1 (highest) | `autorouting` header |
| 2 | Body — a line with a URL (`://autorouting/onadd/`, `://autorouting/add/`) |
| 3 | `routing` header |
| 4 (lowest) | Body — a line with base64 (`://routing/onadd/`, `://routing/add/`, `://routing/`) |

> **Important:** only `://autorouting/` sets `sourceURL` and enables auto-update. `://routing/onadd/{url}` lines in the subscription body import the profile once, without binding it to a source.

---

## Server Description

An additional caption displayed under the server name (maximum 30 characters). It is appended after `title` using the `?` separator:

```
vless://uuid@server:443#Сервер1?serverDescription=base64-text
```

---

## Per-App Proxy (Android only)

The Android VpnService allows routing only **selected apps** through the VPN, or conversely **excluding** them from the tunnel. The provider can force this mode via three headers:

```
per-app-proxy-enable: 1
per-app-proxy-mode: bypass
per-app-proxy-list: com.android.chrome,org.telegram.messenger
```

### Parameters

| Header | Value | Description |
| --- | --- | --- |
| `per-app-proxy-enable` | `1` / `0` | Enable per-app mode |
| `per-app-proxy-mode` | `bypass` \| `proxy` | `bypass` — the listed apps **bypass** the VPN. `proxy` — **only** they go through the VPN |
| `per-app-proxy-list` | CSV or URL | List of package names separated by commas, newlines, or a URL to a text file |

### List Format

**Inline (CSV or line-based):**

```
per-app-proxy-list: com.android.chrome,org.telegram.messenger,com.google.android.youtube
```

**Base64 (for long lists):**

```
per-app-proxy-list: base64:Y29tLmFuZHJvaWQuY2hyb21lCm9yZy50ZWxlZ3JhbS5tZXNzZW5nZXI=
```

**Remote URL:**

```
per-app-proxy-list: https://example.com/myapps.txt
```

The file at the URL is plain text with package names, one per line or comma-separated. The client downloads it when applying the subscription and on every update.

### Behavior

- If none of the three fields is set, the user's settings in the app are **not overridden**.
- If `per-app-proxy-enable` is set to `0`, per-app mode is disabled even if the user enabled it locally.
- Platforms other than Android **ignore** these headers.

---

## TCP Fragmentation

Overrides the user's global fragmentation settings for this subscription.

```
fragmentation-enable: 1
fragmentation-packets: tlshello
fragmentation-length: 10-30
fragmentation-interval: 10-30
```

| Header | Value | Description |
| --- | --- | --- |
| `fragmentation-enable` | `1` / `0` | Enable fragmentation |
| `fragmentation-packets` | `tlshello` \| `1-3` \| `1` \| `all` | Which TCP packets to apply fragmentation to |
| `fragmentation-length` | `min-max` | Fragment length range in bytes |
| `fragmentation-interval` | `min-max` | Range of delay between fragments in ms |

The same parameters are available through the [Premium API](premium-api.md#domain-fronting-and-fragmentation) as `fragmentEnabled / fragmentPackets / fragmentLength / fragmentInterval` — for a Premium subscription, HTTP headers are ignored in favor of API values.

---

## Noise Packets (noises)

Sending random UDP packets before the VPN handshake for obfuscation. Primarily relevant for WireGuard and Hysteria2 on networks with deep packet inspection.

```
noises-enable: 1
noises-type: rand
noises-packet: 10-20
noises-delay: 10-50
```

| Header | Value | Description |
| --- | --- | --- |
| `noises-enable` | `1` / `0` | Enable noise |
| `noises-type` | `rand` \| `str` \| `hex` | Payload format |
| `noises-packet` | string | Noise packet content; for `rand` — a length range `min-max` |
| `noises-delay` | `min-max` ms | Range of delay between noise packets |

---

## Resolving the Server Address via DoH

Bootstrap resolution of the server domain via DNS-over-HTTPS before the tunnel is established. Useful when the provider's DNS spoofs the VPN server address.

```
server-address-resolve-enable: 1
server-address-resolve-dns-domain: https://common.dot.dns.yandex.net/dns-query
server-address-resolve-dns-ip: 77.88.8.8
```

| Header | Value | Description |
| --- | --- | --- |
| `server-address-resolve-enable` | `1` / `0` | Enable DoH resolution |
| `server-address-resolve-dns-domain` | URL | DoH endpoint (usually `/dns-query`) |
| `server-address-resolve-dns-ip` | IP | The DoH server IP for bootstrap — used before its domain is resolved |

The same fields are passed through the Premium API as `serverAddressResolveEnable` / `serverAddressResolveDnsDomain` / `serverAddressResolveDnsIp`.

---

## "Premium" Link

An additional button in the subscription card — it leads to the provider's purchase page or account dashboard.

```
premium-url: https://example.com/pricing
```

| Header | Value | Description |
| --- | --- | --- |
| `premium-url` | URL | URL of the "Premium" button in the subscription card |

If not set, the button is hidden.

---

## Provider Banner

The banner is a prominent strip in the subscription card on the home screen (text + an optional button). It is configured in the premium panel, but the text and button can be **overridden via subscription headers** — convenient for dynamic announcements without opening the panel.

### Display Conditions

The banner is shown only when **both** conditions are met:

1. The provider is **premium** (an active premium subscription).
2. The banner is **enabled in the premium panel** (`bannerEnabled`).

The headers themselves do NOT enable the banner — that is only done in the panel. The headers only set/override the content.

### Priority: Header → Panel

Each field is resolved as `header ?? panel`: if the corresponding `banner-*` header came in the subscription response, it is used; otherwise the value from the panel is used.

```
banner-text: base64:0JDQutGG0LjRjyEg0KHQutC40LTQutCwIDUw0Js=
banner-button-text: Подробнее
banner-button-url: https://example.com/promo
banner-bg-color: #E53E3E
banner-button-color: #38A169
```

| Header | Format | Overrides (panel) |
| --- | --- | --- |
| `banner-text` | text / `base64:...` | `bannerText` |
| `banner-button-text` | text | `bannerButtonText` |
| `banner-button-url` | URL | `bannerButtonUrl` |
| `banner-bg-color` | hex `#RRGGBB` | `bannerBgColor` |
| `banner-button-color` | hex `#RRGGBB` | `bannerButtonColor` |

> The button URL is resolved as `premium-url` → `banner-button-url` → panel: the `premium-url` header has the highest priority (historically).
>
> If `banner-text` is empty after resolution, the banner is not shown, even when it is enabled in the panel.
>
> Supported on iOS, Android, and Desktop.

---

## Hiding the Subscription URL from the User

The `hide-url` parameter prevents the subscription URL from "leaking" off the device: when enabled, the app **does not show or allow exporting** the URL via Share, Copy URL, QR code, or backups. The subscription name, servers, and all the rest of the UX work as usual — only the URL itself is hidden.

**Header:**

```
hide-url: 1
```

**In the subscription body:**

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

### Accepted Values

| What is sent | Behavior |
| --- | --- |
| `1`, `true`, `yes` (case-insensitive) | URL is hidden |
| `0`, `false`, `no`, empty string | URL is visible (default) |
| Any other value in the header | Ignored, URL is visible |

### Source Priority

1. The `hide-url` HTTP header has the highest priority
2. The `#hide-url:` line in the subscription body is used as a fallback when the header is absent
3. The `hide_url` field in the Premium API JSON is an independent source applied in parallel

> If at least one source says "hide", the URL is hidden. To unhide it, disable it in **all** sources (or refresh the subscription with the updated value).

### What Is Blocked

- The **Share** button in the subscription card
- The **Copy URL** button
- Displaying the subscription **QR code**
- Including the subscription in a **backup** (even a password-encrypted one)
- The export button in the subscription's server editor

### What Is NOT Blocked

- Viewing and editing the server settings within the subscription (on devices with an **admin HWID** — see [admin-hwids.md](admin-hwids.md))
- Connecting to servers, ping, traffic stats, refreshing the subscription
- Backups of **individual servers** (if they were imported manually, outside this subscription)

### Rules for Premium Providers

| Premium | Admin HWID | `hide-url` | Sees URL | URL in backup |
| --- | --- | --- | --- | --- |
| no | — | no | yes | yes |
| no | — | yes | no | no |
| yes | yes | no | yes | yes |
| yes | yes | yes | yes | **no** (admin sees it, but cannot export via backup) |
| yes | no | — | no | no |

Without `hide-url`, regular (non-premium) subscriptions are always exported and copied — `hide-url` is the **only** way to forbid this for non-premium.

---

## Settings the Subscription **Cannot** Set via HTTP Headers

These parameters are stored in the provider's [Premium API](premium-api.md) configuration and are applied by the client only if the subscription domain belongs to a Premium provider. They cannot be enabled "via a subscription without an account in the panel" — this is by design.

| Group                | What is configured                                                                 | Link                                                   |
|-----------------------|-----------------------------------------------------------------------------------|----------------------------------------------------------|
| Lite Mode             | Simplified interface, links to bot/channel/support + [preset icons](icon-presets.md) | [premium-api.md § Lite Mode](premium-api.md#lite-mode)          |
| Subscription banner       | Text + colors + button in the subscription card                                        | [premium-api.md § Баннер подписки](premium-api.md#subscription-banner) |
| Custom theme        | Flat colors and gradients for the account / background                                     | [premium-api.md § Кастомная тема](premium-api.md#custom-theme-theme) |
| Force settings       | `forceConnectionStyle`: classic round button vs compact toggle             | [premium-api.md § Принудительные настройки](premium-api.md#forced-settings) |
| Ping and sorting     | `defaultPingProtocol`, `defaultSortOrder`, `pingOnUpdate`                         | [premium-api.md § Ping и сортировка](premium-api.md#ping-and-sorting) |
| Domain fronting       | `resolveAddress` / `hostHeader` (the SNI ↔ Host pairing for obfuscation)                | [premium-api.md § Domain fronting и фрагментация](premium-api.md#domain-fronting-and-fragmentation) |
| Admin access by HWID  | `adminHwids` + push auto-approve                                                  | [admin-hwids.md](admin-hwids.md)                         |
| Push notifications      | Moderation, targeting, cancellation                                                      | [provider-notifications.md](provider-notifications.md)   |

> **Fragmentation, noise, and DoH resolution** are available through **both** channels: subscription HTTP headers (see above) or the Premium API. For a Premium subscription, API values take precedence over headers.
