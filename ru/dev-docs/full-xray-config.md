# Полные Xray-конфигурации

Подписка может возвращать полные конфигурационные файлы xray-core с балансировщиками, обсерваториями и кастомной маршрутизацией. Такие конфигурации передаются в xray-core практически без изменений.

## Определение

Конфигурация считается «полной», если JSON содержит **оба** поля:

- `inbounds` — входящие подключения
- `outbounds` — исходящие подключения

Любой JSON-объект, содержащий и `inbounds`, и `outbounds`, распознаётся как полная конфигурация — независимо от наличия балансировщиков, обсерваторий или метаданных.

## Формат

### Одиночная конфигурация

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

### Массив конфигураций

```json
[
    { "outbounds": [...], "routing": { "balancers": [...] }, "burstObservatory": {...} },
    { "outbounds": [...], "routing": { "balancers": [...] }, "burstObservatory": {...} }
]
```

Каждый элемент массива — отдельная полная конфигурация, импортируется как отдельный «сервер».

## Автоматический патчинг

При запуске приложение автоматически патчит конфигурацию (`patchFullConfigInbounds`):

### 1. Логирование

- `log.loglevel` — устанавливается из настроек пользователя
- `log.access` и `log.error` — устанавливается путь к лог-файлу приложения

> iOS: `group.llc.itdev.incy/logs/xray.log`
> Android/Desktop: передаётся через параметр `logFilePath`

### 2. Inbound порты

- Все `socks` inbound'ы → порт `10808`, listen `127.0.0.1`
- Все `http` inbound'ы → порт `10809`, listen `127.0.0.1`
- Если SOCKS inbound отсутствует — добавляется автоматически с настройками sniffing

### 3. Stats

Если конфигурация содержит `burstObservatory` или `observatory`, но не содержит `stats` — автоматически добавляется пустой объект `"stats": {}`.

### 4. DNS Direct Routing (предотвращение циклической зависимости)

**Условие:** конфигурация содержит **и** observatory, **и** balancers.

**Проблема:** Observatory проверяет серверы → для проверки нужен DNS → DNS идёт через балансировщик → балансировщик зависит от результатов Observatory → цикл.

**Решение:** IP-адреса DNS-серверов из `dns.servers` добавляются в начало `routing.rules` с outbound `"direct"`:

```json
{
    "type": "field",
    "ip": ["8.8.8.8", "1.1.1.1"],
    "outboundTag": "direct"
}
```

Если outbound с тегом `"direct"` или протоколом `"freedom"` отсутствует — добавляется автоматически.

## Отображение в UI

- Полные конфигурации отображаются как один сервер в списке
- Бейджи безопасности и транспорта скрываются (информация внутри конфига)
- Если в `meta` есть `serverDescription` — отображается как описание сервера
- Имя сервера берётся из первого proxy-outbound'а

## Особенности работы с полными конфигурациями

### MPH Cache

Для полных конфигураций **MPH cache не используется**. Кэш (`mph_cache.dat`) предназначен для сериализации DomainMatcher, но несовместим с полными JSON-конфигурациями. При обнаружении полной конфигурации:

- Существующий файл `mph_cache.dat` удаляется
- Xray-core строит матчеры в рантайме
- Флаг `isFullConfig` передаётся из основного приложения в Network Extension (iOS) через `providerConfiguration` и `sharedDefaults`

### Геофайлы (Geo Trimming)

Для полных конфигураций **обрезка геофайлов пропускается**. Полные конфигурации поставляются с собственными кастомными геофайлами от подписки, которые используются как есть. При подключении:

- `GeoTrimmer` не вызывается
- Обрезанные файлы удаляются (`deleteTrimmedGeoFiles`)
- Xray-core использует оригинальные геофайлы

### DNS

Для полных конфигураций **DNS-серверы не заменяются**. Полные конфигурации уже содержат корректно настроенные DNS с фильтрами `domains`/`expectIPs`, поэтому приложение:

- Не подставляет свои DNS-серверы
- Сохраняет оригинальные DNS-записи из конфигурации
- Добавляет только Direct-правило для DNS-серверов (для предотвращения циклической зависимости с Observatory)

## Хранение

Полная JSON-конфигурация сохраняется в поле `fullConfigJson` модели `VLESSConfig`. При запуске xray-core конфиг патчится и передаётся целиком, без генерации из отдельных полей.
