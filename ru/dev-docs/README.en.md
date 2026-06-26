# Developer Documentation

Technical documentation for integrating with the INCY app.

## Contents

### Subscriptions and servers

- [Subscription format](subscription-format.md) — supported formats, protocols, HTTP headers
- [Share-link parameters](share-links.md) — VLESS, VMess, Trojan, Shadowsocks, Hysteria2, SOCKS5, WireGuard
- [Full Xray configurations](full-xray-config.md) — configs with balancers and observatories
- [App management](app-management.md) — HTTP headers and subscription parameters (`hide-url`, provider banner via `banner-*` headers, etc.)

### Routing

- [Routing](routing.md) — routing profiles, geo files, rules, chunk-file trimming
- [Autorouting](autorouting.md) — profiles with auto-update by URL

### Integration

- [Deep Links](deep-links.md) — controlling the app through links (including encrypted `incy://crypt1/<payload>` for anti-grep forwarding)
- [HWID](hwid.md) — hardware device identifier
- [Premium API](premium-api.md) — encrypted provider config API, device limits, fallback domains (`fallbackHosts`)

### Provider settings

- [Preset icons](icon-presets.md) — icons for links in Lite Mode (bot / channel / support)
- [Admin access by HWID](admin-hwids.md) — editing configs on the device + auto-approve of push notifications
- [Provider push notifications](provider-notifications.md) — targeting, moderation, cancellation

### Premium and billing

- [Premium billing](premium-billing.md) — plans, payment methods, account linking, subscription management
- [VPN Auction](auction.md) — weekly auction for placement in the recommendations channel

### Examples

- [Link and parameter examples](examples.md) — ready-made examples for integration
