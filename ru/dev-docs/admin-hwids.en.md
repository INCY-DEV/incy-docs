# Admin Access by HWID

`adminHwids` is a list of device HWIDs to which the provider has granted **admin privileges** within a specific subscription domain. There are two privileges: viewing/editing server configs directly in the app, and sending push notifications bypassing moderation.

---

## Where it's set

The provider adds an HWID in the [web panel](https://web.incy-panel.com) under the domain settings, in the **Admin Access** section. The field is stored in `SubscriptionSettings` and returned to the client through the [Premium API](premium-api.md):

| Field        | Type       | Description                                                       |
|--------------|------------|-------------------------------------------------------------------|
| `adminHwids` | `string[]` | Array of HWIDs in the same format the client sends as `x-hwid` |

For the HWID format, see [hwid.md](hwid.md). Comparison is **character-by-character** (no case normalization), so you need to copy the HWID exactly as the app shows it in its own settings.

---

## Privilege 1: viewing and editing server configs

If the device's HWID is in the current subscription's `adminHwids`:

- An edit button appears on the server card in the app (normally hidden for other users).
- The device can edit VLESS/VMess/Trojan/… parameters directly in the UI: address, port, UUID, transport settings.
- Edits take effect **locally only** on this device — they are not pushed back to the subscription. On the next subscription `refresh` the server is restored to the provider's version.

This is used for debugging: acting as an "insider" device, the provider can verify how a specific key or transport parameter works without rewriting the config on the server side.

---

## Privilege 2: sending notifications without moderation

By default, any notification a provider sends from the panel waits for INCY moderation (status `pending`).

If the targeting specifies a **specific HWID** and that HWID is present in the `adminHwids` of any of the provider's verified domains:

- The notification immediately gets the `approved` status (auto-approve by admin HWID).
- The fan-out starts immediately — without waiting for moderation.

This is needed for debugging your own notifications: the provider sends a test to their own personal device and sees the result instantly.

> **Important:** auto-approve only triggers when `targetSegment.hwid` is set **and** matches one of the `adminHwids`. Notifications without an HWID target or to someone else's HWID still go through moderation. See more in [provider-notifications.md](provider-notifications.md).

---

## Hygiene

- Keep only your own devices in `adminHwids`. Admin access grants a bypass of push notification moderation — a random stranger's HWID could spam the rest of your subscribers.
- A device's HWID changes after a factory reset or OS reinstall — the `adminHwids` list needs to be updated.
- Removing an HWID from the list takes effect the next time the device fetches its config (typically 1–5 minutes, depending on cache).
