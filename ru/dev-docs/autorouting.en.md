# Autorouting

An extension of the [routing](routing.md) functionality that lets you bind a profile to a remote URL source. The profile is downloaded and updated automatically on a schedule.

## Difference from Routing

| | Routing | Autorouting |
|---|---|---|
| Data | Base64 profile passed once | URL source, the profile is downloaded from it |
| Updates | Only when the subscription is updated | Automatically on an interval (default 24h) |
| `sourceURL` | Not set | Set — the profile is bound to a URL |
| Indicator | None | Cloud icon in the profile list |

Geo files have a separate schedule: `routing-geo-update-interval` or the user's choice in the profile editor. Autorouting refreshes the **profile JSON**; this geo interval checks the **existing GeoIP/GeoSite URLs**, even if the profile itself has not changed. See [geo auto-update and retries](routing.md#geo-auto-update).

## Link types

| Link format | Description |
|---|---|
| `://autorouting/onadd/{url}` | Downloads the profile from the URL, sets up auto-updates, and activates it |
| `://autorouting/add/{url}` | Downloads the profile from the URL and sets up auto-updates |

> **Important:** `://routing/onadd/{url}` is **not** autorouting — it is a one-time import without auto-updates. Only the `://autorouting/` scheme sets `sourceURL` and enables auto-updates.

> `{url}` is a direct link to the profile JSON file (starting with `http://` or `https://`).

### Type detection

The type is determined **by the link scheme**:

- `://autorouting/` → **autorouting** (`sourceURL` is set, auto-updates enabled)
- `://routing/` → **routing** (one-time import, no `sourceURL`, no auto-updates)

Examples:
```text
://autorouting/onadd/https://example.com/profile.json   → autorouting (auto-updates)
://routing/onadd/https://example.com/profile.json        → routing (one-time import)
://routing/onadd/ewogICJOYW1lIjogIlRlc3QiCn0=          → routing (base64)
```

## HTTP header

The `autorouting` header contains a link in the same format as in the subscription body — that is, **with the `://autorouting/onadd/` scheme**, not a bare URL:

```
HTTP/2 200
autorouting: incy://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

The profile is downloaded when the subscription is updated, stored with a binding to the URL source, and updated periodically.

> **Important:** a value like `autorouting: https://.../profile.json` (without the `://autorouting/onadd/` prefix) **does not work** — the client ignores such a header. The parser looks for the substring `://autorouting/onadd/` or `://autorouting/add/` in the value and takes everything after it.

The scheme before `://` can be anything — the parser only looks at the `://autorouting/…` part. Both forms are equivalent:

```
autorouting: incy://autorouting/onadd/https://example.com/profile.json
autorouting: ://autorouting/onadd/https://example.com/profile.json
```

As in the subscription body, `onadd` activates the profile immediately, `add` only adds it with auto-update.

## Subscription body

The autorouting string is placed in the subscription body alongside server configurations:

```
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

## Source priority

When several routing sources are present, the **first one found** is used:

| Priority | Source | Type |
|---|---|---|
| 1 (highest) | `autorouting` header | Auto-updating |
| 2 | Body — line with a URL | Auto-updating |
| 3 | `routing` header | Static |
| 4 (lowest) | Body — line with base64 | Static |

---

## GitHub URL conversion

Links to files in GitHub repositories are automatically converted from the "blob" format to "raw":

```
https://github.com/user/repo/blob/main/path/profile.json
→
https://raw.githubusercontent.com/user/repo/main/path/profile.json
```

This happens transparently on import and auto-update. You can use regular GitHub links — the application will substitute the correct URL itself.

---

## Content at the URL

The file at the URL may contain:

**1. Nested deep link:**

If the content starts with `incy://` — the application automatically extracts the profile data from the link. This allows hosting `.deeplink` files:

```text
incy://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIKfQ==
```

The application will extract the base64 data and decode the profile.

**2. JSON profile (recommended):**
```json
{
    "Name": "RoscomVPN",
    "GlobalProxy": "true",
    "RemoteDNSType": "DoH",
    "RemoteDNSDomain": "https://cloudflare-dns.com/dns-query",
    "RemoteDNSIP": "1.1.1.1",
    "Geoipurl": "https://example.com/geoip.dat",
    "Geositeurl": "https://example.com/geosite.dat",
    "DirectSites": ["geosite:ru"],
    "DirectIp": ["geoip:ru"],
    "DomainStrategy": "IPIfNonMatch"
}
```

**3. Base64-encoded JSON:**

```text
ewogICAgIk5hbWUiOiAiUm9zY29tVlBOIiwKICAgICJHbG9iYWxQcm94eSI6ICJ0cnVlIgp9
```

The application tries: nested deep link → JSON → base64 (in priority order).

The profile field structure is described in [routing.md](routing.md#profile-structure).

---

## Auto-updates

### Mechanism

- The application checks all profiles with a `sourceURL` every 30 minutes
- If more than `updateInterval` has passed since the last update (`sourceLastUpdated`) — the profile is re-downloaded
- On update the following are preserved: the profile ID, `sourceURL`, `updateInterval`, geo file hashes
- If the geo file URLs changed after the update — the geo files are re-downloaded automatically

### Update intervals

| Value (sec) | Display |
|---|---|
| `43200` | 12 hours |
| `86400` | 24 hours **(default)** |
| `259200` | 3 days |
| `604800` | 7 days |

### UI management

Profiles with a `sourceURL` show a cloud icon in the list. The profile editor has an "Update source" section:

- **URL** — you can view and change the source URL
- **Update frequency** — choose the update interval
- **Updated** — the time of the last update
- **Update now** — manually update the profile
- **Remove source** — unbind the profile from the URL (turns it into a static one)

---

## Updating existing profiles

- Profiles with the same `Name` are updated, not duplicated
- When an auto-updating profile is updated, the following are preserved: `sourceURL`, `updateInterval`, geo file hashes
- If the geo file URLs (`Geoipurl`, `Geositeurl`) changed — the geo files are re-downloaded automatically
