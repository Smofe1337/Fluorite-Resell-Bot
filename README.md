<div align="center">

# Fluorite Resell Bot

### Telegram Bot for Automated Fluorite Subscription Sales

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://aiogram.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)

**[English](#english)** | **[Русский](#русский)**

</div>

---

<a id="english"></a>

## Overview

Fluorite Resell Bot is a ready-to-deploy Telegram bot built for Fluorite resellers. It fully automates subscription sales — customers browse the catalog, choose a game and duration, pay through one of the supported methods, and instantly receive their key. No manual work required.

Integrated with the Fluorite Dashboard API, the bot manages keys, HWID resets, and bans directly through the platform. A built-in admin panel gives resellers full control over their business.

## Why Use This

- **Fully automated** — set it up once and it runs 24/7 without intervention
- **Instant delivery** — keys are issued the moment payment is confirmed
- **Multiple payment options** — crypto (CryptoBot), fiat (AAIO, NicePay), or in-app balance
- **Built-in referral program** — customers bring new customers, rewards grow with each milestone
- **Anti-abuse protection** — rate limiting, captcha, automatic bans for bot attacks
- **Admin dashboard** — manage everything from a modern web panel
- **Multi-language** — Russian and English out of the box

## Features

### Customer Side
- **Game Catalog** — browse supported games with 1-day, 7-day, and 30-day subscription options
- **Flexible Payments** — CryptoBot (crypto), AAIO (fiat), NicePay, or wallet balance
- **Gift Keys** — buy a subscription as a shareable gift link
- **Referral Program** — earn escalating bonuses for every 10 invited users
- **HWID Reset** — reset hardware binding directly from the bot
- **Order History** — full purchase history with statuses and key details
- **Coupons** — redeem promo codes for free keys or balance top-ups

### Admin Dashboard
- **User Management** — search users, adjust balances, ban/unban, set VIP status
- **Game Management** — add/edit games, upload images, set prices (USD, auto-converted), toggle visibility
- **Key Inventory** — add keys individually or bulk import, monitor stock (available / sold / pending)
- **Order Tracking** — search, filter by status, paginated order list
- **Staff Accounts** — multiple admin logins with JWT authentication

### Security
- **Referral Guard** — rate limiting with automatic captcha on suspicious activity
- **Attack Detection** — auto-ban + key blocking on referral abuse, $100 unban fee via CryptoBot invoice
- **Webhook Verification** — HMAC-SHA-256 (CryptoBot), hash signing (AAIO/NicePay)
- **IP Whitelisting** — payment webhook source validation
- **JWT Auth** — secure dashboard access

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Bot | Aiogram 3.21 (async Telegram framework) |
| API | FastAPI + Uvicorn |
| Database | PostgreSQL + SQLAlchemy 2.0 (async) |
| Dashboard | React 18 + Vite + Tailwind CSS + shadcn/ui |
| Payments | CryptoBot (webhook) / AAIO / NicePay |
| Key Platform | Fluorite Dashboard API |
| Auth | PyJWT + bcrypt |

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Fluorite reseller API key

### 1. Clone the repository

```bash
git clone https://github.com/Smofe1337/Fluorite-Resell-Bot.git
cd Fluorite-Resell-Bot
```

### 2. Install Python dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Install dashboard dependencies

```bash
cd dashboard
npm install
cd ..
```

### 4. Set up the database

Create a PostgreSQL database:

```sql
CREATE DATABASE fluorite_bot;
```

Tables are created automatically on first launch.

### 5. Configure environment variables

Create a `.env` file in the root directory:

```env
# Telegram
BOT_TOKEN=your_telegram_bot_token
BOT_SECRET=your_base64_encoded_secret

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fluorite_bot

# CryptoBot
CRYPTO_BOT=your_cryptobot_api_token

# AAIO
AAIO_MERCHANT_ID=your_merchant_id
AAIO_SECRET_KEY_1=your_secret_key_1
AAIO_SECRET_KEY_2=your_secret_key_2
AAIO_API_KEY=your_api_key

# NicePay
NICEPAY_MERCHANT_ID=your_merchant_id
NICEPAY_SECRET_KEY=your_secret_key

# Fluorite
FLUORITE_API=your_fluorite_reseller_api_key

# Dashboard
SECRET=your_jwt_secret_key
```

### 6. Configure the bot

Edit `config.py`:

| Setting | Description |
|---------|-------------|
| `BOT_BASE_URL` | Your bot's Telegram link (e.g. `t.me/YourBot`) |
| `ADMIN_LINK` | Admin contact link for support |
| `ADMINS_IDS` | List of admin Telegram user IDs |
| `OWNER_ID` | Primary owner's Telegram ID |
| `UPDATE_CHANNEL` | Telegram channel ID for update notifications |
| `BASE_URL_CB` | CryptoBot API URL — `https://testnet-pay.crypt.bot/api/` for testing, `https://pay.crypt.bot/api/` for production |

### 7. Launch

```bash
# Start bot + API server
python main.py

# In a separate terminal — start dashboard
cd dashboard
npm run dev
```

Bot starts polling, API runs on `http://127.0.0.1:1337`, dashboard on `http://localhost:8000`.

### 8. Create an admin account

```bash
curl -X POST http://127.0.0.1:1337/api/dashboard/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Log in at `http://localhost:8000`.

### 9. Set up payment webhooks

Your API must be reachable from the internet for payment confirmations. For local development, you can use ngrok:

```bash
ngrok http 1337
```

In production, use a reverse proxy (e.g. nginx) pointing to your API.

Configure these webhook URLs in each payment provider's settings:

| Provider | Webhook URL |
|----------|------------|
| CryptoBot | `https://your-domain/api/cryptobot/` |
| AAIO | `https://your-domain/api/aaio/` |
| NicePay | `https://your-domain/api/nicepay/` |

## Getting Started

### Add games to the catalog

1. Open dashboard → **Game Management**
2. Create a game — set name, image, and pricing in USD
3. Prices auto-convert to the customer's local currency

### Stock keys

1. Go to **Keys Management**
2. Add keys individually or bulk import
3. Select the game and duration (1 / 7 / 30 days)
4. Keys are automatically delivered to buyers upon payment

### Manage customers

1. Go to **User Management**
2. Search by Telegram ID, username, or display name
3. Adjust balance, toggle VIP status, ban/unban

## Project Structure

```
Fluorite-Resell-Bot/
├── main.py                     # Entry point
├── config.py                   # Bot & API configuration
├── bot/
│   ├── handlers/               # Telegram message & callback handlers
│   │   ├── referral_system.py  # Referral program with anti-abuse
│   │   ├── paymethod/          # Payment flow handlers
│   │   └── orders/             # Order history & cancellation
│   ├── api/                    # FastAPI backend
│   │   ├── app.py              # App setup & router registration
│   │   ├── payments/hooks/     # Payment webhook endpoints
│   │   └── dashboard/          # Admin panel API
│   ├── database/               # Data layer
│   │   ├── models/             # SQLAlchemy models
│   │   ├── repository/         # Database queries
│   │   └── service/            # Business logic
│   ├── payments/               # Payment provider clients
│   ├── security/               # Referral guard, captcha
│   ├── external/               # Fluorite API integration
│   ├── localization/locales/   # en.json, ru.json
│   └── commands/               # /start, /help handlers
└── dashboard/                  # React admin panel
    └── src/
        ├── pages/              # Login, Admin
        └── components/         # User/Game/Key/Order management
```

---

<a id="русский"></a>

<div align="center">

## Русский

</div>

## Обзор

Fluorite Resell Bot — готовый к деплою Telegram-бот для реселлеров Fluorite. Полностью автоматизирует продажу подписок — клиенты выбирают игру и срок, оплачивают удобным способом и мгновенно получают ключ. Никакой ручной работы.

Бот интегрирован с Fluorite Dashboard API — управление ключами, сброс HWID и баны выполняются напрямую через платформу. Встроенная админ-панель даёт полный контроль над бизнесом.

## Преимущества

- **Полная автоматизация** — настройте один раз, бот работает 24/7 без вмешательства
- **Мгновенная выдача** — ключ приходит в момент подтверждения оплаты
- **Несколько способов оплаты** — крипта (CryptoBot), фиат (AAIO, NicePay), внутренний баланс
- **Реферальная программа** — клиенты приводят новых клиентов, бонусы растут с каждым этапом
- **Защита от злоупотреблений** — лимиты, капча, автоматические баны за бот-атаки
- **Админ-панель** — управляйте всем через современный веб-интерфейс
- **Мультиязычность** — русский и английский из коробки

## Возможности

### Для клиентов
- **Каталог игр** — поддерживаемые игры с подписками на 1 день, 7 дней и 30 дней
- **Гибкая оплата** — CryptoBot (крипта), AAIO (фиат), NicePay или баланс кошелька
- **Подарочные ключи** — купите подписку в виде подарочной ссылки
- **Реферальная программа** — растущие бонусы за каждые 10 приглашённых пользователей
- **Сброс HWID** — сброс привязки к устройству прямо из бота
- **История заказов** — полная история покупок со статусами и ключами
- **Купоны** — промокоды на бесплатные ключи или пополнение баланса

### Админ-панель
- **Пользователи** — поиск, управление балансом, баны, VIP-статус
- **Игры** — добавление/редактирование, загрузка изображений, цены в USD (автоконвертация), видимость
- **Склад ключей** — добавление по одному или массовый импорт, мониторинг наличия
- **Заказы** — поиск, фильтрация по статусу, пагинация
- **Персонал** — несколько админ-аккаунтов с JWT-аутентификацией

### Безопасность
- **Защита рефералов** — лимиты частоты с автоматической капчей при подозрительной активности
- **Детекция атак** — автобан + блокировка ключей при злоупотреблении, разбан за $100 через CryptoBot
- **Верификация вебхуков** — HMAC-SHA-256 (CryptoBot), хеш-подпись (AAIO/NicePay)
- **Белый список IP** — валидация источника платёжных вебхуков
- **JWT-авторизация** — защищённый доступ к панели

## Установка

### Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- API-ключ реселлера Fluorite

### 1. Клонирование

```bash
git clone https://github.com/Smofe1337/Fluorite-Resell-Bot.git
cd Fluorite-Resell-Bot
```

### 2. Python-зависимости

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Зависимости дашборда

```bash
cd dashboard
npm install
cd ..
```

### 4. База данных

```sql
CREATE DATABASE fluorite_bot;
```

Таблицы создаются автоматически при первом запуске.

### 5. Переменные окружения

Создайте `.env` в корне проекта:

```env
# Telegram
BOT_TOKEN=токен_бота
BOT_SECRET=секрет_в_base64

# База данных
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fluorite_bot

# CryptoBot
CRYPTO_BOT=токен_cryptobot

# AAIO
AAIO_MERCHANT_ID=merchant_id
AAIO_SECRET_KEY_1=секретный_ключ_1
AAIO_SECRET_KEY_2=секретный_ключ_2
AAIO_API_KEY=api_ключ

# NicePay
NICEPAY_MERCHANT_ID=merchant_id
NICEPAY_SECRET_KEY=секретный_ключ

# Fluorite
FLUORITE_API=api_ключ_реселлера

# Дашборд
SECRET=секрет_jwt
```

### 6. Конфигурация

Отредактируйте `config.py`:

| Параметр | Описание |
|----------|----------|
| `BOT_BASE_URL` | Ссылка на бота (например `t.me/YourBot`) |
| `ADMIN_LINK` | Ссылка на админа для поддержки |
| `ADMINS_IDS` | Список Telegram ID администраторов |
| `OWNER_ID` | Telegram ID владельца |
| `UPDATE_CHANNEL` | ID канала для уведомлений |
| `BASE_URL_CB` | URL API CryptoBot — `https://testnet-pay.crypt.bot/api/` для тестов, `https://pay.crypt.bot/api/` для прода |

### 7. Запуск

```bash
# Бот + API
python main.py

# В отдельном терминале — дашборд
cd dashboard
npm run dev
```

Бот: polling, API: `http://127.0.0.1:1337`, дашборд: `http://localhost:8000`.

### 8. Создание админа

```bash
curl -X POST http://127.0.0.1:1337/api/dashboard/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ваш_пароль"}'
```

Войдите на `http://localhost:8000`.

### 9. Настройка вебхуков

API должен быть доступен из интернета. Для локальной разработки можно использовать ngrok:

```bash
ngrok http 1337
```

На проде используйте обратный прокси (например nginx), направленный на API.

Настройте URL вебхуков у провайдеров:

| Провайдер | URL вебхука |
|-----------|------------|
| CryptoBot | `https://ваш-домен/api/cryptobot/` |
| AAIO | `https://ваш-домен/api/aaio/` |
| NicePay | `https://ваш-домен/api/nicepay/` |

## Начало работы

### Добавление игр

1. Дашборд → **Game Management**
2. Создайте игру — название, изображение, цены в USD
3. Цены автоматически конвертируются в валюту клиента

### Загрузка ключей

1. **Keys Management**
2. Добавьте ключи по одному или массовым импортом
3. Выберите игру и срок (1 / 7 / 30 дней)
4. Ключи автоматически выдаются покупателям после оплаты

### Управление клиентами

1. **User Management**
2. Поиск по Telegram ID, юзернейму или имени
3. Баланс, VIP-статус, бан/разбан

