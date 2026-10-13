# Routing

The application supports configuring traffic routing through routing profiles. The application ships with preinstalled geo files so it works right after installation. Updates happen when the profile is updated or manually.

## Adding profiles

Routing profiles can be added via:

- Clipboard
- Deeplink links
- QR codes
- HTTP headers (`routing`)
- Subscription body

## Link types

| Link format | Description |
|---|---|
| `incy://routing/add/{base64}` | Adds the profile; activates after geo files are downloaded successfully |
| `incy://routing/onadd/{base64}` | Adds and immediately activates the profile |
| `incy://routing/off` | Fully disables built-in routing (no payload) |

> `{base64}` is the JSON profile encoded in base64.

> **`incy://routing/off`** disables built-in routing entirely — equivalent to turning off the routing-profiles toggle in settings: the config is generated with no routing rules. The selected profile is kept (reversible: the provider can re-enable it via `onadd`).

> Backward compatibility: the `://routing/add/` and `://routing/onadd/` links are also supported.

## Error handling

The geo file download manager runs in the background:

- Downloads exceeding 3 minutes are aborted
- Error messages are shown on the main screen
- Problematic profiles are marked with a red exclamation mark in the list
- Problems disappear after files download successfully or the profile is removed

## HTTP header

The profile is passed in the `routing` header in base64 format. Two formats are supported:

**Format 1 — base64 directly:**
```
HTTP/2 200
routing: ewogICJOYW1lIjogIlJvc2NvbVZQTiIs...
```

**Format 2 — full link (any scheme):**
```
HTTP/2 200
routing: ://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIs...
```

**Format 3 — disable routing:**

The value `off` (or the `://routing/off` link) disables built-in routing entirely — the provider turns routing off straight from the subscription response, with no user action:
```
HTTP/2 200
routing: off
```

## Subscription body

The routing string is placed in the subscription body alongside server configurations:

```
vless://uuid@server1:443?security=tls#Server1
vmess://eyJhZGQiOiAic2VydmVyMi...
incy://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIs...
```

## Updating existing profiles

- Profiles with the same `Name` field are updated, not duplicated
- The `LastUpdated` field with a Unix timestamp controls freshness — an update happens when the value is greater than that of the stored profile

---

## Profile structure

### Profile example

```json
{
    "Name": "RoscomVPN",
    "GlobalProxy": "true",
    "RemoteDNSType": "DoH",
    "RemoteDNSDomain": "https://cloudflare-dns.com/dns-query",
    "RemoteDNSIP": "1.1.1.1",
    "DomesticDNSType": "DoH",
    "DomesticDNSDomain": "https://dns.google/dns-query",
    "DomesticDNSIP": "8.8.8.8",
    "Geoipurl": "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat",
    "Geositeurl": "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat",
    "DnsHosts": {
        "cloudflare-dns.com": "1.1.1.1",
        "dns.google": "8.8.8.8"
    },
    "DirectSites": ["geosite:ru"],
    "DirectIp": ["geoip:ru", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16", "224.0.0.0/4", "255.255.255.255"],
    "ProxySites": [],
    "ProxyIp": [],
    "BlockSites": ["geosite:category-ads-all"],
    "BlockIp": [],
    "DomainStrategy": "IPIfNonMatch",
    "FakeDNS": "false"
}
```

### Field descriptions

#### General settings

| Field | Type | Default | Description |
|---|---|---|---|
| `Name` | string | `"Default"` | Profile name |
| `GlobalProxy` | string | `"true"` | `"true"` — all traffic goes through the proxy; `"false"` — direct connection. Defines the behavior when there is no match in the routing rules |
| `LastUpdated` | string | | Unix timestamp. Controls forced geo file updates on first save or when updating the profile with a newer timestamp |

#### DNS settings

The system splits DNS queries into remote (Remote, via proxy) and local (Domestic, direct connection).

**Remote DNS** (for proxied resources):

| Field | Type | Default | Description |
|---|---|---|---|
| `RemoteDNSType` | string | `"DoH"` | Protocol: `DoH`, `DoU` |
| `RemoteDNSDomain` | string | `"https://cloudflare-dns.com/dns-query"` | DNS server address (required for DoH) |
| `RemoteDNSIP` | string | `"1.1.1.1"` | DNS server IP |
| `RemoteDns` | string | | Alternative field for `RemoteDNSIP` (backward compatibility) |

**Local DNS** (for direct resources):

| Field | Type | Default | Description |
|---|---|---|---|
| `DomesticDNSType` | string | `"DoU"` | Protocol: `DoH`, `DoU` |
| `DomesticDNSDomain` | string | `""` | DNS server address (empty by default — `DomesticDNSIP` over UDP is used) |
| `DomesticDNSIP` | string | `"8.8.8.8"` | DNS server IP |
| `DomesticDns` | string | | Alternative field for `DomesticDNSIP` (backward compatibility) |

**Additional DNS settings:**

| Field | Type | Description |
|---|---|---|
| `DnsHosts` | object | Manual DNS records (analogous to a hosts file). Format: `{"domain": "ip"}` |
| `FakeDNS` | string | `"true"` — substitutes virtual IPs instead of real ones so that Xray handles all queries according to the configuration |

#### VPN DNS → Internal versus FakeDNS

These are separate settings. In the Apple client's HEV mode, **Internal**
(`198.18.0.2`) uses `mapdns`: applications receive a virtual IPv4 from
`240.0.0.0/4`, and HEV restores its domain before handing the connection to
Xray. This can happen even with profile `FakeDNS=false`. These addresses
must stay inside the VPN; they are not the provider server's addresses.

Profile `FakeDNS` controls Xray's mechanism. `RemoteDNS` and `DomesticDNS`
select profile resolvers; they do not switch HEV mapdns on or off. Full
subscription JSON may supply its own DNS configuration.

The October 2026 fixes restore Android mapdns and capture its virtual range
when LAN bypass is enabled. Desktop Internal gains an equivalent using
Xray FakeDNS while retaining Xray TUN, upstream resolvers and explicit
provider pools. DNS selection rules may still return real addresses for
specific domains. Stored profiles are unchanged. Availability depends on
the installed build.

For real IPs, select a public VPN DNS preset and disable profile FakeDNS.
Generated configurations still intercept DNS in Xray, retaining the
profile's Remote/Domestic DNS and routing. For full JSON, also check its
own DNS and interception rules. Reconnect and restart the affected browser
to exclude stale DNS cache. A virtual IP alone does not establish the cause
of a JavaScript or WebSocket failure; include DNS results and logs if the
problem persists.

#### Routing rules

Traffic is distributed across three categories:

| Field | Type | Description |
|---|---|---|
| `DirectSites` | string[] | Domains/categories for direct access (no proxy) |
| `DirectIp` | string[] | IP addresses and subnets for direct access |
| `ProxySites` | string[] | Domains/categories routed through the proxy |
| `ProxyIp` | string[] | IP addresses and subnets through the proxy |
| `BlockSites` | string[] | Blocked domains/categories (ads, trackers) |
| `BlockIp` | string[] | Blocked IP addresses and subnets |

Rules support geo categories (`geosite:ru`, `geoip:ru`), specific domains, and IP/CIDR subnets.

#### Geo files

| Field | Type | Description |
|---|---|---|
| `Geoipurl` | string | URL to download `geoip.dat` |
| `Geositeurl` | string | URL to download `geosite.dat` |

#### Routing strategy

The `DomainStrategy` field defines the rule evaluation order (default `AsIs`):

| Value | Description |
|---|---|
| `AsIs` | Domains are passed as is, without DNS resolution (default) |
| `IPIfNonMatch` | Domain check first; if there is no match — DNS resolution and IP rule check |
| `IPOnDemand` | Always resolves domains to IPs before checking the rules |

---

## Geo files: optimized downloading

Geo files (`geoip.dat`, `geosite.dat`) are downloaded from the URLs specified in the profile. A hash check is used to save traffic.

### Algorithm

1. `{filename}.sha256` (a few bytes) is downloaded from the same URL
2. If the hash matches the stored one **and** the file exists locally → the download is skipped (even on a manual update)
3. Without `.sha256`, an ordinary profile import can use `LastUpdated` to skip unchanged data. Manual and scheduled geo refresh bypass this timestamp check.
4. Required files are downloaded into a staging directory. The client computes SHA-256 and verifies it against the sidecar when available. An incomplete HTTP transfer or checksum mismatch fails the update.
5. Only after all required downloads succeed are the live files replaced. Network failures keep the old pair; failure to install the second file triggers rollback of the first.
6. Hashes and the successful-check timestamp are saved after installation. See [failure handling and retries](#geo-update-safety).

### Recommendation for providers

Place a `geoip.dat.sha256` and `geosite.dat.sha256` file next to the geo files. The file must contain only the hex string of the SHA-256 hash (64 characters). This lets clients skip downloading unchanged files and save traffic.

Example contents of `geoip.dat.sha256`:
```
556d4041c378123499c307abc6165ab61eda2a7541f792def3d52c160e2fdd05
```

---

## Trimming geo files (chunk files)

Full geoip/geosite files weigh tens of megabytes. If a profile uses only a limited subset of `geoip:`/`geosite:` tags, the client can trim the downloaded files down to the entries actually needed.

### Profile field

| Field            | Type     | Description                                                                                                            |
|-----------------|---------|---------------------------------------------------------------------------------------------------------------------|
| `useChunkFiles` | boolean | If `true` — the client calls the internal `CutGeoData()` after downloading and keeps only the tags referenced in the rules |

- **By default** `false` on all platforms — backward compatibility with old profiles.
- **Android / iOS** implement trimming via the built-in Go module `incycore.CutGeoData()` (protobuf parsing of geoip/geosite and discarding unneeded entries).
- **Desktop (Linux / Windows)** still uses full files — `useChunkFiles` is ignored; the xray process works with the untrimmed `.dat`.
- After trimming, the hash is recomputed locally and saved in the profile — a re-download will not start until the source `.sha256` on the server changes.

### When to use

Enable it if:

- Few geo tags are used in `proxy` / `direct` / `block` (for example, only `geoip:ru`, `geoip:cn`, `geosite:google`).
- Users complain about memory when loading heavy lists.

Do not enable it if:

- The profile uses many tags — trimming gives no benefit.
- There are custom geosite files with a non-standard layout — the client may not recognize the structure.

## Per-profile geo file auto-update {#geo-auto-update}

Any provider can send `routing-geo-update-interval: 24` as an HTTP response header, or `#routing-geo-update-interval: 24` in the subscription text (including base64-encoded text). Premium is not required. Values are integer hours from `0` to `8760`; zero or an absent value disables periodic checks **when there is no local override**. Invalid values are ignored. A valid HTTP header takes precedence over the body. `profile-update-interval` continues to control subscription refresh only.

The setting is supported on iOS/tvOS (including Designed for iPad on macOS), Android/TV and Desktop. It applies to the routing profile delivered with the subscription; it does not provide geo download URLs by itself. Those URLs come from `Geoipurl` and `Geositeurl` in the profile.

### Interval selection

The header always uses **hours**, even when the editor displays days:

| Editor interval | Header value |
|---|---|
| 3 days | `72` |
| 7 days | `168` |
| 15 days | `360` |
| 30 days | `720` |
| 90 days | `2160` |

Every profile editor offers disabled, 1/6/12/24 hours or 3/7/15/30/90 days, or the provider default. The local choice survives subscription updates and application restarts. A missing provider default means disabled. Initial downloads, manual refresh and changed-profile handling remain independent of this schedule.

### Failed downloads and retries {#geo-update-safety}

Scheduled checks refresh files at their existing URLs even when the profile's `LastUpdated` is unchanged. Matching `.sha256` sidecars avoid unnecessary downloads. Successful checks are recorded even when the contents are unchanged.

GeoIP and GeoSite are first downloaded into a staging directory. HTTP completeness, non-empty content and the published `.sha256` checksum are checked before replacing either live file. A network interruption or checksum mismatch keeps both previous files and does not advance the successful-check timestamp. If installing the second file fails, the first is rolled back.

Automatic failures back off for at least 30 minutes, then 1, 2, 4 and at most 6 hours while the app is running. Success resets the delay. Backoff is per session: restarting the app allows a fresh attempt. Manual refresh remains available immediately. On iOS, each file download also has up to three attempts with short delays.

A failed attempt does not restart the configured 3/7/15/30/90-day interval: it uses the shorter retry delay. Automatic retries require geo auto-update to be enabled. If it is disabled, use manual refresh. Until a successful update, existing geo rules continue to use the downloaded files. On a first download there is no previous copy to restore.

Checks run while the application is running and after launch. Background suspension or sleep can delay them. A new geo directory takes effect on the next connection; refresh does not forcibly disconnect VPN.

### Profiles from different providers

Imported profiles are shown as **Profile [GoVPN]**, using the provider's `profile-title` or the subscription name as fallback. They are bound by local subscription ID, so identical names in different subscriptions remain isolated. Renaming the provider updates the existing profile label. Legacy unbound profiles are retained to protect manually configured rules.
