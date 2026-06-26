# Premium Billing

The INCY Premium payment and subscription management system for providers.

## Overview

Premium gives providers access to advanced features: domain management, push notifications, analytics, custom theme, and logo.

---

## Pricing

| Parameter | Value |
| --- | --- |
| Base rate | **$0.06** per device per month |
| Minimum | 100 devices |
| Self-service | up to 10,000 devices |
| Enterprise | 10,000+ devices (custom terms) |

### Billing periods

| Period | Discount |
| --- | --- |
| 1 month | — |
| 3 months | 3% |
| 6 months | 8% |

### Enterprise

For providers with more than 10,000 devices, custom terms are available:
- Custom rate (below $0.06)
- Priority support

To get started: [premium@incy.cc](mailto:premium@incy.cc)

---

## Payment methods

### SBP (Overpay)

Payment via the Faster Payments System in rubles. The USD→RUB rate is fixed.

### Cryptocurrency (Heleket)

Payment in USD via cryptocurrency (USDT, BTC, etc.).

---

## Account linking

To pay through the Telegram bot, the provider links their account:

1. Go to [web panel → Billing](https://web.incy-panel.com/billing)
2. Click the **Sign in with Telegram** button (Telegram Login Widget)
3. Confirm the link

After linking, payment is available through the bot: `/premium` or [t.me/incyhelperbot?start=premium](https://t.me/incyhelperbot?start=premium)

---

## Managing a subscription

### Renewal

The provider chooses a period (1/3/6 months) → payment method → pays.
The time is added to the current term (not from the moment of payment).

### Buying more devices

Available only with an active subscription. The surcharge is calculated proportionally to the remaining time:

```
surcharge = (new_devices - current) × rate × (remaining_days / 30)
```

The subscription term does not change when buying more devices. The number of devices cannot be reduced.

### Expiration notifications

Automatic Telegram reminders: 7 days, 3 days, 1 day before, and on the day of expiration.

---

## Web panel: billing page

Available at `/billing` in the web panel:

- Current plan (devices, cost, expiration date, rate)
- Telegram linking
- Cost calculator (slider 100–10,000 devices)
- Enterprise block (for >10,000)
- Payment history

---

## Administration

### Via the Telegram bot

`/admin` → **Provider Billing** → enter Telegram ID:

- View the provider card
- Set the device count (no limits)
- Set a custom rate
- Enable/disable Enterprise

### Via the web panel

`/admin/providers` → select a provider:

- Set Premium status and expiration date
- Set the device limit
- View Telegram linking
- View the plan and last payment
