# Provider Push Notifications

Providers with an active Premium plan can send push notifications to their subscribers. All messages go through INCY moderation, except when sending to your own device via an [admin HWID](admin-hwids.md).

---

## Notification lifecycle

1. **Creation.** The provider clicks "Send" in the panel → the notification is queued with status `pending`.
2. **Moderation.** The notification goes through INCY moderation: "Approve" or "Reject with comment".
3. **Fan-out.** On approval, the server selects devices by `targetSegment` and sends a push to every device that has a push token.
4. **Statuses.** The provider sees the status and the `deliveredCount` / `failedCount` counters in the panel.

### Record statuses

| Status       | Meaning                                                             |
|--------------|---------------------------------------------------------------------|
| `pending`    | Awaiting moderation                                                 |
| `approved`   | Approved by a moderator (or auto-approved); FCM fan-out completed   |
| `rejected`   | Rejected by a moderator. `moderatorComment` contains the reason     |
| `cancelled`  | Provider cancelled before approval. Fan-out was not performed       |
| `failed`     | Approved, but fan-out failed (no verified domains / FCM error)      |

---

## Sending: notification fields

| Field           | Type      | Required | Description                                                 |
|-----------------|-----------|:--------:|-------------------------------------------------------------|
| `title`         | `string`  | yes      | Title, ≤ 100 characters                                     |
| `body`          | `string`  | yes      | Text, ≤ 500 characters                                      |
| `image`         | `string?` | no       | URL of a large image (shown in the expanded push)           |
| `url`           | `string?` | no       | URL for the button / tap on the notification                |
| `urlButtonName` | `string?` | no       | Button label. Defaults to "Open"                            |
| `forceTimer`    | `number?` | no       | Enterprise-only: show a modal dialog for N seconds (1-10)   |
| `targetSegment` | `object`  | yes      | Targeting parameters (below)                                |

### Targeting (`targetSegment`)

| Field        | Type        | Description                                                              |
|--------------|-------------|--------------------------------------------------------------------------|
| `platform`   | `string`    | `all` \| `ios` \| `android` \| `linux` \| `windows` \| `macos`           |
| `region`     | `string[]?` | Device locale (e.g. `["ru", "by"]`). Comparison is case-insensitive      |
| `domain`     | `string?`   | A specific provider subscription domain (if the provider has several)    |
| `activeDays` | `number?`   | Only devices apparently active within the last N days                    |
| `appVersion` | `string?`   | Only a specific app version (e.g. `"2.5.6"`)                             |
| `hwid`       | `string?`   | A specific HWID. Enables [admin-HWID auto-approve](#auto-approve-via-admin-hwid) |

All filters are combined with logical **AND**. Empty / unspecified fields do not restrict the fan-out.

### Delivery

- **Android / iOS** receive the push directly (FCM / APNs).
- **Desktop (Linux / Windows)** picks up the notification on its next sync (desktop has no push channel) — text, link, button, image, and timer.

### Limitations

- Only for the provider's verified domains.
- Only with an active Premium plan.
- `forceTimer` > 0 works only on the Enterprise plan.

---

## Auto-approve via admin HWID

If `targetSegment.hwid` matches one of the `adminHwids` of any of the provider's verified domains, the record is created immediately with status `approved`, moderation is skipped, and FCM is sent right away.

Details: [admin-hwids.md](admin-hwids.md).

This is the only way a provider can send a notification bypassing moderation.

---

## Cancelling a fan-out

While the status is `pending`, the provider can cancel the notification in the panel. As a result:

- The status changes to `cancelled`.
- If the moderator decides to "Approve" at that moment, the bot gets the response "Provider cancelled the fan-out" and FCM is not performed.

After moving to any terminal status (`approved` / `rejected` / `cancelled` / `failed`), the operation is irreversible.

---

## Audit

Each record in `pendingNotifications` stores:

| Field               | Description                                               |
|---------------------|-----------------------------------------------------------|
| `providerId`        | Provider UID                                              |
| `providerEmail`     | Provider email at the time of sending                    |
| `createdAt`         | When the provider clicked "Send"                         |
| `moderatedAt`       | When the moderator decided / the system auto-approved    |
| `moderatorComment`  | Rejection text (for `rejected`)                          |
| `autoApproved`      | `true` if moderation was bypassed                        |
| `autoApproveReason` | Reason, e.g. `"adminHwid"`                               |
| `cancelledAt`       | For `cancelled` — when the provider cancelled            |
| `cancelledBy`       | Source of cancellation (currently only `"provider"`)     |
| `deliveredCount`    | Number of pushes successfully sent + desktop-polling devices |
| `failedCount`       | FCM errors                                               |
