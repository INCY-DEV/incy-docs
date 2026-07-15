# Link Icon Presets

Icons shown next to the **Bot / Channel / Support** links in the subscription card (`liteMode` mode). The provider picks an icon by key from a preset set — each platform (Android, iOS, Desktop) maps that key to its own native icon.

Why this approach instead of an image URL:

- **Consistent appearance across all platforms** — icons from the system set (Material Icons, SF Symbols) adapt to the theme.
- **Zero network requests in the client** — the key is just a string in `settings`.
- **Offline support** — the app works even without a server connection.

---

## Where it's set

The provider picks the icon in the [web panel](https://web.incy-panel.com) for each domain in the **Lite Mode** block. Values are stored in `SubscriptionSettings`:

| Field             | Type      | Description                         |
|-------------------|-----------|-------------------------------------|
| `botIconKey`      | `string?` | Icon key for `botUrl`               |
| `channelIconKey`  | `string?` | Icon key for `channelUrl`           |
| `supportIconKey`  | `string?` | Icon key for `supportUrl`           |

Returned to the client through the [Premium API](premium-api.md) in the `settings` object.

---

## Client behavior

- **Key set and known** → the client renders the corresponding native icon.
- **Key empty (`null` / `""`)** → fallback to the slot's default icon:
  - `botUrl` → `send` (paper plane)
  - `channelUrl` → `megaphone` (bullhorn)
  - `supportUrl` → `help` (question mark)
- **Key set but unknown to the client** (old app version + new key) → fallback to the same default.

---

## Full preset list

20 keys in total. The key name is **stable** — once a key is published it is never renamed.

### Bot / messages

| Key          | Preview | Purpose                            |
|--------------|:------:|------------------------------------|
| `send`       |  ✈️   | Paper plane (default for `botUrl`)  |
| `bot`        |  🤖   | Robot                              |
| `chat`       |  💬   | Speech bubble                      |
| `message`    |  ✉️   | Envelope (opened message)          |
| `mail`       |  📧   | Mail                               |

### News / broadcast

| Key          | Preview | Purpose                            |
|--------------|:------:|------------------------------------|
| `megaphone`  |  📢   | Bullhorn (default for `channelUrl`) |
| `bell`       |  🔔   | Bell                               |
| `newspaper`  |  📰   | Newspaper                          |
| `rss`        |  📡   | RSS                                |
| `broadcast`  |  📻   | Antenna / radio                    |

### Support / help

| Key          | Preview | Purpose                            |
|--------------|:------:|------------------------------------|
| `help`       |  ❓   | Question (default for `supportUrl`) |
| `support`    |  🎧   | Support agent                      |
| `lifebuoy`   |  🛟   | Lifebuoy                           |
| `info`       |  ℹ️   | Information                        |
| `book`       |  📖   | Book / FAQ                         |

### Accent

| Key      | Preview | Purpose                 |
|----------|:------:|-------------------------|
| `crown`  |  👑   | Crown                   |
| `star`   |  ⭐   | Star                    |
| `gem`    |  💎   | Diamond                 |
| `rocket` |  🚀   | Rocket                  |
| `heart`  |  ❤️   | Heart                   |

---

## Mapping to native icons

For reference — which native icons are rendered on each platform. Adding / changing a mapping must be done simultaneously in all three clients + the web panel.

| Key          | Material Icons (Android / Desktop) | SF Symbols (iOS)                               |
|--------------|------------------------------------|------------------------------------------------|
| `send`       | `Send`                             | `paperplane.fill`                              |
| `bot`        | `SmartToy`                         | `cpu`                                          |
| `chat`       | `Chat`                             | `bubble.left.fill`                             |
| `message`    | `Message`                          | `message.fill`                                 |
| `mail`       | `Email`                            | `envelope.fill`                                |
| `megaphone`  | `Campaign`                         | `megaphone.fill`                               |
| `bell`       | `Notifications`                    | `bell.fill`                                    |
| `newspaper`  | `Newspaper`                        | `newspaper.fill`                               |
| `rss`        | `RssFeed`                          | `dot.radiowaves.left.and.right`                |
| `broadcast`  | `Podcasts`                         | `mic.fill`                                     |
| `help`       | `HelpOutline`                      | `questionmark.circle`                          |
| `support`    | `SupportAgent`                     | `headphones`                                   |
| `lifebuoy`   | `MedicalServices`                  | `lifepreserver`                                |
| `info`       | `Info`                             | `info.circle`                                  |
| `book`       | `MenuBook`                         | `book.fill`                                    |
| `crown`      | `EmojiEvents`                      | `crown.fill`                                   |
| `star`       | `Star`                             | `star.fill`                                    |
| `gem`        | `Diamond`                          | `diamond.fill`                                 |
| `rocket`     | `RocketLaunch`                     | `flame.fill`                                   |
| `heart`      | `Favorite`                         | `heart.fill`                                   |

---

## Example

```json
{
  "settings": {
    "liteMode": true,
    "botUrl": "https://t.me/my_bot",
    "botIconKey": "bot",
    "channelUrl": "https://t.me/my_channel",
    "channelIconKey": "megaphone",
    "supportUrl": "https://t.me/my_support",
    "supportIconKey": "lifebuoy"
  }
}
```

In the subscription card the user will see three buttons: robot (bot), bullhorn (channel), lifebuoy (support).
