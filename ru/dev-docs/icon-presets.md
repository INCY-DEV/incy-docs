# Пресет-иконки ссылок

Иконки, которые отображаются рядом с ссылками **Бот / Канал / Поддержка** в карточке подписки (режим `liteMode`). Провайдер выбирает иконку по ключу из пресет-набора — каждая платформа (Android, iOS, Desktop) маппит этот ключ на свою нативную иконку.

Зачем так, а не URL картинки:

- **Единый внешний вид на всех платформах** — иконки из системного набора (Material Icons, SF Symbols) подстраиваются под тему.
- **Ноль сетевых запросов в клиенте** — ключ это просто строка в `settings`.
- **Поддержка в офлайне** — приложение работает даже без связи с сервером.

---

## Где задаётся

Провайдер выбирает иконку в [веб-панели](https://web.incy-panel.com) для каждого домена в блоке **Lite Mode**. Значения сохраняются в `SubscriptionSettings`:

| Поле              | Тип       | Описание                            |
|-------------------|-----------|-------------------------------------|
| `botIconKey`      | `string?` | Ключ иконки для `botUrl`            |
| `channelIconKey`  | `string?` | Ключ иконки для `channelUrl`        |
| `supportIconKey`  | `string?` | Ключ иконки для `supportUrl`        |

Возвращаются клиенту через [Premium API](premium-api.md) в объекте `settings`.

---

## Поведение клиента

- **Ключ задан и известен** → клиент рендерит соответствующую нативную иконку.
- **Ключ пустой (`null` / `""`)** → fallback на дефолтную иконку слота:
  - `botUrl` → `send` (бумажный самолётик)
  - `channelUrl` → `megaphone` (рупор)
  - `supportUrl` → `help` (вопросительный знак)
- **Ключ задан, но неизвестен клиенту** (старая версия приложения + новый ключ) → fallback на тот же дефолт.

---

## Полный список пресетов

Всего 20 ключей. Имя ключа **стабильно** — один раз опубликованный ключ не переименовывается.

### Бот / сообщения

| Ключ         | Превью | Назначение                         |
|--------------|:------:|------------------------------------|
| `send`       |  ✈️   | Бумажный самолётик (по умолчанию для `botUrl`) |
| `bot`        |  🤖   | Робот                              |
| `chat`       |  💬   | Речевое облачко                    |
| `message`    |  ✉️   | Конверт (открытое сообщение)       |
| `mail`       |  📧   | Почта                              |

### Новости / вещание

| Ключ         | Превью | Назначение                         |
|--------------|:------:|------------------------------------|
| `megaphone`  |  📢   | Рупор (по умолчанию для `channelUrl`) |
| `bell`       |  🔔   | Колокольчик                        |
| `newspaper`  |  📰   | Газета                             |
| `rss`        |  📡   | RSS                                |
| `broadcast`  |  📻   | Антенна / радио                    |

### Поддержка / справка

| Ключ         | Превью | Назначение                         |
|--------------|:------:|------------------------------------|
| `help`       |  ❓   | Вопрос (по умолчанию для `supportUrl`) |
| `support`    |  🎧   | Агент поддержки                    |
| `lifebuoy`   |  🛟   | Спасательный круг                  |
| `info`       |  ℹ️   | Информация                         |
| `book`       |  📖   | Книга / FAQ                        |

### Акцентные

| Ключ     | Превью | Назначение              |
|----------|:------:|-------------------------|
| `crown`  |  👑   | Корона                  |
| `star`   |  ⭐   | Звезда                  |
| `gem`    |  💎   | Алмаз                   |
| `rocket` |  🚀   | Ракета                  |
| `heart`  |  ❤️   | Сердце                  |

---

## Маппинг на нативные иконки

Для справки — какие нативные иконки рендерятся на каждой платформе. Добавлять / менять маппинг нужно одновременно в трёх клиентах + web-панели.

| Ключ         | Material Icons (Android / Desktop) | SF Symbols (iOS)                               |
|--------------|------------------------------------|------------------------------------------------|
| `send`       | `Send`                             | `paperplane.fill`                              |
| `bot`        | `SmartToy`                         | `apps.iphone`                                  |
| `chat`       | `Chat`                             | `bubble.left.fill`                             |
| `message`    | `Message`                          | `message.fill`                                 |
| `mail`       | `Email`                            | `envelope.fill`                                |
| `megaphone`  | `Campaign`                         | `megaphone.fill`                               |
| `bell`       | `Notifications`                    | `bell.fill`                                    |
| `newspaper`  | `Newspaper`                        | `newspaper.fill`                               |
| `rss`        | `RssFeed`                          | `dot.radiowaves.left.and.right`                |
| `broadcast`  | `Podcasts`                         | `antenna.radiowaves.left.and.right`            |
| `help`       | `HelpOutline`                      | `questionmark.circle`                          |
| `support`    | `SupportAgent`                     | `person.fill.questionmark`                     |
| `lifebuoy`   | `MedicalServices`                  | `lifepreserver`                                |
| `info`       | `Info`                             | `info.circle`                                  |
| `book`       | `MenuBook`                         | `book.fill`                                    |
| `crown`      | `EmojiEvents`                      | `crown.fill`                                   |
| `star`       | `Star`                             | `star.fill`                                    |
| `gem`        | `Diamond`                          | `diamond.fill`                                 |
| `rocket`     | `RocketLaunch`                     | `paperplane.fill`                              |
| `heart`      | `Favorite`                         | `heart.fill`                                   |

---

## Пример

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

В карточке подписки пользователь увидит три кнопки: робот (бот), рупор (канал), спасательный круг (поддержка).
