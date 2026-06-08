# Примеры ссылок и параметров

Готовые примеры для интеграции маршрутизации и автообновляемой маршрутизации в подписки INCY.

---

## Deeplink-ссылки

### Статический профиль (base64)

Добавляет и активирует профиль из base64-данных:

```
://routing/onadd/eyJOYW1lIjoiUm9zY29tVlBOIiwiR2xvYmFsUHJveHkiOiJ0cnVlIiwiUmVtb3RlRE5TVHlwZSI6IkRvSCIsIlJlbW90ZUROU0RvbWFpbiI6Imh0dHBzOi8vY2xvdWRmbGFyZS1kbnMuY29tL2Rucy1xdWVyeSIsIlJlbW90ZUROU0lQIjoiMS4xLjEuMSIsIkRvbWVzdGljRE5TVHlwZSI6IkRvSCIsIkRvbWVzdGljRE5TRG9tYWluIjoiaHR0cHM6Ly9kbnMuZ29vZ2xlL2Rucy1xdWVyeSIsIkRvbWVzdGljRE5TSVAiOiI4LjguOC44IiwiRG9tYWluU3RyYXRlZ3kiOiJJUElmTm9uTWF0Y2gifQ==
```

Добавляет профиль без активации:

```
://routing/add/eyJOYW1lIjoiUm9zY29tVlBOIn0=
```

### Автообновляемый профиль (URL)

Скачивает профиль по URL и устанавливает автообновление:

```
://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

Через `routing/onadd/` с URL (URL обнаруживается автоматически):

```
://routing/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

### GitHub blob URL

Обычные GitHub-ссылки конвертируются автоматически:

```
://autorouting/onadd/https://github.com/user/repo/blob/main/INCY/DEFAULT.JSON
```

Приложение автоматически преобразует в:

```
https://raw.githubusercontent.com/user/repo/main/INCY/DEFAULT.JSON
```

---

## HTTP-заголовки подписки

### Autorouting — автообновляемый профиль

```
HTTP/2 200
content-type: text/plain
autorouting: https://raw.githubusercontent.com/user/repo/main/profile.json

vless://uuid@server1:443?security=tls&type=ws#Server 1
vless://uuid@server2:443?security=tls&type=ws#Server 2
```

### Routing — статический профиль (base64)

```
HTTP/2 200
content-type: text/plain
routing: ewogICJOYW1lIjogIlJvc2NvbVZQTiIsCiAgIkdsb2JhbFByb3h5IjogInRydWUiCn0=

vless://uuid@server1:443?security=tls#Server1
```

### Routing — статический профиль (полная ссылка)

```
HTTP/2 200
content-type: text/plain
routing: ://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIsCiAgIkdsb2JhbFByb3h5IjogInRydWUiCn0=

vless://uuid@server1:443?security=tls#Server1
```

### Комбинация заголовков

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

## Тело подписки (body)

### Autorouting в body

```
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://autorouting/onadd/https://raw.githubusercontent.com/user/repo/main/profile.json
```

### Routing в body

```
vless://uuid@server1:443?security=tls#Server1
vless://uuid@server2:443?security=tls#Server2
://routing/onadd/ewogICJOYW1lIjogIlJvc2NvbVZQTiIsCiAgIkdsb2JhbFByb3h5IjogInRydWUiCn0=
```

### Inline-метаданные в body (статический файл)

Все метаданные через `#` комментарии — полезно при раздаче подписок как статических файлов (nginx), где нет возможности задать кастомные HTTP-заголовки:

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

### Комбинация заголовков и body-метаданных

HTTP-заголовки имеют приоритет. Body-метаданные используются как fallback:

```
HTTP/2 200
content-type: text/plain
profile-title: VPN Pro

#support-url: https://t.me/support
#profile-update-interval: 6
vless://uuid@server1:443?security=tls#NL
vless://uuid@server2:443?security=tls#DE
```

В этом примере `profile-title` берётся из заголовка (`VPN Pro`), а `support-url` и `profile-update-interval` — из тела подписки.

---

## Примеры JSON-профилей

### Минимальный профиль

```json
{
    "Name": "Minimal",
    "GlobalProxy": "true",
    "DomainStrategy": "AsIs"
}
```

### Профиль для обхода блокировок РФ

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

### Профиль для Китая

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

## Размещение геофайлов с хеш-проверкой

Для оптимизации трафика размещайте SHA-256 хеш-файлы рядом с геофайлами:

```
https://example.com/geo/geoip.dat
https://example.com/geo/geoip.dat.sha256
https://example.com/geo/geosite.dat
https://example.com/geo/geosite.dat.sha256
```

Содержимое `.sha256` файла — hex-строка SHA-256 хеша (64 символа):

```
38c25fea171323e0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4
```

Генерация хеша:

```bash
sha256sum geoip.dat | awk '{print $1}' > geoip.dat.sha256
sha256sum geosite.dat | awk '{print $1}' > geosite.dat.sha256
```

Приложение скачивает `.sha256` перед полным файлом. Если хеш не изменился — скачивание полного файла пропускается (даже при ручном обновлении).

> **Примечание:** Начиная с версии 2.0.3, базовые геофайлы Loyalsoldier вшиты в приложение. Первый запуск не требует загрузки из интернета. Обновление геофайлов происходит при обновлении подписки или вручную.

---

## Примеры share-ссылок с транспортами

### mKCP с кастомными MTU и TTI

```
vless://uuid@server:443?security=none&type=kcp&headerType=srtp&seed=myseed&mtu=1400&tti=20#mKCP Server
```

| Параметр | Значение | Описание |
|---|---|---|
| `type` | `kcp` | Транспорт mKCP |
| `headerType` | `srtp` | Маскировка под SRTP |
| `seed` | `myseed` | Обфускация |
| `mtu` | `1400` | MTU (по умолчанию 1350) |
| `tti` | `20` | TTI в мс, 10–5000 (по умолчанию 50) |

### XHTTP

```
vless://uuid@server:443?security=tls&type=xhttp&mode=auto&path=/xhttp#XHTTP Server
```

### VLESS + REALITY

```
vless://uuid@server:443?security=reality&type=tcp&flow=xtls-rprx-vision&sni=example.com&fp=chrome&pbk=PUBLIC_KEY&sid=SHORT_ID&spx=%2F#REALITY Server
```
