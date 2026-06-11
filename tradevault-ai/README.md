# TRADEVAULT AI

A professional full-stack SaaS trading journal platform built with **Flask + SQLite + HTML/CSS/JS**.

## What Is This?

TradeVault AI is a complete trading management platform for serious traders:

- **Journal** every trade with detailed metrics (P&L, R-multiple, psychology notes)
- **Store strategies** with entry/exit/risk rules
- **Backtest** and record performance statistics
- **Learn** from a 48-lesson curriculum (7 modules)
- **Track progress** with weekly goals and dashboard analytics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ / Flask |
| Database | SQLite |
| Frontend | HTML5 / CSS3 / Vanilla JS |
| Auth | Flask-Login + Werkzeug (bcrypt) |
| Styling | Custom CSS (Dark Fintech Theme) |

## Project Structure

```
tradevault-ai/
├── app.py                    # Main Flask app — all routes & logic
├── requirements.txt          # Python dependencies
├── database/
│   ├── schema.sql            # Full SQLite schema (tables, indexes, FKs)
│   ├── init_db.py            # Seed script (7 modules, 48 lessons)
│   └── tradevault.db         # Auto-created on first run
├── templates/                # Jinja2 HTML templates
│   ├── base.html             # Master layout (nav, sidebar, flashes)
│   ├── index.html            # Futuristic landing page with canvas animation
│   ├── login.html            # Sign in page
│   ├── signup.html           # Registration page
│   ├── dashboard.html        # Main dashboard with stats & equity chart
│   ├── journal.html          # Trade list with filters
│   ├── journal_form.html     # Create/edit trade form
│   ├── strategies.html       # Strategy vault grid
│   ├── strategy_form.html    # Create/edit strategy form
│   ├── backtest.html         # Backtest records list
│   ├── backtest_form.html    # New backtest form
│   ├── learning.html         # Learning modules & lessons
│   ├── lesson.html           # Single lesson view
│   ├── goals.html            # Weekly goals management
│   └── profile.html          # User profile & stats
├── static/
│   ├── css/
│   │   └── style.css         # Complete dark fintech theme
│   └── js/
│       └── app.js            # Frontend interactions
└── README.md                 # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python database/init_db.py
```

This creates `database/tradevault.db` and seeds:
- 7 Learning Modules
- 48 Lessons (full curriculum)

### 3. Run the App

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### 4. Create Account

Click **Get Started** on the landing page and sign up. All features are unlocked after login.

## Features Breakdown

### Authentication
- Secure registration with bcrypt password hashing
- Session-based login via Flask-Login
- Protected routes (login required for all app pages)

### Trading Journal
- Log trades: pair, direction, entry/exit prices, stop loss, take profit
- Auto-calculate P&L and R-multiple when exit price provided
- Tag trades, add screenshots, psychology notes
- Filter by status, direction, pair
- Edit/delete any trade

### Strategy Vault
- Create strategies with name, market type, timeframe
- Document entry rules, exit rules, risk rules
- Archive/restore strategies (soft delete)
- Link strategies to backtests

### Backtesting Buddy
- Record backtest results: date range, pair, trade count
- Track win rate, profit factor, max drawdown, total return
- Visual balance progression display
- Link to existing strategies

### Learning Hub
- 7 modules: Basics → Risk → Psychology → TA → Strategy → Backtest → Advanced
- 48 lessons with structured content
- Progress tracking per user
- Mark lessons complete, auto-advance to next

### Dashboard
- Total trades, win rate, net P&L, open positions
- Strategies count, backtests count
- Learning progress ring
- Recent trades table
- Weekly goals progress bars
- Equity curve chart (Canvas-based)

### Weekly Goals
- Set process-based targets (not profit-based)
- Track progress with visual bars
- Auto-complete when target reached

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Accounts (id, username, email, password_hash) |
| `trades` | Journal entries with full trade details |
| `strategies` | Trading strategy definitions |
| `backtests` | Strategy validation records |
| `learning_modules` | Course modules (pre-seeded) |
| `learning_lessons` | Individual lessons (pre-seeded) |
| `user_progress` | Lesson completion tracking |
| `weekly_goals` | User-defined weekly targets |

All tables use foreign keys and cascading deletes where appropriate.

## Security

- Passwords hashed with `werkzeug.security` (PBKDF2-SHA256)
- Session management via Flask-Login
- SQL injection protection via parameterized queries
- CSRF-ready structure (can add Flask-WTF easily)

## Deployment

### Local (Development)
```bash
python app.py
```

### Production
1. Set `SECRET_KEY` environment variable
2. Use a production WSGI server (Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
3. Use a reverse proxy (Nginx) for SSL
4. Consider migrating to PostgreSQL for scale

## Customization

- **Colors**: Edit CSS variables in `static/css/style.css` (top of file)
- **Logo**: Replace icon classes in templates
- **Lessons**: Edit `database/init_db.py` lesson content arrays
- **Fields**: Add columns to `schema.sql` and update forms in templates

## License

MIT — Built for traders, by traders.

---

**TradeVault AI** — *Journal. Analyze. Improve. Dominate.*
