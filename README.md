# WhatsApp-based Expense Tracker

## Problem Statement:
Managing daily expenses can be tedious and often requires users to manually note down transactions in spreadsheets or apps, which disrupts their natural workflow.

## Objective:
Build a WhatsApp-integrated chatbot that allows users to record, manage, and summarize expenses directly through WhatsApp with real-time confirmations, automated daily summaries, and secure storage using Supabase.

## Target Audience:

Individuals who want a quick and hassle-free way to track personal expenses.
Students and professionals who prefer expense tracking without installing extra apps.
Small groups or families needing a lightweight expense management solution.


##  Features

* **WhatsApp Integration (Twilio API)**
  Add expenses directly through WhatsApp messages.

* **Smart AI Categorization (OpenAI API)**
  Automatically groups expenses into categories like *Groceries, Electronics, Food, Transport,* etc.

* **Secure Cloud Storage (Supabase)**
  All expenses linked to your WhatsApp number and stored securely.

* **Daily & Weekly Reports**
  Automated **cron jobs** deliver expense summaries with total + category breakdown.

* **Web Dashboard (FastAPI + Jinja2)**
  View insights for today, last 7 days, and last 30 days.

* **Authentication with OTP (TOTP + JWT)**
  Login using WhatsApp-based OTP for secure access.

* **Account Controls**
  Update name/email, delete account, or export data anytime.

---

##  Tech Stack

* **Backend:** FastAPI
* **Database:** Supabase (Postgres)
* **Messaging:** Twilio WhatsApp API
* **AI Categorization:** OpenAI GPT models
* **Scheduling:** APScheduler (AsyncIO)
* **Frontend:** Jinja2 Templates (Dashboard, Settings, Login, Guidelines, About)
* **Auth & Security:** TOTP (pyotp), JWT Tokens, dotenv

---

##  Project Structure

```
├── src/
│   ├── config/         # Database setup with Supabase
│   ├── integrations/   # Twilio & OpenAI helpers
│   ├── routes/         # FastAPI routers (auth, dashboard, whatsapp webhook)
│   ├── services/       # Cron jobs, user registration
│   └── util_functions/ # Utilities (parsers, formatters, OTP, JWT)
├── templates/          # Frontend HTML (dashboard, login, settings, about, etc.)
├── cronjob.py          # Daily summary scheduler
├── main.py             # FastAPI app entry point
```

---

##  Example Usage

1. **Send an expense via WhatsApp:**

   ```
   Apple 50
   Wheat 5kg 100
   Coffee 120
   ```

2. **Get instant help via commands:**

   ```
   /help
   /totalexpenseoftoday
   /categorize_items
   /delete_account
   ```

3. **Receive daily summary (auto):**

   ```
   Today's Expenses:
   Apple - ₹50
   Wheat 5kg - ₹100
   Coffee - ₹120
   -------------------------
   Total = ₹270
   ```

4. **Category breakdown (AI-powered):**

   ```
    Today's Category Breakdown:
   Groceries: ₹150
   Beverages: ₹120
   -------------------------
   Total = ₹270
   ```

---

##  Getting Started

1. Clone repo

   ```bash
   git clone https://github.com/AshwinBhaskaran42/Expense-Tracker.git
   cd whatsapp-expense-tracker
   ```

2. Setup environment

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure `.env` (Supabase, Twilio, OpenAI, Secret Keys).

4. Run server

   ```bash
   uvicorn main:app --reload
   ```

---
