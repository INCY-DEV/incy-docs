# Share-link parameters

Description of parameters for protocol server links (VLESS, VMess, Trojan, Shadowsocks, Hysteria2, SOCKS5, WireGuard).

---

## VLESS

```
vless://uuid@host:port?params#name?serverDescription=base64
```

### Core parameters

| Parameter | Field | Default | Description |
|---|---|---|---|
| `encryption` | encryption | `"none"` | Encryption |
| `flow` | flow | | XTLS flow (e.g. `xtls-rprx-vision`) |
| `type` | network | `"tcp"` | Transport: `tcp`, `ws`, `grpc`, `xhttp`, `kcp`, `quic` |
| `security` | security | `"none"` | Security: `none`, `tls`, `reality` |

### TLS

| Parameter | Field | Description |
|---|---|---|
| `sni` | SNI | Server Name Indication |
| `fp` | fingerprint | uTLS fingerprint (values below) |
| `alpn` | ALPN | Comma-separated protocols (e.g. `h2,http/1.1`) |

**Allowed `fp` values** (uTLS from xray-core): `chrome`, `firefox`, `safari`, `ios`, `android`, `edge`, `360`, `qq`, `random` (a random real browser), `randomized` (randomized with ALPN), `randomizednoalpn`. Pinned versions are also accepted: `hellochrome_120/131/133`, `hellofirefox_120/148`, `helloios_13/14`, `helloedge_106`, `hellosafari_26_3`, `hello360_11_0`, `helloqq_11_1`, `hellogolang` (Go-default, no impersonation), `unsafe`. Empty/unset → `chrome`. The value is passed to xray as-is.

### Reality

| Parameter | Field | Description |
|---|---|---|
| `pbk` | publicKey | Reality public key |
| `sid` | shortId | Short ID |
| `spx` | spiderX | Spider X path |

### Transport (WebSocket)

| Parameter | Field | Description |
|---|---|---|
| `path` | path | WebSocket path (URL-decoded) |
| `host` | host | Host header |

### Transport (gRPC)

| Parameter | Field | Description |
|---|---|---|
| `serviceName` | serviceName | gRPC service name |
| `authority` | authority | HTTP authority |

### Transport (xHTTP / SplitHTTP)

| Parameter | Field | Description |
|---|---|---|
| `path` | path | Path |
| `host` | host | Host header |
| `mode` | xhttpMode | Mode: `auto`, `packet`, `connect` |
| `extra` | xhttpExtra | Additional data (URL-encoded JSON) |

> `type=splithttp` is automatically normalized to `xhttp`.

### Transport (mKCP)

| Parameter | Field | Description |
|---|---|---|
| `headerType` | headerType | Header type (none, srtp, utp, wechat-video, etc.) |
| `seed` | kcpSeed | KCP seed |
| `mtu` | kcpMtu | MTU (Maximum Transmission Unit), default 1350 |
| `tti` | kcpTti | TTI (Transmission Time Interval) in ms, 10–5000, default 50 |

### Transport (QUIC)

| Parameter | Field | Description |
|---|---|---|
| `quicSecurity` | quicSecurity | `none`, `aes-128-gcm`, `chacha20-poly1305` |
| `key` | quicKey | QUIC key |

### Advanced security parameters

| Parameter | Field | Description |
|---|---|---|
| `fm` | finalmask | uTLS mask (URL-encoded JSON) |
| `pcs` | pinnedPeerCertSha256 | SHA-256 certificate pin (URL-encoded) |
| `vcn` | verifyPeerCertByName | Verify certificate by name (URL-encoded) |
| `ech` | echConfigList | Encrypted Client Hello config (URL-encoded) |
| `pqv` | mldsa65Verify | Post-quantum ML-DSA-65 verification |

### TCP fragmentation (per-server)

Fragmentation parameters can be set directly in the share-link, and they apply only to that server (separately from the provider-level `fragmentEnabled` in [Premium API](premium-api.md)).

| Parameter | Field | Description |
|---|---|---|
| `fragmentPackets` | fragmentPackets | Which packets to apply to: `tlshello`, `1-3`, `1`, `all` |
| `fragmentLength` | fragmentLength | Fragment length range in bytes (e.g. `10-30`) |
| `fragmentInterval` | fragmentInterval | Delay range between fragments in ms (e.g. `10-30`) |

These same parameters can be passed on any VLESS/VMess/Trojan server — the parser adds them to the `VLESSConfig` model and xray applies fragmentation when the `security` check is active (tls/reality).

### Fragment (after `#`)

```
#ServerName?serverDescription=SGlnaC1TcGVlZA==
```

- Everything before the first `?` is the server name (URL-decoded)
- `serverDescription` is a base64-encoded description (up to 30 characters)

---

## VMess

```
vmess://base64({ json })
```

Base64-encoded JSON object:

| Field | Type | Default | Description |
|---|---|---|---|
| `add` | string | | Server address |
| `port` | int | | Port |
| `id` | string | | UUID |
| `ps` | string | | Name / remark |
| `scy` | string | `"auto"` | Encryption |
| `aid` | int | `0` | Alter ID |
| `net` | string | `"tcp"` | Transport |
| `tls` | string | | `"tls"` or empty |
| `sni` | string | | SNI |
| `fp` | string | | TLS fingerprint |
| `path` | string | | WebSocket/gRPC path |
| `host` | string | | Host header |
| `type` | string | | Header type (ignored if `"none"`) |
| `alpn` | string | | Comma-separated ALPN |

Additionally for full xray configs:

| Field | Type | Description |
|---|---|---|
| `meta.serverDescription` | string | Server description |

---

## Trojan

```
trojan://password@host:port?params#name?serverDescription=base64
```

Parameters are similar to VLESS with the following differences:

- The password is passed in userInfo (instead of a UUID)
- `security` defaults to `"tls"` (not `"none"`)
- Additional parameter `peer` — fallback for SNI (if `sni` is not specified)
- Supports advanced parameters: `fm`, `pcs`, `vcn`, `ech`

---

## Shadowsocks

Two formats:

**Modern:**
```
ss://base64(method:password)@host:port#name?serverDescription=base64
```

**SIP002:**
```
ss://base64(method:password@host:port)#name?serverDescription=base64
```

| Component | Description |
|---|---|
| `method` | Encryption method (e.g. `aes-256-gcm`, `chacha20-ietf-poly1305`) |
| `password` | Password |

---

## Hysteria2

```
hysteria2://password@host:port1,port2-port3?params#name?serverDescription=base64
hy2://password@host:port?params#name?serverDescription=base64
```

### Parameters

| Parameter | Field | Description |
|---|---|---|
| `insecure` | security | `"1"` → no certificate verification |
| `sni` | SNI | Server Name Indication |
| `fp` | fingerprint | TLS fingerprint |
| `pinSHA256` | pinnedPeerCertSha256 | SHA-256 certificate pin (URL-encoded) |
| `alpn` | ALPN | Comma-separated protocols |
| `obfs` | hy2Obfs | Obfuscation type |
| `obfs-password` | hy2ObfsPassword | Obfuscation password (URL-encoded) |
| `up` | hy2UpMbps | Upload speed (Mbps) |
| `down` | hy2DownMbps | Download speed (Mbps) |

### Multi-port format

```
hysteria2://password@server:443,8443-8445#Server
```

- The first port (`443`) is used for connecting
- Format: `port1,port2-port3` (ranges are supported)

### IPv6

```
hysteria2://password@[::1]:443#Server
```

---

## SOCKS5

```
socks://username:password@host:port#name?serverDescription=base64
```

| Component | Description |
|---|---|
| `username:password` | SOCKS5 credentials (optional, may be anonymous) |
| `host:port` | Proxy server address |

SOCKS5 is a simple proxying protocol; no additional query parameters are required.

Fragment (`#`): everything before the first `?` is the server name (URL-decoded), `serverDescription` is a base64-encoded description (up to 30 characters).

### SOCKS5 example

```
socks://pkg-private2-country-us-city-new_york_city:w0e20i55uuq6pxqg@quality.proxywing.com:1080#title?serverDescription=SGFwcCB0aGUgYmVzdA==
```

---

## WireGuard

```
wireguard://secretKey@host:port?publickey=KEY&address=ADDR&mtu=1500&reserved=1,22,33#name?serverDescription=base64
```

| Component | Description |
|---|---|
| `secretKey` | Private (secret) key in userInfo |
| `host:port` | WireGuard endpoint address |

### WireGuard parameters

| Parameter | Required | Description |
|---|---|---|
| `publickey` | Yes | Peer public key |
| `address` | No | Local tunnel address (comma-separated for multiple) |
| `mtu` | No | MTU (default 1500) |
| `reserved` | No | Reserved bytes (comma-separated: `1,22,33`) |
| `allowinsecure` | No | `1` = do not verify certificate (informational) |

Fragment (`#`): everything before the first `?` is the server name (URL-decoded), `serverDescription` is a base64-encoded description (up to 30 characters).

### WireGuard example

```
wireguard://password2key@123.123.123.2:10803?publickey=asd33d223d33&address=dom.ru&allowinsecure=1&mtu=1500&reserved=1,22,33#title?serverDescription=SGFwcCB0aGUgYmVzdA==
```
