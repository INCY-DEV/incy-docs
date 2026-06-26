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

> `{base64}` is the JSON profile encoded in base64.

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
3. If the `.sha256` file is unavailable → fall back to comparing `LastUpdated` timestamps
4. The full file is downloaded → SHA-256 is computed → the file is replaced
5. The new hash is saved in the profile

### Recommendation for providers

Place a `geoip.dat.sha256` and `geosite.dat.sha256` file next to the geo files. The file must contain only the hex string of the SHA-256 hash (64 characters). This lets clients skip downloading unchanged files and save traffic.

Example contents of `geoip.dat.sha256`:
```
38c25fea171323e0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4
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
