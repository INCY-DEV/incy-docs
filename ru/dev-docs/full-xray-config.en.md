# Full Xray Configurations

A subscription can return complete xray-core configuration files with balancers, observatories, and custom routing. Such configurations are passed to xray-core almost unchanged.

## Detection

A configuration is considered "full" if the JSON contains **both** fields:

- `inbounds` — incoming connections
- `outbounds` — outgoing connections

Any JSON object containing both `inbounds` and `outbounds` is recognized as a full configuration — regardless of whether it has balancers, observatories, or metadata.

## Format

### Single Configuration

```json
{
    "log": { "loglevel": "warning" },
    "dns": { "servers": [...] },
    "inbounds": [
        { "tag": "socks-in", "protocol": "socks", "port": 10808, "listen": "127.0.0.1" },
        { "tag": "http-in", "protocol": "http", "port": 10809, "listen": "127.0.0.1" }
    ],
    "outbounds": [
        { "tag": "proxy-1", "protocol": "vless", "settings": {...} },
        { "tag": "proxy-2", "protocol": "vless", "settings": {...} },
        { "tag": "direct", "protocol": "freedom" },
        { "tag": "block", "protocol": "blackhole" }
    ],
    "routing": {
        "domainStrategy": "IPIfNonMatch",
        "rules": [...],
        "balancers": [
            {
                "tag": "balancer-1",
                "selector": ["proxy-1", "proxy-2"],
                "strategy": { "type": "leastPing" }
            }
        ]
    },
    "burstObservatory": {
        "subjectSelector": ["proxy-1", "proxy-2"],
        "pingConfig": {
            "destination": "http://www.google.com/generate_204",
            "connectivity": "http://www.google.com/generate_204",
            "interval": "30s",
            "sampling": 2,
            "timeout": "5s"
        }
    },
    "stats": {}
}
```

### Array of Configurations

```json
[
    { "outbounds": [...], "routing": { "balancers": [...] }, "burstObservatory": {...} },
    { "outbounds": [...], "routing": { "balancers": [...] }, "burstObservatory": {...} }
]
```

Each element of the array is a separate full configuration, imported as a separate "server".

## Automatic Patching

On startup, the app automatically patches the configuration (`patchFullConfigInbounds`):

### 1. Logging

- `log.loglevel` — set from the user's settings
- `log.access` and `log.error` — set to the app's log file path

> iOS: `group.llc.itdev.incy/logs/xray.log`
> Android/Desktop: passed via the `logFilePath` parameter

### 2. Inbounds

- For all non-internal `socks` / `mixed` / `http` inbounds, `listen` is forced to `127.0.0.1` (the port is **not** changed — the config must itself listen on `10808` for SOCKS/mixed and `10809` for HTTP, these are the client's entry points).
- If the config has no socks-like inbound at all, a `mixed` inbound on `127.0.0.1:10808` with sniffing is added.
- For specific inbounds without their own authorization, the client "paints on" credentials so the port is not left as an open relay.

### 3. Stats

If the configuration contains `burstObservatory` or `observatory` but does not contain `stats`, an empty `"stats": {}` object is added automatically.

### 4. DNS Direct Routing (preventing a circular dependency)

**Condition:** the configuration contains **both** an observatory **and** balancers.

**Problem:** The observatory checks servers → checking requires DNS → DNS goes through the balancer → the balancer depends on the observatory's results → a loop.

**Solution:** The IP addresses of the DNS servers from `dns.servers` are added at the beginning of `routing.rules` with the `"direct"` outbound:

```json
{
    "type": "field",
    "ip": ["8.8.8.8", "1.1.1.1"],
    "outboundTag": "direct"
}
```

If an outbound with the `"direct"` tag or the `"freedom"` protocol is absent, it is added automatically.

## Display in the UI

- Full configurations are displayed as a single server in the list
- Security and transport badges are hidden (the information is inside the config)
- If `meta` contains `serverDescription`, it is displayed as the server description
- The server name is taken from the first proxy outbound

## Specifics of Working with Full Configurations

### MPH Cache

For full configurations, the **MPH cache is not used**. The cache (`mph_cache.dat`) is intended for serializing the DomainMatcher, but it is incompatible with full JSON configurations. When a full configuration is detected:

- The existing `mph_cache.dat` file is deleted
- Xray-core builds the matchers at runtime
- The `isFullConfig` flag is passed from the main app to the Network Extension (iOS) via `providerConfiguration` and `sharedDefaults`

### Geo Files (Geo Trimming)

For full configurations, **geo file trimming is skipped**. Full configurations ship with their own custom geo files from the subscription, which are used as-is. When connecting:

- `GeoTrimmer` is not called
- Trimmed files are deleted (`deleteTrimmedGeoFiles`)
- Xray-core uses the original geo files

### DNS

For full configurations, **DNS servers are not replaced**. Full configurations already contain properly configured DNS with `domains`/`expectIPs` filters, so the app:

- Does not substitute its own DNS servers
- Preserves the original DNS records from the configuration
- Only adds a Direct rule for the DNS servers (to prevent a circular dependency with the observatory)

## Storage

The full JSON configuration is stored in the `fullConfigJson` field of the `VLESSConfig` model. When xray-core starts, the config is patched and passed in full, without generating it from individual fields.
