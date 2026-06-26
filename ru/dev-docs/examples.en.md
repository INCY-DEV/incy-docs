# Link and Parameter Examples

Ready-made examples for integrating routing and auto-updated routing into INCY subscriptions.

---

## Deeplinks

### Static Profile (base64)

Adds and activates a profile from base64 data:

```
://routing/onadd/eyJOYW1lIjoiUm9zY29tVlBOIiwiR2xvYmFsUHJveHkiOiJ0cnVlIiwiUmVtb3RlRE5TVHlwZSI6IkRvSCIsIlJlbW90ZUROU0RvbWFpbiI6Imh0dHBzOi8vY2xvdWRmbGFyZS1kbnMuY29tL2Rucy1xdWVyeSIsIlJlbW90ZUROU0lQIjoiMS4xLjEuMSIsIkRvbWVzdGljRE5TVHlwZSI6IkRvSCIsIkRvbWVzdGljRE5TRG9tYWluIjoiaHR0cHM6Ly9kbnMuZ29vZ2xlL2Rucy1xdWVyeSIsIkRvbWVzdGljRE5TSVAiOiI4LjguOC44IiwiRG9tYWluU3RyYXRlZ3kiOiJJUElmTm9uTWF0Y2gifQ==
```

Adds a profile without activating it:

```
://routing/add/eyJOYW1lIjoiUm9zY29tVlBOIn0=
```

### Auto-Updated Profile (URL)

Downloads the profile from a URL and enables auto-update:

```
://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

Via `routing/onadd/` with a URL (the URL is detected automatically):

```
://routing/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

### GitHub blob URL

Regular GitHub links are converted automatically:

```
://autorouting/onadd/https://github.com/user/repo/blob/main/INCY/DEFAULT.JSON
```

The app automatically converts it to:

```
https://raw.githubusercontent.com/user/repo/main/INCY/DEFAULT.JSON
```

---

## Subscription HTTP Headers

### Autorouting — auto-updated profile

```
HTTP/2 200
content-type: text/plain
autorouting: https://raw.githubusercontent.com/user/repo/main/profile.json

vless://uuid@server1:443?security=tls&type=ws#Server 1
vless://uuid@server2:443?security=tls&type=ws#Server 2
```

### Routing — static profile (base64)

```
HTTP/2 200
content-type: text/plain
routing: ewogICJOYW1lIjogIlJvc2NvbVZQTiIsCiAgIkdsb2JhbFByb3h5IjogInRydWUiCn0=

vless://uuid@server1:443?security=tls#Server1
```

### Routing — static profile (full link)

```
HTTP/2 200
content-type: text/plain
routing: ://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIsCiAgIkdsb2JhbFByb3h5IjogInRydWUiCn0=

vless://uuid@server1:443?security=tls#Server1
```

### Header Combination

```
HTTP/2 200
content-type: text/plain
profile-title: My VPN
support-url: https://t.me/support_bot
profile-web-page-url: https://my-vpn.com
subscription-userinfo: upload=0;download=536870912;total=10737418240;expire=1735689600
autorouting: https://raw.githubusercontent.com/user/repo/main/profile.json

vless://uuid@server1:443?security=tls#NL
vless://uuid@server2:443?security=tls#DE
vless://uuid@server3:443?security=tls#FI
```

---

## Subscription Body

### Autorouting in the body

```
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

### Routing in the body

```
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIsCiAgIkdsb2JhbFByb3h5IjogInRydWUiCn0=
```

### Inline Metadata in the Body (static file)

All metadata via `#` comments — useful when serving subscriptions as static files (nginx), where custom HTTP headers cannot be set:

```
#profile-update-interval: 1
#profile-title: Обход белых списков
#support-url: https://t.me/+example
#announce: base64:0J/Qu9Cw0L3QvtCy0L7QtSDQvtCx0YHQu9GD0LbQuNCy0LDQvdC40LU=
#announce-url: https://example.com/news
#profile-web-page-url: https://example.com
vless://uuid@server1:443?security=tls#NL
vless://uuid@server2:443?security=tls#DE
://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

### Combination of Headers and Body Metadata

HTTP headers take precedence. Body metadata is used as a fallback:

```
HTTP/2 200
content-type: text/plain
profile-title: VPN Pro

#support-url: https://t.me/support
#profile-update-interval: 6
vless://uuid@server1:443?security=tls#NL
vless://uuid@server2:443?security=tls#DE
```

In this example, `profile-title` is taken from the header (`VPN Pro`), while `support-url` and `profile-update-interval` come from the subscription body.

---

## JSON Profile Examples

### Minimal Profile

```json
{
    "Name": "Minimal",
    "GlobalProxy": "true",
    "DomainStrategy": "AsIs"
}
```

### Profile for Bypassing RU Blocks

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

### Profile for China

```json
{
    "Name": "China",
    "GlobalProxy": "true",
    "RemoteDNSType": "DoH",
    "RemoteDNSDomain": "https://cloudflare-dns.com/dns-query",
    "RemoteDNSIP": "1.1.1.1",
    "DomesticDNSType": "DoU",
    "DomesticDNSDomain": "",
    "DomesticDNSIP": "8.8.8.8",
    "Geoipurl": "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat",
    "Geositeurl": "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat",
    "DnsHosts": {
        "cloudflare-dns.com": "1.1.1.1"
    },
    "DirectSites": ["geosite:cn", "geosite:geolocation-cn"],
    "DirectIp": ["geoip:cn", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16", "224.0.0.0/4", "255.255.255.255"],
    "ProxySites": ["geosite:cn"],
    "ProxyIp": ["geoip:amazon"],
    "BlockSites": ["geosite:ads"],
    "BlockIp": ["geoip:ads"],
    "DomainStrategy": "IPIfNonMatch",
    "FakeDNS": "false"
}
```

---

## Hosting Geo Files with Hash Verification

To optimize traffic, place SHA-256 hash files next to the geo files:

```
https://example.com/geo/geoip.dat
https://example.com/geo/geoip.dat.sha256
https://example.com/geo/geosite.dat
https://example.com/geo/geosite.dat.sha256
```

The contents of the `.sha256` file is a hex string of the SHA-256 hash (64 characters):

```
38c25fea171323e0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4
```

Generating the hash:

```bash
sha256sum geoip.dat | awk '{print $1}' > geoip.dat.sha256
sha256sum geosite.dat | awk '{print $1}' > geosite.dat.sha256
```

The app downloads the `.sha256` before the full file. If the hash has not changed, downloading the full file is skipped (even during a manual update).

> **Note:** Starting with version 2.0.3, the base Loyalsoldier geo files are bundled into the app. The first launch does not require downloading from the internet. Geo files are updated when the subscription is refreshed or manually.

---

## Share Link Examples with Transports

### mKCP with custom MTU and TTI

```
vless://uuid@server:443?security=none&type=kcp&headerType=srtp&seed=myseed&mtu=1400&tti=20#mKCP Server
```

| Parameter | Value | Description |
|---|---|---|
| `type` | `kcp` | mKCP transport |
| `headerType` | `srtp` | Masquerade as SRTP |
| `seed` | `myseed` | Obfuscation |
| `mtu` | `1400` | MTU (default 1350) |
| `tti` | `20` | TTI in ms, 10–5000 (default 50) |

### XHTTP

```
vless://uuid@server:443?security=tls&type=xhttp&mode=auto&path=/xhttp#XHTTP Server
```

### VLESS + REALITY

```
vless://uuid@server:443?security=reality&type=tcp&flow=xtls-rprx-vision&sni=example.com&fp=chrome&pbk=PUBLIC_KEY&sid=SHORT_ID&spx=%2F#REALITY Server
```
