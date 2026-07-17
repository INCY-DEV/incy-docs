# Premium API

Subscription management system with encryption based on domain hashes. Lets providers customize the app appearance, server parameters, and notifications for their users.

## Overview

When a subscription is added, the app extracts the domain from the URL and requests the provider configuration through the encrypted API. The domain is never transmitted in plaintext — a SHA-256 hash is used.

---

## API

### Endpoint

```
GET /api/subscription/config?h=<sha256hex>&hwid=<sha256hex>
```

### Request

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `h` | string | yes | SHA-256 hash of the domain (64 hex characters) |
| `hwid` | string | no | SHA-256 hash of the device HWID (64 hex characters). Used to check the device limit |

The hash is computed from the lowercased domain:

```
SHA256("example.com") → "a379a6f6eeafb9a55e378c118034e2751e682fab9f2d30ab13d2125586ce1947"
```

### Response

The server always returns an encrypted response:

```json
{
    "encrypted": true,
    "iv": "<base64>",
    "data": "<base64>",
    "tag": "<base64>"
}
```

### Response fields (after decryption)

| Field | Type | Description |
| --- | --- | --- |
| `success` | boolean | Whether the request succeeded |
| `domain` | string | Subscription domain |
| `isPremium` | boolean | Whether the provider has Premium active |
| `deviceLimitExceeded` | boolean | The provider's device limit is exceeded (see [Device limits](#device-limits)) |
| `logoUrl` | string? | URL of the provider logo |
| `settings` | object | Provider settings (see below) |
| `theme` | object | Custom theme (see below) |

### Rate Limit

30 requests per minute per IP address. When exceeded — a `429` response.

---

## Encryption

API responses are encrypted with the AES-256-GCM algorithm. The encryption key is derived from the domain — only a client that knows the original domain and combination can decrypt the response.

Response components:

| Field | Description |
|---|---|
| `iv` | Initialization vector (base64, 12 bytes) |
| `data` | Encrypted data (base64) |
| `tag` | Authentication tag (base64, 16 bytes) |

> Key derivation details and the encryption implementation are internal and are not published.

---

## Configuration structure

### Provider settings (`settings`)

#### Basic

| Field | Type | Description |
|---|---|---|
| `serverDescription` | string | Server description (up to 30 characters) |
| `alwaysHwidEnable` | boolean | Force sending the HWID (the user cannot disable it) |
| `expiryNotifications` | boolean | Local notifications about subscription expiry |
| `showServerDescription` | boolean | Show server descriptions. Defaults to `true` |

#### Domain fronting and fragmentation

| Field | Type | Description |
|---|---|---|
| `resolveAddress` | string | IP for domain fronting |
| `hostHeader` | string | Host header for domain fronting |
| `fragmentEnabled` | boolean | TCP fragmentation in hev-socks5-tunnel |
| `fragmentLength` | string | Fragment length range (e.g. `"10-30"`) |
| `fragmentInterval` | string | Interval range (e.g. `"20-40"` ms) |
| `fragmentPackets` | string | Number of fragments (e.g. `"5-10"`) |

#### DNS resolution of the server address (DoH)

| Field | Type | Description |
|---|---|---|
| `serverAddressResolveEnable` | boolean | Pre-resolve the server address via DoH |
| `serverAddressResolveDnsDomain` | string | DoH server URL (e.g. `https://common.dot.dns.yandex.net/dns-query`) |
| `serverAddressResolveDnsIp` | string | DoH server IP (used before its domain is resolved) |

#### Lite Mode

A simplified interface with links to the bot, channel, support, and (optionally) premium. More about icons — [icon-presets.md](icon-presets.md).

| Field | Type | Description |
|---|---|---|
| `liteMode` | boolean | Enable the simplified mode |
| `botUrl` | string? | Link to the Telegram bot |
| `channelUrl` | string? | Link to the Telegram channel |
| `supportUrl` | string? | Link to support |
| `botIconKey` | string? | Bot icon key from the preset set (see [icon-presets.md](icon-presets.md)) |
| `channelIconKey` | string? | Channel icon key |
| `supportIconKey` | string? | Support icon key |

> `null` or an unknown key → the client uses the default icon (`send` for the bot, `megaphone` for the channel, `help` for support).

#### Admin access (admin HWIDs)

Devices in the `adminHwids` list can:

- View and edit server configs directly in the app.
- Send provider notifications **without moderation** (auto-approve when matching `targetSegment.hwid`).

Details — [admin-hwids.md](admin-hwids.md).

| Field        | Type       | Description                             |
|--------------|------------|-----------------------------------------|
| `adminHwids` | `string[]` | List of HWIDs of devices with admin rights |

#### Subscription banner

A red / arbitrary-color banner inside the subscription card. Used for upsell / expiry warnings / announcements.

| Field | Type | Description |
|---|---|---|
| `bannerEnabled` | boolean | Show the banner |
| `bannerText` | string? | Banner text (white on `bannerBgColor`) |
| `bannerButtonText` | string? | Button text (if empty — the button is hidden) |
| `bannerButtonUrl` | string? | Button URL |
| `bannerBgColor` | string? | Banner background color (hex, e.g. `"#E53E3E"`, defaults to red) |
| `bannerButtonColor` | string? | Button color (hex, defaults to green) |

#### Forced settings

Override the user's choice in the app settings while the subscription is active.

| Field                  | Type      | Description                                                                                            |
|------------------------|-----------|-------------------------------------------------------------------------------------------------------|
| `forceConnectionStyle` | `string?` | Connection button style: `"classic"` (large round button) or `"compact"` (narrow toggle at the bottom) |

#### Ping and sorting

Applied on the first connection of a subscription and override the app's default settings.

| Field | Type | Description |
|---|---|---|
| `defaultPingProtocol` | string? | Ping type: `incy`, `tcp`, `proxy_head`, `proxy_get`, `icmp` |
| `pingTestUrl` | string? | URL for HTTP ping (used with `incy` / `proxy_head` / `proxy_get`) |
| `defaultSortOrder` | string? | Server sorting: `none`, `ping`, `name` |
| `defaultPingDisplayFormat` | string? | Ping display style: `time` (numbers, ms), `bars` (bar gauge), `both` (numbers + gauge), or `dots` (green dots — responded/not). The `dots` mode is iOS-only; Android/Desktop show `time`/`bars`/`both` |
| `pingOnUpdate` | boolean? | Auto-ping all servers after a subscription update |

`incy` — **INCY Ping**: a real HTTP GET through the proxy, but the value is divided by ~3.3 so it reads like a familiar ping instead of the full proxied round-trip. The app's default method.

#### Content

| Field | Type | Description |
|---|---|---|
| `announceUrl` | string? | URL for the provider's in-app announcements |
| `webPageUrl` | string? | Link to the provider's web page |

#### Fallback domains (`fallbackHosts`)

| Field | Type | Description |
|---|---|---|
| `fallbackHosts` | string[] | List of fallback hosts. If the main subscription domain does not respond during an update, the client retries the same request, substituting these hosts one by one (only the host changes, the path/token stay the same). They are tried top to bottom. |

> The client caches `fallbackHosts` on the subscription, so the fallback works even when the main domain is completely unreachable. On `404`/`410` (subscription deleted) the fallback is not attempted. In the premium panel it is set via the "Fallback" button next to the domain.

### Custom theme (`theme`)

An extended palette, applied only when the user sees a premium subscription. Supports flat colors and 2-4-stop gradients.

#### Flat colors

| Field | Type | Description |
|---|---|---|
| `enabled` | boolean | Custom theme enabled |
| `darkMode` | boolean | Dark mode |
| `accent` | string | Primary accent color (hex, e.g. `"#FF6B6B"`) |
| `accentSecondary` | string | Secondary accent color |
| `background` | string | Background color |
| `card` | string | Card color |
| `surface` | string | Surface color |
| `textPrimary` | string | Primary text color |
| `textSecondary` | string | Secondary text color |

#### Gradients

If set, overrides the flat `accent`/`accentSecondary` for accent elements and `background` for the background.

| Field | Type | Description |
|---|---|---|
| `accentGradient.stops` | GradientStop[] | 2-4 stops (`{ color, position }`), `position` in the range `0.0..1.0` |
| `accentGradient.angle` | number | Gradient angle in degrees `0..360` |
| `backgroundGradient.enabled` | boolean | Enable a gradient background |
| `backgroundGradient.stops` | GradientStop[] | 2-3 stops |
| `backgroundGradient.angle` | number | Gradient angle |

Each stop:

```json
{ "color": "#B8D94A", "position": 0.0 }
```

---

## Device limits

Premium providers have plans with a limit on the number of devices. The limit is set by the provider's `maxDevices` field.

### How it works

1. The client sends `hwid=SHA256(rawHwid)` in the configuration request
2. The server checks whether a device with this `hwidHash` is registered for this provider's domains
3. If the device is **already registered** — it always gets premium (existing devices are not blocked)
4. If the device is **not registered** — the server counts the provider's total number of devices:
   - If `totalDevices < maxDevices` — premium is granted
   - If `totalDevices >= maxDevices` — `isPremium: false` + `deviceLimitExceeded: true` is returned

### Client behavior on `deviceLimitExceeded: true`

- Premium features are disabled (as with `isPremium: false`)
- The provider's custom theme is not applied
- Premium settings (fragmentation, fronting, etc.) are not used
- The VPN keeps working in basic mode
- The device is registered (but without premium)

### Plans

| Limit | Description |
| --- | --- |
| `1000` | Standard plan |
| `3000` | Medium plan |
| `6000` | Maximum plan |
| `null` | Unlimited (no restrictions) |

---

## Device registration

When a subscription is added, the app registers the device to track active connections and push notifications.

### Registration data

| Field | Type | Description |
| --- | --- | --- |
| `hwid` | string | Device hardware identifier ([more](hwid.md)) |
| `hwidHash` | string | SHA-256 hash of the HWID (for server-side limit checks) |
| `uid` | string | Anonymous device UID |
| `platform` | string | `"android"`, `"ios"`, `"linux"`, `"windows"`, `"macos"` |
| `appVersion` | string | App version |
| `osVersion` | string | OS version |
| `locale` | string | Device language |
| `subscriptionDomainHash` | string | SHA-256 hash of the subscription domain |
| `fcmToken` | string | Push token for notifications (FCM / APNs) |
| `lastActive` | timestamp | Time of last activity |

> The `hwidHash` field is added during registration and is used by the server to check the device limit without knowing the original HWID.

### Subscription synchronization

The server can set the `subscriptionNeedsSync = true` flag on a device. When this flag is detected, the app:

1. Reads the `subscriptionNewDomain` field from the device document
2. Updates the subscription URL to the new domain
3. Clears the `subscriptionNeedsSync` flag

This lets the provider migrate users to a new domain when the old one is blocked.

---

## Caching

- **In-memory cache:** the configuration is kept in memory for the duration of the app session
- **Disk cache:** stored in SecureStorage for offline access
- **Fallback:** on a `503` error the cached configuration is used
- **Cleanup:** the configuration is removed from the cache if the domain is no longer premium

---

## Certificate Pinning

Requests to the Premium API on Android and Desktop are protected by certificate pinning (SHA-256 pins of the TLS certificate). This prevents MITM attacks on the communication channel with the API.
