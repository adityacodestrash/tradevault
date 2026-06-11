#!/usr/bin/env python3
"""
================================================================================
TRADEVAULT AI - Main Flask Application
================================================================================
A professional SaaS trading journal platform built with Flask + SQLite.

Architecture:
- app.py        : Main application entry point, all routes, business logic
- database/     : SQLite schema and initialization
- templates/    : HTML templates (Jinja2)
- static/       : CSS, JavaScript, assets

Features:
- Authentication (signup, login, logout) with bcrypt hashing
- Trading Journal (CRUD operations)
- Strategy Vault (CRUD operations)
- Backtesting Buddy (record and analyze backtests)
- Learning Hub (48 lessons across 7 modules with progress tracking)
- Dashboard (aggregated statistics and analytics)

Security:
- Passwords hashed with werkzeug.security
- Session-based authentication with flask_login
- CSRF protection via WTF forms (simplified for this version)
- SQL injection protection via parameterized queries
================================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import json

# =============================================================================
# APP CONFIGURATION
# =============================================================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tradevault-dev-secret-key-change-in-production')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database', 'tradevault.db')

# Flask-Login setup for session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# =============================================================================
# DATABASE HELPERS
# =============================================================================
def get_db():
    """Get SQLite database connection with row factory for dict-like access."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row  # Enables dict-like access to rows
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Execute a query and return results. 'one=True' returns single row."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute INSERT/UPDATE/DELETE and commit. Returns lastrowid."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# =============================================================================
# USER MODEL & AUTHENTICATION
# =============================================================================
class User(UserMixin):
    """User model for Flask-Login. Wraps database user record."""
    def __init__(self, id, username, email, created_at):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID for Flask-Login sessions."""
    row = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    if row:
        return User(row['id'], row['username'], row['email'], row['created_at'])
    return None

# =============================================================================
# CONTEXT PROCESSORS
# =============================================================================
@app.context_processor
def inject_globals():
    """Make current year and app info available in all templates."""
    return {
        'current_year': datetime.now().year,
        'app_name': 'TRADEVAULT AI'
    }

# =============================================================================
# LANDING PAGE (PUBLIC)
# =============================================================================
@app.route('/')
def index():
    """Futuristic landing page - trading-themed hero with animations."""
    return render_template('index.html')

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration with password hashing and validation."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        # Check if username/email exists
        existing = query_db('SELECT id FROM users WHERE username = ? OR email = ?', 
                           [username, email], one=True)
        if existing:
            errors.append('Username or email already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('signup.html')

        # Hash password and create user
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        user_id = execute_db(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            [username, email, password_hash]
        )

        # Auto-login after signup
        user = User(user_id, username, email, datetime.now())
        login_user(user)
        flash('Welcome to TRADEVAULT AI! Your account has been created.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with credential verification."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Find user by username or email
        row = query_db(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            [username, username], one=True
        )

        if row and check_password_hash(row['password_hash'], password):
            user = User(row['id'], row['username'], row['email'], row['created_at'])
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Log out user and clear session."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# =============================================================================
# DASHBOARD (PROTECTED)
# =============================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing aggregated trading statistics and analytics."""
    user_id = current_user.id

    # Trade statistics
    total_trades = query_db(
        'SELECT COUNT(*) as count FROM trades WHERE user_id = ?', [user_id], one=True
    )['count']

    win_count = query_db(
        'SELECT COUNT(*) as count FROM trades WHERE user_id = ? AND pnl > 0', [user_id], one=True
    )['count']

    win_rate = round((win_count / total_trades * 100), 1) if total_trades > 0 else 0

    net_pnl = query_db(
        'SELECT COALESCE(SUM(pnl), 0) as total FROM trades WHERE user_id = ?', [user_id], one=True
    )['total']

    open_positions = query_db(
        'SELECT COUNT(*) as count FROM trades WHERE user_id = ? AND status = ?', 
        [user_id, 'OPEN'], one=True
    )['count']

    total_strategies = query_db(
        'SELECT COUNT(*) as count FROM strategies WHERE user_id = ? AND is_archived = 0', 
        [user_id], one=True
    )['count']

    total_backtests = query_db(
        'SELECT COUNT(*) as count FROM backtests WHERE user_id = ?', [user_id], one=True
    )['count']

    # Recent trades (last 5)
    recent_trades = query_db(
        '''SELECT * FROM trades WHERE user_id = ? ORDER BY trade_date DESC, created_at DESC LIMIT 5''',
        [user_id]
    )

    # Learning progress
    total_lessons = query_db('SELECT COUNT(*) as count FROM learning_lessons', [], one=True)['count']
    completed_lessons = query_db(
        'SELECT COUNT(*) as count FROM user_progress WHERE user_id = ? AND completed = 1',
        [user_id], one=True
    )['count']
    learning_percent = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0

    # Weekly goals
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    goals = query_db(
        '''SELECT * FROM weekly_goals 
           WHERE user_id = ? AND week_start_date = ? 
           ORDER BY created_at DESC''',
        [user_id, week_start.strftime('%Y-%m-%d')]
    )

    # Equity curve data (last 30 trades for chart)
    equity_data = query_db(
        '''SELECT trade_date, pnl FROM trades 
           WHERE user_id = ? AND pnl IS NOT NULL 
           ORDER BY trade_date LIMIT 30''',
        [user_id]
    )

    stats = {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'net_pnl': round(net_pnl, 2),
        'open_positions': open_positions,
        'total_strategies': total_strategies,
        'total_backtests': total_backtests,
        'learning_percent': learning_percent,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons
    }

    return render_template('dashboard.html', stats=stats, recent_trades=recent_trades,
                         goals=goals, equity_data=equity_data)

# =============================================================================
# TRADING JOURNAL ROUTES
# =============================================================================
@app.route('/journal')
@login_required
def journal():
    """Trading journal page - list all trades with filters."""
    user_id = current_user.id

    # Get filter params
    status = request.args.get('status', '')
    pair = request.args.get('pair', '')
    direction = request.args.get('direction', '')

    query = 'SELECT * FROM trades WHERE user_id = ?'
    params = [user_id]

    if status:
        query += ' AND status = ?'
        params.append(status)
    if pair:
        query += ' AND pair LIKE ?'
        params.append(f'%{pair}%')
    if direction:
        query += ' AND direction = ?'
        params.append(direction)

    query += ' ORDER BY trade_date DESC, created_at DESC'

    trades = query_db(query, params)

    # Get unique pairs for filter dropdown
    pairs = query_db('SELECT DISTINCT pair FROM trades WHERE user_id = ? ORDER BY pair', [user_id])

    return render_template('journal.html', trades=trades, pairs=pairs, 
                         filters={'status': status, 'pair': pair, 'direction': direction})

@app.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_trade():
    """Create a new trade journal entry."""
    if request.method == 'POST':
        user_id = current_user.id

        # Extract form data
        trade_date = request.form.get('trade_date')
        pair = request.form.get('pair', '').upper()
        direction = request.form.get('direction')
        entry_price = float(request.form.get('entry_price', 0))
        exit_price = request.form.get('exit_price')
        stop_loss = request.form.get('stop_loss')
        take_profit = request.form.get('take_profit')
        position_size = request.form.get('position_size')
        risk_percent = request.form.get('risk_percent')
        pnl = request.form.get('pnl')
        r_multiple = request.form.get('r_multiple')
        screenshot_url = request.form.get('screenshot_url', '')
        notes = request.form.get('notes', '')
        psychology_notes = request.form.get('psychology_notes', '')
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'OPEN')

        # Auto-calculate P&L and R-Multiple if exit price provided
        if exit_price and float(exit_price) > 0:
            exit_price_f = float(exit_price)
            if direction == 'LONG':
                calculated_pnl = exit_price_f - entry_price
            else:
                calculated_pnl = entry_price - exit_price_f

            if pnl is None or pnl == '':
                pnl = calculated_pnl

            # Calculate R-Multiple if stop loss provided
            if stop_loss and float(stop_loss) > 0:
                sl = float(stop_loss)
                if direction == 'LONG':
                    risk = entry_price - sl
                else:
                    risk = sl - entry_price
                if risk != 0:
                    r_multiple = round(calculated_pnl / risk, 2)

        execute_db('''
            INSERT INTO trades (user_id, trade_date, pair, direction, entry_price, exit_price,
                              stop_loss, take_profit, position_size, risk_percent, pnl,
                              r_multiple, screenshot_url, notes, psychology_notes, tags, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [user_id, trade_date, pair, direction, entry_price, 
              float(exit_price) if exit_price else None,
              float(stop_loss) if stop_loss else None,
              float(take_profit) if take_profit else None,
              float(position_size) if position_size else None,
              float(risk_percent) if risk_percent else None,
              float(pnl) if pnl else None,
              float(r_multiple) if r_multiple else None,
              screenshot_url, notes, psychology_notes, tags, status])

        flash('Trade saved successfully!', 'success')
        return redirect(url_for('journal'))

    return render_template('journal_form.html', trade=None)

@app.route('/journal/edit/<int:trade_id>', methods=['GET', 'POST'])
@login_required
def edit_trade(trade_id):
    """Edit an existing trade entry."""
    user_id = current_user.id

    trade = query_db('SELECT * FROM trades WHERE id = ? AND user_id = ?', 
                    [trade_id, user_id], one=True)
    if not trade:
        flash('Trade not found.', 'danger')
        return redirect(url_for('journal'))

    if request.method == 'POST':
        trade_date = request.form.get('trade_date')
        pair = request.form.get('pair', '').upper()
        direction = request.form.get('direction')
        entry_price = float(request.form.get('entry_price', 0))
        exit_price = request.form.get('exit_price')
        stop_loss = request.form.get('stop_loss')
        take_profit = request.form.get('take_profit')
        position_size = request.form.get('position_size')
        risk_percent = request.form.get('risk_percent')
        pnl = request.form.get('pnl')
        r_multiple = request.form.get('r_multiple')
        screenshot_url = request.form.get('screenshot_url', '')
        notes = request.form.get('notes', '')
        psychology_notes = request.form.get('psychology_notes', '')
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'OPEN')

        # Auto-calculate if exit price changed
        if exit_price and float(exit_price) > 0:
            exit_price_f = float(exit_price)
            if direction == 'LONG':
                calculated_pnl = exit_price_f - entry_price
            else:
                calculated_pnl = entry_price - exit_price_f

            if pnl is None or pnl == '':
                pnl = calculated_pnl

            if stop_loss and float(stop_loss) > 0:
                sl = float(stop_loss)
                if direction == 'LONG':
                    risk = entry_price - sl
                else:
                    risk = sl - entry_price
                if risk != 0:
                    r_multiple = round(calculated_pnl / risk, 2)

        execute_db('''
            UPDATE trades SET
                trade_date = ?, pair = ?, direction = ?, entry_price = ?, exit_price = ?,
                stop_loss = ?, take_profit = ?, position_size = ?, risk_percent = ?, pnl = ?,
                r_multiple = ?, screenshot_url = ?, notes = ?, psychology_notes = ?, tags = ?,
                status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', [trade_date, pair, direction, entry_price,
              float(exit_price) if exit_price else None,
              float(stop_loss) if stop_loss else None,
              float(take_profit) if take_profit else None,
              float(position_size) if position_size else None,
              float(risk_percent) if risk_percent else None,
              float(pnl) if pnl else None,
              float(r_multiple) if r_multiple else None,
              screenshot_url, notes, psychology_notes, tags, status,
              trade_id, user_id])

        flash('Trade updated successfully!', 'success')
        return redirect(url_for('journal'))

    return render_template('journal_form.html', trade=trade)

@app.route('/journal/delete/<int:trade_id>', methods=['POST'])
@login_required
def delete_trade(trade_id):
    """Delete a trade entry permanently."""
    user_id = current_user.id
    execute_db('DELETE FROM trades WHERE id = ? AND user_id = ?', [trade_id, user_id])
    flash('Trade deleted.', 'info')
    return redirect(url_for('journal'))

# =============================================================================
# STRATEGY VAULT ROUTES
# =============================================================================
@app.route('/strategies')
@login_required
def strategies():
    """Strategy vault - list all saved trading strategies."""
    user_id = current_user.id
    archived = request.args.get('archived', '0')

    query = 'SELECT * FROM strategies WHERE user_id = ?'
    params = [user_id]

    if archived == '0':
        query += ' AND is_archived = 0'
    elif archived == '1':
        query += ' AND is_archived = 1'

    query += ' ORDER BY created_at DESC'

    strategies_list = query_db(query, params)
    return render_template('strategies.html', strategies=strategies_list, archived=archived)

@app.route('/strategies/new', methods=['GET', 'POST'])
@login_required
def new_strategy():
    """Create a new trading strategy."""
    if request.method == 'POST':
        user_id = current_user.id
        name = request.form.get('name', '').strip()
        market_type = request.form.get('market_type')
        timeframe = request.form.get('timeframe', '').upper()
        entry_rules = request.form.get('entry_rules', '')
        exit_rules = request.form.get('exit_rules', '')
        risk_rules = request.form.get('risk_rules', '')
        notes = request.form.get('notes', '')

        execute_db('''
            INSERT INTO strategies (user_id, name, market_type, timeframe, entry_rules, exit_rules, risk_rules, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [user_id, name, market_type, timeframe, entry_rules, exit_rules, risk_rules, notes])

        flash('Strategy saved to vault!', 'success')
        return redirect(url_for('strategies'))

    return render_template('strategy_form.html', strategy=None)

@app.route('/strategies/edit/<int:strategy_id>', methods=['GET', 'POST'])
@login_required
def edit_strategy(strategy_id):
    """Edit an existing strategy."""
    user_id = current_user.id

    strategy = query_db('SELECT * FROM strategies WHERE id = ? AND user_id = ?',
                       [strategy_id, user_id], one=True)
    if not strategy:
        flash('Strategy not found.', 'danger')
        return redirect(url_for('strategies'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        market_type = request.form.get('market_type')
        timeframe = request.form.get('timeframe', '').upper()
        entry_rules = request.form.get('entry_rules', '')
        exit_rules = request.form.get('exit_rules', '')
        risk_rules = request.form.get('risk_rules', '')
        notes = request.form.get('notes', '')

        execute_db('''
            UPDATE strategies SET
                name = ?, market_type = ?, timeframe = ?, entry_rules = ?, exit_rules = ?,
                risk_rules = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', [name, market_type, timeframe, entry_rules, exit_rules, risk_rules, notes,
              strategy_id, user_id])

        flash('Strategy updated!', 'success')
        return redirect(url_for('strategies'))

    return render_template('strategy_form.html', strategy=strategy)

@app.route('/strategies/archive/<int:strategy_id>', methods=['POST'])
@login_required
def archive_strategy(strategy_id):
    """Toggle archive status of a strategy (soft delete)."""
    user_id = current_user.id
    strategy = query_db('SELECT is_archived FROM strategies WHERE id = ? AND user_id = ?',
                       [strategy_id, user_id], one=True)
    if strategy:
        new_status = 0 if strategy['is_archived'] else 1
        execute_db('UPDATE strategies SET is_archived = ? WHERE id = ?',
                  [new_status, strategy_id])
        action = 'restored' if new_status == 0 else 'archived'
        flash(f'Strategy {action}.', 'success')
    return redirect(url_for('strategies'))

# =============================================================================
# BACKTESTING BUDDY ROUTES
# =============================================================================
@app.route('/backtest')
@login_required
def backtest():
    """Backtesting hub - list all backtest records."""
    user_id = current_user.id
    backtests = query_db(
        'SELECT * FROM backtests WHERE user_id = ? ORDER BY created_at DESC',
        [user_id]
    )
    return render_template('backtest.html', backtests=backtests)

@app.route('/backtest/new', methods=['GET', 'POST'])
@login_required
def new_backtest():
    """Create a new backtest record with performance metrics."""
    user_id = current_user.id

    # Get user's strategies for dropdown
    user_strategies = query_db(
        'SELECT id, name FROM strategies WHERE user_id = ? AND is_archived = 0 ORDER BY name',
        [user_id]
    )

    if request.method == 'POST':
        strategy_id = request.form.get('strategy_id')
        strategy_name = request.form.get('strategy_name', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        pair = request.form.get('pair', '').upper()
        trade_count = int(request.form.get('trade_count', 0))
        initial_balance = float(request.form.get('initial_balance', 0))
        final_balance = request.form.get('final_balance')
        total_return = request.form.get('total_return')
        win_rate = request.form.get('win_rate')
        profit_factor = request.form.get('profit_factor')
        max_drawdown = request.form.get('max_drawdown')
        notes = request.form.get('notes', '')

        # If strategy selected from dropdown, use its name
        if strategy_id:
            strat = query_db('SELECT name FROM strategies WHERE id = ?', [strategy_id], one=True)
            if strat:
                strategy_name = strat['name']

        execute_db('''
            INSERT INTO backtests (user_id, strategy_id, strategy_name, start_date, end_date,
                                 pair, trade_count, initial_balance, final_balance, total_return,
                                 win_rate, profit_factor, max_drawdown, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [user_id, strategy_id if strategy_id else None, strategy_name, start_date, end_date,
              pair, trade_count, initial_balance,
              float(final_balance) if final_balance else None,
              float(total_return) if total_return else None,
              float(win_rate) if win_rate else None,
              float(profit_factor) if profit_factor else None,
              float(max_drawdown) if max_drawdown else None,
              notes])

        flash('Backtest saved successfully!', 'success')
        return redirect(url_for('backtest'))

    return render_template('backtest_form.html', strategies=user_strategies, backtest=None)

@app.route('/backtest/delete/<int:backtest_id>', methods=['POST'])
@login_required
def delete_backtest(backtest_id):
    """Delete a backtest record."""
    user_id = current_user.id
    execute_db('DELETE FROM backtests WHERE id = ? AND user_id = ?', [backtest_id, user_id])
    flash('Backtest deleted.', 'info')
    return redirect(url_for('backtest'))

# =============================================================================
# LEARNING HUB ROUTES
# =============================================================================
@app.route('/learn')
@login_required
def learn():
    """Learning hub - display all modules with progress tracking."""
    user_id = current_user.id

    # Get all modules with lesson counts
    modules = query_db('''
        SELECT m.*, 
               COUNT(DISTINCT l.id) as total_lessons,
               COUNT(DISTINCT CASE WHEN up.completed = 1 THEN up.lesson_id END) as completed_lessons
        FROM learning_modules m
        LEFT JOIN learning_lessons l ON m.id = l.module_id
        LEFT JOIN user_progress up ON l.id = up.lesson_id AND up.user_id = ?
        GROUP BY m.id
        ORDER BY m.module_order
    ''', [user_id])

    # Pre-fetch all lessons and completion status for each module
    module_lessons = {}
    for module in modules:
        lessons = query_db('''
            SELECT l.*,
                   CASE WHEN up.completed = 1 THEN 1 ELSE 0 END as is_completed
            FROM learning_lessons l
            LEFT JOIN user_progress up ON l.id = up.lesson_id AND up.user_id = ?
            WHERE l.module_id = ?
            ORDER BY l.lesson_order
        ''', [user_id, module['id']])
        module_lessons[module['id']] = [dict(lesson) for lesson in lessons]

    return render_template('learning.html', modules=modules, module_lessons=module_lessons)

@app.route('/learn/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    """Display a single lesson with completion tracking."""
    user_id = current_user.id

    lesson = query_db('''
        SELECT l.*, m.title as module_title, m.module_order
        FROM learning_lessons l
        JOIN learning_modules m ON l.module_id = m.id
        WHERE l.id = ?
    ''', [lesson_id], one=True)

    if not lesson:
        flash('Lesson not found.', 'danger')
        return redirect(url_for('learn'))

    # Check completion status
    progress = query_db(
        'SELECT * FROM user_progress WHERE user_id = ? AND lesson_id = ?',
        [user_id, lesson_id], one=True
    )
    is_completed = progress['completed'] if progress else False

    # Get next and previous lessons
    prev_lesson = query_db('''
        SELECT id FROM learning_lessons 
        WHERE module_id = ? AND lesson_order < ? 
        ORDER BY lesson_order DESC LIMIT 1
    ''', [lesson['module_id'], lesson['lesson_order']], one=True)

    next_lesson = query_db('''
        SELECT id FROM learning_lessons 
        WHERE module_id = ? AND lesson_order > ? 
        ORDER BY lesson_order ASC LIMIT 1
    ''', [lesson['module_id'], lesson['lesson_order']], one=True)

    return render_template('lesson.html', lesson=lesson, is_completed=is_completed,
                         prev_lesson=prev_lesson, next_lesson=next_lesson)

@app.route('/learn/complete/<int:lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    """Mark a lesson as completed and update progress."""
    user_id = current_user.id

    # Upsert progress
    existing = query_db('SELECT id FROM user_progress WHERE user_id = ? AND lesson_id = ?',
                       [user_id, lesson_id], one=True)

    if existing:
        execute_db('''
            UPDATE user_progress SET completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND lesson_id = ?
        ''', [user_id, lesson_id])
    else:
        execute_db('''
            INSERT INTO user_progress (user_id, lesson_id, completed, completed_at)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
        ''', [user_id, lesson_id])

    flash('Lesson completed! Great work.', 'success')

    # Redirect to next lesson if exists, else back to learn page
    next_lesson = query_db('''
        SELECT l.id FROM learning_lessons l
        JOIN learning_lessons current ON current.id = ?
        WHERE l.module_id = current.module_id AND l.lesson_order > current.lesson_order
        ORDER BY l.lesson_order LIMIT 1
    ''', [lesson_id], one=True)

    if next_lesson:
        return redirect(url_for('lesson', lesson_id=next_lesson['id']))
    return redirect(url_for('learn'))

# =============================================================================
# GOALS & PROFILE ROUTES
# =============================================================================
@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    """Weekly goals management."""
    user_id = current_user.id
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start_str = week_start.strftime('%Y-%m-%d')

    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        target = int(request.form.get('target', 0))

        execute_db('''
            INSERT INTO weekly_goals (user_id, week_start_date, description, target)
            VALUES (?, ?, ?, ?)
        ''', [user_id, week_start_str, description, target])

        flash('Goal created!', 'success')
        return redirect(url_for('goals'))

    weekly_goals = query_db('''
        SELECT * FROM weekly_goals 
        WHERE user_id = ? AND week_start_date = ?
        ORDER BY created_at DESC
    ''', [user_id, week_start_str])

    return render_template('goals.html', goals=weekly_goals)

@app.route('/goals/update/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    """Update goal progress."""
    user_id = current_user.id
    current_val = int(request.form.get('current', 0))

    goal = query_db('SELECT target FROM weekly_goals WHERE id = ? AND user_id = ?',
                   [goal_id, user_id], one=True)

    if goal:
        completed = 1 if current_val >= goal['target'] else 0
        execute_db('''
            UPDATE weekly_goals SET current = ?, completed = ?
            WHERE id = ? AND user_id = ?
        ''', [current_val, completed, goal_id, user_id])

    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    """User profile page."""
    user_id = current_user.id

    # User stats
    trade_stats = query_db('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
            SUM(pnl) as net_pnl,
            AVG(pnl) as avg_pnl,
            MAX(pnl) as best_trade,
            MIN(pnl) as worst_trade
        FROM trades WHERE user_id = ?
    ''', [user_id], one=True)

    return render_template('profile.html', stats=trade_stats)

# =============================================================================
# API ENDPOINTS (JSON)
# =============================================================================
@app.route('/api/stats')
@login_required
def api_stats():
    """Return dashboard statistics as JSON for AJAX updates."""
    user_id = current_user.id

    total = query_db('SELECT COUNT(*) as c FROM trades WHERE user_id = ?', [user_id], one=True)['c']
    wins = query_db('SELECT COUNT(*) as c FROM trades WHERE user_id = ? AND pnl > 0', [user_id], one=True)['c']
    pnl = query_db('SELECT COALESCE(SUM(pnl), 0) as total FROM trades WHERE user_id = ?', [user_id], one=True)['total']

    return jsonify({
        'total_trades': total,
        'win_rate': round(wins / total * 100, 1) if total else 0,
        'net_pnl': round(pnl, 2)
    })

@app.route('/api/trades/recent')
@login_required
def api_recent_trades():
    """Return recent trades as JSON."""
    user_id = current_user.id
    trades = query_db(
        'SELECT * FROM trades WHERE user_id = ? ORDER BY trade_date DESC LIMIT 10',
        [user_id]
    )
    return jsonify([dict(row) for row in trades])

# =============================================================================
# ERROR HANDLERS
# =============================================================================
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors gracefully."""
    return render_template('base.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors gracefully."""
    return render_template('base.html', error='Something went wrong. Please try again.'), 500

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
if __name__ == '__main__':
    # Ensure database exists
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        print("⚠️  Database not found. Run: python database/init_db.py")

    print("=" * 60)
    print("  TRADEVAULT AI - Starting Development Server")
    print("=" * 60)
    print(f"  Local URL: http://127.0.0.1:5000")
    print(f"  Database:  {db_path}")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
