# VPN Auction

A weekly auction for placing VPN service ads in the "Recommended VPN" channel.

## Overview

VPN service providers bid to get into the channel's top 10 recommendations. Winners get their ad placed for a week.

---

## How it works

### For participants

1. Open the bot: [@incyhelperbot](https://t.me/incyhelperbot)
2. `/start` → **VPN Auction**
3. Top up your balance (SBP via Kassai/FreeKassa or cryptocurrency via CryptoPay)
4. Place a bid
5. Create an ad (title, description, link)
6. Wait for the auction to end

### Auction cycle

| Stage | Description |
| --- | --- |
| Monday | A new auction opens |
| During the week | Participants place bids |
| Sunday | The auction ends at a random time between 20:00 and 22:00 (MSK) |
| After it ends | The top 10 get placement; the rest get a refund to their bot balance for participating in future auctions |

The end time is chosen randomly to protect against sniping (last-second bids).

The auction balance cannot be used to pay for Premium.

---

## Bids

### Rules

- One active bid per user per week
- A bid locks funds on the balance (escrow)
- You can raise a bid — the difference is deducted from the balance
- If pushed out of the top 10 — a full refund to the bot balance
- The minimum raise step is configured by the administrator

### Top 10

The ranking is by bid size (highest to lowest). When all 10 slots are filled, a new bid must be higher than the lowest one in the top.

When pushed out, the user gets:
- A Telegram notification
- A full refund of the locked funds

---

## Ads

Each participant can create an ad:

| Field | Limit |
| --- | --- |
| Title | up to 100 characters |
| Description | up to 200 characters |
| Link | HTTP/HTTPS or t.me/ |

The ad is displayed in the channel upon winning. It can be changed at any time.

---

## Results

### In the channel

After the auction ends, a showcase of the winners' ads is published to the channel:

- Top 3 — with medals (🥇🥈🥉)
- Places 4–10 — with numbers
- Each line is a clickable link to the service

Format: `🥇 Title - Description` (the entire line is a link)

### During the auction

- Nothing is published to the channel
- Participants see the ranking only in the bot
- Participant IDs are masked (first 4 digits)

---

## Balance

### Top-up

- **Kassai/FreeKassa** (SBP) — the user enters an amount in dollars; payment is charged in rubles at the current rate
- **CryptoPay** (Telegram Crypto Bot) — in cryptocurrency

### Fund movement

| Operation | Balance |
| --- | --- |
| Top-up | + |
| Bid | − (lock) |
| Bid raise | − (pay the difference) |
| Pushed out of top 10 | + (refund) |
| Lost the auction | + (refund) |
| Won the auction | funds are charged permanently |

---

## Notifications

Participants receive Telegram notifications:

- Pushed out of the top 10 (with the refund amount)
- Win (place and amount)
- Loss (with refund)

---

## Administration

Via the bot (`/admin`):

- View auction statistics (participants, bids, locked funds)
- End the auction early
- Adjust users' balances

---

## Who will see the ad

INCY app users without a premium subscription see the "Where can I get servers?" section in the app settings (the "About" screen). Tapping it takes them to the channel with the auction results.

Channel: [@recommended_vpn](https://t.me/recommended_vpn)
