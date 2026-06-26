# HWID (Hardware ID)

Аппаратный идентификатор устройства, используемый для привязки подписок к конкретным устройствам и отслеживания активных подключений.

## Формат

HWID — строка в формате UUID (`8-4-4-4-12`, верхний регистр), производная от аппаратных характеристик устройства. Считается SHA-256 хеш от характеристик (с солью `incy_hwid_`), и его hex-дайджест форматируется в UUID. На всех платформах одинаково — 36 символов с дефисами, например `270DD26E-160D-4257-B8AC-654800E12F24`.

## Генерация по платформам

### Android

**Компоненты** (объединяются через `|`):

| Компонент | Источник |
|---|---|
| Android ID | `Settings.Secure.ANDROID_ID` |
| Производитель | `Build.MANUFACTURER` |
| Модель | `Build.MODEL` |
| Бренд | `Build.BRAND` |
| Устройство | `Build.DEVICE` |
| Продукт | `Build.PRODUCT` |
| Плата | `Build.BOARD` |
| Оборудование | `Build.HARDWARE` |

**Алгоритм:**
```
deviceId = SHA256("androidId|manufacturer|model|brand|device|product|board|hardware")
hwid = hashToUuid(SHA256("incy_hwid_" + deviceId))   // hex → UUID 8-4-4-4-12
```

**Результат:** UUID (36 символов, верхний регистр)
**Хранение:** EncryptedSharedPreferences (сохраняется при переустановке)

### Desktop (Linux)

**Компоненты** (объединяются через `|`):

| Компонент | Источник |
|---|---|
| Machine ID | `/etc/machine-id` |
| Hostname | `InetAddress.getLocalHost().hostName` |
| OS | `System.getProperty("os.name")` |
| Архитектура | `System.getProperty("os.arch")` |
| Пользователь | `System.getProperty("user.name")` |

### Desktop (Windows)

**Компоненты** (объединяются через `|`):

| Компонент | Источник |
|---|---|
| Machine GUID | `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` |
| Hostname | `InetAddress.getLocalHost().hostName` |
| OS | `System.getProperty("os.name")` |
| Архитектура | `System.getProperty("os.arch")` |
| Пользователь | `System.getProperty("user.name")` |

**Алгоритм (Linux/Windows):**
```
deviceId = SHA256("machineId|hostname|os|arch|user")
hwid = hashToUuid(SHA256("incy_hwid_" + deviceId))   // hex → UUID 8-4-4-4-12
```

**Результат:** UUID (36 символов, верхний регистр)
**Хранение:** файл `{configDir}/device_id`

### iOS

**Компоненты:**

| Компонент | Источник |
|---|---|
| Vendor ID | `UIDevice.current.identifierForVendor` |
| Имя устройства | Модель устройства |

**Алгоритм:**
```
raw = "incy_hwid_{vendorID}-{deviceName}"
hwid = hashToUuid(SHA256(raw))   // hex → UUID 8-4-4-4-12
```

**Результат:** UUID (36 символов, верхний регистр)
**Хранение:** Keychain (сохраняется даже при удалении приложения)

> Формат одинаков на всех платформах — UUID из SHA-256 хеша. `shortHWID` (первые 8 символов) используется только для отображения.

## Использование

### HTTP-заголовки запроса

При включённой отправке HWID приложение добавляет заголовки к запросам подписки:

```http
x-hwid: <hwid>
x-device-os: <platform>
x-ver-os: <os_version>
x-device-model: <model>
```

### Premium API — проверка лимита устройств

При запросе конфигурации провайдера клиент передаёт хеш HWID:

```http
GET /api/subscription/config?h=<domainHash>&hwid=<sha256(hwid)>
```

Сервер использует `hwidHash` для проверки, зарегистрировано ли устройство у данного провайдера, и принятия решения о выдаче premium-статуса в рамках [лимита устройств](premium-api.md#лимиты-устройств).

### Поле `hwidHash` в регистрации

При регистрации устройства помимо сырого `hwid` сервер хранит `hwidHash = SHA256(hwid)`. Это позволяет находить устройство по хешу без знания исходного идентификатора.

### Принудительная отправка

Провайдер может включить принудительную отправку HWID через Premium API:

```json
{
    "settings": {
        "alwaysHwidEnable": true
    }
}
```

При этом пользователь не может отключить отправку HWID для данной подписки.

## Short HWID

Для отображения в UI используются первые 8 символов HWID.
