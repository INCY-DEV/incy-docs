# HWID (Hardware ID)

A device hardware identifier used to bind subscriptions to specific devices and to track active connections.

## Format

The HWID is a string in UUID format (`8-4-4-4-12`, uppercase) derived from the device's hardware characteristics. A SHA-256 hash of the characteristics is computed (with the salt `incy_hwid_`), and its hex digest is formatted into a UUID. It is the same across all platforms — 36 characters with hyphens, for example `270DD26E-160D-4257-B8AC-654800E12F24`.

## Generation per platform

### Android

**Components** (joined with `|`):

| Component | Source |
|---|---|
| Android ID | `Settings.Secure.ANDROID_ID` |
| Manufacturer | `Build.MANUFACTURER` |
| Model | `Build.MODEL` |
| Brand | `Build.BRAND` |
| Device | `Build.DEVICE` |
| Product | `Build.PRODUCT` |
| Board | `Build.BOARD` |
| Hardware | `Build.HARDWARE` |

**Algorithm:**
```
deviceId = SHA256("androidId|manufacturer|model|brand|device|product|board|hardware")
hwid = hashToUuid(SHA256("incy_hwid_" + deviceId))   // hex → UUID 8-4-4-4-12
```

**Result:** UUID (36 characters, uppercase)
**Storage:** EncryptedSharedPreferences (persists across reinstall)

### Desktop (Linux)

**Components** (joined with `|`):

| Component | Source |
|---|---|
| Machine ID | `/etc/machine-id` |
| Hostname | `InetAddress.getLocalHost().hostName` |
| OS | `System.getProperty("os.name")` |
| Architecture | `System.getProperty("os.arch")` |
| User | `System.getProperty("user.name")` |

### Desktop (Windows)

**Components** (joined with `|`):

| Component | Source |
|---|---|
| Machine GUID | `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` |
| Hostname | `InetAddress.getLocalHost().hostName` |
| OS | `System.getProperty("os.name")` |
| Architecture | `System.getProperty("os.arch")` |
| User | `System.getProperty("user.name")` |

**Algorithm (Linux/Windows):**
```
deviceId = SHA256("machineId|hostname|os|arch|user")
hwid = hashToUuid(SHA256("incy_hwid_" + deviceId))   // hex → UUID 8-4-4-4-12
```

**Result:** UUID (36 characters, uppercase)
**Storage:** file `{configDir}/device_id`

### iOS

**Components:**

| Component | Source |
|---|---|
| Vendor ID | `UIDevice.current.identifierForVendor` |
| Device name | Device model |

**Algorithm:**
```
raw = "incy_hwid_{vendorID}-{deviceName}"
hwid = hashToUuid(SHA256(raw))   // hex → UUID 8-4-4-4-12
```

**Result:** UUID (36 characters, uppercase)
**Storage:** Keychain (persists even when the app is deleted)

> The format is the same on all platforms — a UUID from a SHA-256 hash. `shortHWID` (the first 8 characters) is used only for display.

## Usage

### HTTP request headers

When HWID sending is enabled, the app adds headers to subscription requests:

```http
x-hwid: <hwid>
x-device-os: <platform>
x-ver-os: <os_version>
x-device-model: <model>
```

### Premium API — device limit check

When requesting the provider configuration, the client passes the HWID hash:

```http
GET /api/subscription/config?h=<domainHash>&hwid=<sha256(hwid)>
```

The server uses `hwidHash` to check whether the device is registered with this provider and to decide whether to grant premium status within the [device limit](premium-api.md#device-limits).

### The `hwidHash` field in registration

During device registration, in addition to the raw `hwid`, the server stores `hwidHash = SHA256(hwid)`. This makes it possible to find a device by its hash without knowing the original identifier.

### Forced sending

The provider can enable forced HWID sending via the Premium API:

```json
{
    "settings": {
        "alwaysHwidEnable": true
    }
}
```

In this case the user cannot disable HWID sending for this subscription.

## Short HWID

The first 8 characters of the HWID are used for display in the UI.
