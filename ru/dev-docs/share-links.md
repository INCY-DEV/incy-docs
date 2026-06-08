# Параметры share-ссылок

Описание параметров для протокольных ссылок серверов (VLESS, VMess, Trojan, Shadowsocks, Hysteria2, SOCKS5, WireGuard).

---

## VLESS

```
vless://uuid@host:port?params#name?serverDescription=base64
```

### Основные параметры

| Параметр | Поле | По умолчанию | Описание |
|---|---|---|---|
| `encryption` | encryption | `"none"` | Шифрование |
| `flow` | flow | | XTLS flow (напр. `xtls-rprx-vision`) |
| `type` | network | `"tcp"` | Транспорт: `tcp`, `ws`, `grpc`, `xhttp`, `kcp`, `quic` |
| `security` | security | `"none"` | Безопасность: `none`, `tls`, `reality` |

### TLS

| Параметр | Поле | Описание |
|---|---|---|
| `sni` | SNI | Server Name Indication |
| `fp` | fingerprint | TLS fingerprint (chrome, firefox, safari, и др.) |
| `alpn` | ALPN | Протоколы через запятую (напр. `h2,http/1.1`) |

### Reality

| Параметр | Поле | Описание |
|---|---|---|
| `pbk` | publicKey | Публичный ключ Reality |
| `sid` | shortId | Short ID |
| `spx` | spiderX | Spider X path |

### Transport (WebSocket)

| Параметр | Поле | Описание |
|---|---|---|
| `path` | path | Путь WebSocket (URL-decoded) |
| `host` | host | Host-заголовок |

### Transport (gRPC)

| Параметр | Поле | Описание |
|---|---|---|
| `serviceName` | serviceName | Имя gRPC-сервиса |
| `authority` | authority | HTTP authority |

### Transport (xHTTP / SplitHTTP)

| Параметр | Поле | Описание |
|---|---|---|
| `path` | path | Путь |
| `host` | host | Host-заголовок |
| `mode` | xhttpMode | Режим: `auto`, `packet`, `connect` |
| `extra` | xhttpExtra | Дополнительные данные (URL-encoded JSON) |

> `type=splithttp` автоматически нормализуется в `xhttp`.

### Transport (mKCP)

| Параметр | Поле | Описание |
|---|---|---|
| `headerType` | headerType | Тип заголовка (none, srtp, utp, wechat-video, и др.) |
| `seed` | kcpSeed | KCP seed |
| `mtu` | kcpMtu | MTU (Maximum Transmission Unit), по умолчанию 1350 |
| `tti` | kcpTti | TTI (Transmission Time Interval) в мс, 10–5000, по умолчанию 50 |

### Transport (QUIC)

| Параметр | Поле | Описание |
|---|---|---|
| `quicSecurity` | quicSecurity | `none`, `aes-128-gcm`, `chacha20-poly1305` |
| `key` | quicKey | Ключ QUIC |

### Расширенные параметры безопасности

| Параметр | Поле | Описание |
|---|---|---|
| `fm` | finalmask | Маска uTLS (URL-encoded JSON) |
| `pcs` | pinnedPeerCertSha256 | SHA-256 пин сертификата (URL-encoded) |
| `vcn` | verifyPeerCertByName | Проверка сертификата по имени (URL-encoded) |
| `ech` | echConfigList | Encrypted Client Hello конфиг (URL-encoded) |
| `pqv` | mldsa65Verify | Post-quantum ML-DSA-65 верификация |

### TCP-фрагментация (per-server)

Параметры фрагментации можно задать прямо в share-link, и они применятся только к этому серверу (отдельно от провайдерских `fragmentEnabled` в [Premium API](premium-api.md)).

| Параметр | Поле | Описание |
|---|---|---|
| `fragmentPackets` | fragmentPackets | На какие пакеты применять: `tlshello`, `1-3`, `1`, `all` |
| `fragmentLength` | fragmentLength | Диапазон длины фрагмента в байтах (напр. `10-30`) |
| `fragmentInterval` | fragmentInterval | Диапазон задержки между фрагментами в мс (напр. `10-30`) |

Эти же параметры можно передать на любом VLESS/VMess/Trojan-сервере — парсер добавит их в модель `VLESSConfig` и xray применит фрагментацию при активной проверке `security` (tls/reality).

### Фрагмент (после `#`)

```
#ServerName?serverDescription=SGlnaC1TcGVlZA==
```

- Всё до первого `?` — имя сервера (URL-decoded)
- `serverDescription` — base64-закодированное описание (до 30 символов)

---

## VMess

```
vmess://base64({ json })
```

Base64-закодированный JSON-объект:

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `add` | string | | Адрес сервера |
| `port` | int | | Порт |
| `id` | string | | UUID |
| `ps` | string | | Имя / remark |
| `scy` | string | `"auto"` | Шифрование |
| `aid` | int | `0` | Alter ID |
| `net` | string | `"tcp"` | Транспорт |
| `tls` | string | | `"tls"` или пусто |
| `sni` | string | | SNI |
| `fp` | string | | TLS fingerprint |
| `path` | string | | WebSocket/gRPC путь |
| `host` | string | | Host-заголовок |
| `type` | string | | Header type (игнорируется если `"none"`) |
| `alpn` | string | | ALPN через запятую |

Дополнительно для полных xray-конфигов:

| Поле | Тип | Описание |
|---|---|---|
| `meta.serverDescription` | string | Описание сервера |

---

## Trojan

```
trojan://password@host:port?params#name?serverDescription=base64
```

Параметры аналогичны VLESS со следующими отличиями:

- Пароль передаётся в userInfo (вместо UUID)
- `security` по умолчанию `"tls"` (не `"none"`)
- Дополнительный параметр `peer` — fallback для SNI (если `sni` не указан)
- Поддерживает расширенные параметры: `fm`, `pcs`, `vcn`, `ech`

---

## Shadowsocks

Два формата:

**Современный:**
```
ss://base64(method:password)@host:port#name?serverDescription=base64
```

**SIP002:**
```
ss://base64(method:password@host:port)#name?serverDescription=base64
```

| Компонент | Описание |
|---|---|
| `method` | Метод шифрования (напр. `aes-256-gcm`, `chacha20-ietf-poly1305`) |
| `password` | Пароль |

---

## Hysteria2

```
hysteria2://password@host:port1,port2-port3?params#name?serverDescription=base64
hy2://password@host:port?params#name?serverDescription=base64
```

### Параметры

| Параметр | Поле | Описание |
|---|---|---|
| `insecure` | security | `"1"` → без проверки сертификата |
| `sni` | SNI | Server Name Indication |
| `fp` | fingerprint | TLS fingerprint |
| `pinSHA256` | pinnedPeerCertSha256 | SHA-256 пин сертификата (URL-encoded) |
| `alpn` | ALPN | Протоколы через запятую |
| `obfs` | hy2Obfs | Тип обфускации |
| `obfs-password` | hy2ObfsPassword | Пароль обфускации (URL-encoded) |
| `up` | hy2UpMbps | Скорость загрузки (Mbps) |
| `down` | hy2DownMbps | Скорость скачивания (Mbps) |

### Мульти-портовый формат

```
hysteria2://password@server:443,8443-8445#Server
```

- Первый порт (`443`) используется для подключения
- Формат: `порт1,порт2-порт3` (диапазоны поддерживаются)

### IPv6

```
hysteria2://password@[::1]:443#Server
```

---

## SOCKS5

```
socks://username:password@host:port#name?serverDescription=base64
```

| Компонент | Описание |
|---|---|
| `username:password` | Учётные данные SOCKS5 (опционально, может быть анонимным) |
| `host:port` | Адрес прокси-сервера |

SOCKS5 — простой протокол проксирования, дополнительные query-параметры не требуются.

Фрагмент (`#`): всё до первого `?` — имя сервера (URL-decoded), `serverDescription` — base64-закодированное описание (до 30 символов).

### Пример SOCKS5

```
socks://pkg-private2-country-us-city-new_york_city:w0e20i55uuq6pxqg@quality.proxywing.com:1080#title?serverDescription=SGFwcCB0aGUgYmVzdA==
```

---

## WireGuard

```
wireguard://secretKey@host:port?publickey=KEY&address=ADDR&mtu=1500&reserved=1,22,33#name?serverDescription=base64
```

| Компонент | Описание |
|---|---|
| `secretKey` | Приватный (секретный) ключ в userInfo |
| `host:port` | Адрес эндпоинта WireGuard |

### Параметры WireGuard

| Параметр | Обязательный | Описание |
|---|---|---|
| `publickey` | Да | Публичный ключ пира |
| `address` | Нет | Локальный туннельный адрес (через запятую для нескольких) |
| `mtu` | Нет | MTU (по умолчанию 1500) |
| `reserved` | Нет | Зарезервированные байты (через запятую: `1,22,33`) |
| `allowinsecure` | Нет | `1` = не проверять сертификат (информационный) |

Фрагмент (`#`): всё до первого `?` — имя сервера (URL-decoded), `serverDescription` — base64-закодированное описание (до 30 символов).

### Пример WireGuard

```
wireguard://password2key@123.123.123.2:10803?publickey=asd33d223d33&address=dom.ru&allowinsecure=1&mtu=1500&reserved=1,22,33#title?serverDescription=SGFwcCB0aGUgYmVzdA==
```
