# Penny's Bazaar – Extended Setup Guide

## What's New

| Feature | Details |
|---|---|
| 💳 Stripe Payments | Hosted Checkout + PaymentIntent + Webhook handler |
| 📧 Email Notifications | Order confirmation, shipping update, 2-week survey |
| 📊 Analytics Dashboard | Revenue, orders, conversion, top products, low-stock alerts |
| 🤖 Penny AI Chat | Claude-powered customer chat widget (bottom-right corner) |

---

## 1. Install Dependencies

```bash
pip install flask flask-cors apscheduler stripe anthropic
```

---

## 2. Environment Variables

Create a `.env` file (or export in your shell):

```bash
# Stripe (get from https://dashboard.stripe.com/apikeys)
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."   # from Stripe CLI / dashboard

# Email (Gmail example – use an App Password, not your real password)
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="you@gmail.com"
export SMTP_PASS="your_app_password"
export EMAIL_FROM="Penny's Bazaar <you@gmail.com>"

# Penny AI Chat (get from https://console.anthropic.com)
export ANTHROPIC_API_KEY="sk-ant-..."
```

> **Gmail tip:** Enable 2FA → Google Account → Security → App Passwords → generate one for "Mail".

---

## 3. Run

```bash
python merchandiser_bot_extended.py
```

- Shop: http://127.0.0.1:5000/
- Analytics: http://127.0.0.1:5000/analytics

---

## 4. Stripe Setup

### Test Mode (no real money)
1. Copy your test keys from https://dashboard.stripe.com/test/apikeys
2. Set `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`
3. Click "Pay with Stripe" in the shop – it'll redirect to Stripe Checkout

### Webhook (for automatic order creation after payment)
```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:5000/api/stripe/webhook
# Copy the webhook signing secret → set STRIPE_WEBHOOK_SECRET
```

### Go Live
- Swap `sk_test_` → `sk_live_` keys in production
- Flip `mode="payment"` to `mode="subscription"` for recurring billing

---

## 5. API Reference

### Products
```
GET  /api/products              → full catalog with stock
```

### Cart & Checkout
```
POST /api/penny/verify          → verify cart + get ETA
POST /api/penny/complete_order  → place order (manual payment)
POST /api/stripe/create_session → create Stripe Checkout session
POST /api/stripe/webhook        → Stripe webhook receiver
```

### Penny Chat
```
POST /api/penny/chat
Body: { "message": "Do you have noise-canceling earbuds?", "session_token": "abc123" }
```

### Analytics
```
GET  /api/analytics             → full analytics summary (JSON)
GET  /analytics                 → dashboard UI
```

### Tracking & Bot
```
GET  /api/tracking/{order_id}   → order status + ETA
GET  /api/bot/tiktok/{prod_id}  → TikTok content package
```

---

## 6. Email Flow

| Trigger | Email |
|---|---|
| Order placed | ✅ Order confirmation with items + ETA |
| Order shipped | 🚚 Shipping update with tracking link |
| 2 weeks post-delivery | 💙 Thank-you + survey + 15% discount code |

> In development the tracker runs on a fast simulation (30s ship, 60s deliver, 90s survey). Change the `time.sleep()` values in `SHTracker` and `SurveyScheduler` for production timing.

---

## 7. Analytics Dashboard

Tracks automatically:
- **page_view** – every `/api/products` call
- **add_to_cart** – every `/api/penny/verify` call
- **purchase** – every completed order
- **chat_message** – every Penny chat message

Dashboard auto-refreshes every 30 seconds.

---

## 8. Deployment Options

### Render (free tier)
1. Push to GitHub
2. New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `python merchandiser_bot_extended.py`
5. Add env vars in Render dashboard

### Railway
```bash
railway init
railway up
railway variables set STRIPE_SECRET_KEY=sk_test_...
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask flask-cors apscheduler stripe anthropic
EXPOSE 5000
CMD ["python", "merchandiser_bot_extended.py"]
```

---

## 9. Production Checklist

- [ ] Replace `app.secret_key` with a secure random value
- [ ] Replace in-memory `products_db` / `orders_db` with a real database (SQLite → PostgreSQL)
- [ ] Replace `time.sleep()` threads with proper APScheduler jobs for S&H timing
- [ ] Add authentication to `/analytics` and `/api/bot/*` routes
- [ ] Set `debug=False` in `app.run()`
- [ ] Use `gunicorn` instead of Flask dev server: `gunicorn -w 4 merchandiser_bot_extended:app`
- [ ] Configure Stripe live keys + re-register webhook endpoint URL
