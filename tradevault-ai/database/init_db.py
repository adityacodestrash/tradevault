#!/usr/bin/env python3
"""
TRADEVAULT AI - Database Initialization Script
Run this once to create the database and seed learning content.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'tradevault.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def init_db():
    """Initialize database with schema and seed data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Execute schema
    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())

    # Seed learning modules
    modules = [
        (1, 'Trading Basics', 'Foundation concepts every trader must master', 1, 8, 0, None),
        (2, 'Risk Management', 'Protect your capital with proper risk rules', 2, 6, 0, 1),
        (3, 'Trading Psychology', 'Master your emotions and trading mindset', 3, 6, 0, 2),
        (4, 'Technical Analysis', 'Read charts, patterns, and indicators', 4, 8, 0, 3),
        (5, 'Strategy Building', 'Create and refine your edge', 5, 6, 0, 4),
        (6, 'Backtesting', 'Validate your strategy with historical data', 6, 6, 0, 5),
        (7, 'Advanced Concepts', 'Professional techniques and market nuances', 7, 8, 0, 6),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO learning_modules (id, title, description, module_order, lesson_count, is_locked, prerequisite_module_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', modules)

    # Seed lessons for Trading Basics (module 1)
    lessons_module1 = [
        (1, 1, 'What is Trading?', 'Trading is the act of buying and selling financial instruments to profit from price movements. Unlike investing which focuses on long-term growth, trading seeks to capitalize on short-term market fluctuations.', 10, 1),
        (2, 1, 'Markets Overview', 'Explore Forex, Crypto, Stocks, Futures, and Indices. Each market has unique characteristics, volatility patterns, and trading hours that affect strategy selection.', 12, 2),
        (3, 1, 'Order Types', 'Learn Market Orders, Limit Orders, Stop Orders, and Stop-Limit Orders. Understanding order types is crucial for precise trade execution and risk control.', 8, 3),
        (4, 1, 'Reading Price Charts', 'Master candlestick charts, bar charts, and line charts. Learn to identify bullish and bearish candles and what they reveal about market sentiment.', 15, 4),
        (5, 1, 'Support & Resistance', 'Discover the most fundamental concept in technical analysis. Learn how to draw levels and why they act as barriers for price movement.', 14, 5),
        (6, 1, 'Trends & Trendlines', 'Identify uptrends, downtrends, and sideways markets. Learn to draw trendlines correctly and trade in the direction of the dominant trend.', 12, 6),
        (7, 1, 'Volume & Liquidity', 'Understand how volume confirms price movements. Learn why liquidity matters and how it affects your trade execution and slippage.', 10, 7),
        (8, 1, 'Trading Sessions', 'Know when to trade. Understand the overlap between London, New York, and Tokyo sessions and how volatility changes throughout the day.', 9, 8),
    ]

    # Seed lessons for Risk Management (module 2)
    lessons_module2 = [
        (9, 2, 'The 1% Rule', 'Never risk more than 1-2% of your account on a single trade. This rule ensures you survive losing streaks and stay in the game long-term.', 10, 1),
        (10, 2, 'Position Sizing', 'Calculate exact lot sizes based on your stop loss and account balance. Learn the formula: Risk Amount / (Entry - Stop Loss) = Position Size.', 12, 2),
        (11, 2, 'Stop Loss Placement', 'Place stops at logical technical levels, not arbitrary distances. Learn to use ATR, swing highs/lows, and structure for optimal stop placement.', 14, 3),
        (12, 2, 'Risk-Reward Ratio', 'Aim for minimum 1:2 risk-reward. This means risking $1 to make $2. With a 40% win rate and 1:2 R:R, you are profitable over time.', 10, 4),
        (13, 2, 'Drawdown Recovery', 'Understand the math: a 50% drawdown requires a 100% gain to recover. Learn why preserving capital is more important than chasing returns.', 11, 5),
        (14, 2, 'Portfolio Heat', 'Monitor total open risk across all positions. Never expose more than 5-6% of your account to risk at any given time.', 9, 6),
    ]

    # Seed lessons for Trading Psychology (module 3)
    lessons_module3 = [
        (15, 3, 'Emotional Control', 'Fear and greed destroy accounts. Learn to recognize emotional trading and develop protocols to trade with logic instead of feelings.', 12, 1),
        (16, 3, 'Trading Plan', 'Every professional has a written trading plan. Create yours covering strategy rules, risk parameters, and daily routines.', 15, 2),
        (17, 3, 'Journaling Discipline', 'Your journal is your mirror. Review every trade to identify patterns in your behavior and eliminate costly mistakes.', 10, 3),
        (18, 3, 'FOMO & Revenge Trading', 'Fear of Missing Out and Revenge Trading are the two biggest account killers. Learn specific techniques to prevent both.', 11, 4),
        (19, 3, 'Confidence & Consistency', 'Build confidence through backtesting and small wins. Consistency comes from following your plan, not from random big wins.', 13, 5),
        (20, 3, 'Mental Preparation', 'Pre-market routines, meditation, and physical health directly impact trading performance. Treat trading like a professional sport.', 9, 6),
    ]

    # Seed lessons for Technical Analysis (module 4)
    lessons_module4 = [
        (21, 4, 'Moving Averages', 'SMA and EMA are foundational trend indicators. Learn how to use the 50, 100, and 200 period MAs for trend direction and dynamic support/resistance.', 12, 1),
        (22, 4, 'RSI Indicator', 'The Relative Strength Index measures momentum. Learn to identify overbought (>70) and oversold (<30) conditions and divergence signals.', 11, 2),
        (23, 4, 'MACD', 'Moving Average Convergence Divergence shows trend strength and momentum shifts. Learn to read the MACD line, signal line, and histogram.', 13, 3),
        (24, 4, 'Chart Patterns', 'Master Head & Shoulders, Double Tops/Bottoms, Triangles, and Flags. These patterns reveal market psychology and high-probability setups.', 16, 4),
        (25, 4, 'Fibonacci Retracement', 'Use the golden ratio (0.618, 0.382) to find potential reversal zones. Combine Fibs with support/resistance for confluence.', 14, 5),
        (26, 4, 'Candlestick Patterns', 'Learn Doji, Engulfing, Hammer, Shooting Star, and Morning Star. Single and multi-candle patterns reveal immediate sentiment shifts.', 15, 6),
        (27, 4, 'Bollinger Bands', 'Measure volatility with Bollinger Bands. Learn the squeeze (low volatility = big move coming) and band walking strategies.', 11, 7),
        (28, 4, 'Multi-Timeframe Analysis', 'Always check higher timeframes for context. The daily trend defines the direction; the 1H provides the entry timing.', 12, 8),
    ]

    # Seed lessons for Strategy Building (module 5)
    lessons_module5 = [
        (29, 5, 'Finding Your Edge', 'An edge is a repeatable advantage. It comes from combining confluence factors: trend + level + pattern + indicator alignment.', 12, 1),
        (30, 5, 'Entry Criteria', 'Define precise entry rules. Vague entries lead to inconsistent results. Write down exactly what must happen before you enter.', 14, 2),
        (31, 5, 'Exit Criteria', 'Plan your exit before you enter. Know your take profit targets and trailing stop rules before the trade is live.', 13, 3),
        (32, 5, 'Strategy Types', 'Explore trend following, mean reversion, breakout trading, and range trading. Match your personality to your strategy style.', 11, 4),
        (33, 5, 'Confluence Trading', 'The more factors align, the higher the probability. Stack trend direction, key level, pattern, and momentum for A+ setups.', 15, 5),
        (34, 5, 'Strategy Documentation', 'Document every rule, parameter, and condition. A strategy is only real when it is written down and repeatable.', 10, 6),
    ]

    # Seed lessons for Backtesting (module 6)
    lessons_module6 = [
        (35, 6, 'What is Backtesting?', 'Backtesting applies your strategy rules to historical data to see how it would have performed. It validates edge before risking real money.', 10, 1),
        (36, 6, 'Manual Backtesting', 'Scroll through charts trade by trade. Record every setup, entry, exit, and result. This builds deep strategy familiarity.', 14, 2),
        (37, 6, 'Key Metrics', 'Track Win Rate, Profit Factor, Average R-Multiple, Max Drawdown, and Expectancy. These numbers tell you if your strategy is viable.', 16, 3),
        (38, 6, 'Sample Size', 'You need minimum 100 trades for statistical relevance. 30 trades is not enough. More data = more confidence in your edge.', 11, 4),
        (39, 6, 'Curve Fitting Trap', 'Do not optimize your strategy to fit past data perfectly. A curve-fit strategy fails in live markets. Keep rules simple and robust.', 13, 5),
        (40, 6, 'Forward Testing', 'After backtesting, trade your strategy on a demo account for 2-3 months. Live execution reveals issues backtesting cannot.', 12, 6),
    ]

    # Seed lessons for Advanced Concepts (module 7)
    lessons_module7 = [
        (41, 7, 'Market Structure', 'Understand how markets create higher highs, higher lows, lower highs, and lower lows. Structure reveals trend health and potential reversals.', 14, 1),
        (42, 7, 'Liquidity Grabs', 'Institutions hunt stop losses. Learn to spot liquidity pools above swing highs and below swing lows where smart money operates.', 15, 2),
        (43, 7, 'Supply & Demand Zones', 'Advanced support/resistance based on institutional order flow. These zones offer high-probability entries with tight risk.', 16, 3),
        (44, 7, 'Correlation Analysis', 'Currency pairs move together. Trading EUR/USD and GBP/USD simultaneously doubles your risk. Learn to manage correlated positions.', 11, 4),
        (45, 7, 'Economic Calendar', 'Major news events create volatility spikes. Know when NFP, CPI, and FOMC releases occur. Decide whether to trade through news or sit out.', 12, 5),
        (46, 7, 'Trade Management', 'Advanced techniques: scaling in, scaling out, breakeven stops, and trailing stops. Learn when to hold and when to take partial profits.', 14, 6),
        (47, 7, 'Journal Analytics', 'Review monthly statistics. Identify your best performing pairs, times of day, and strategy variations. Double down on what works.', 13, 7),
        (48, 7, 'Continuous Improvement', 'Markets evolve. Your strategy must too. Schedule monthly reviews to adapt rules to changing market conditions.', 10, 8),
    ]

    all_lessons = (lessons_module1 + lessons_module2 + lessons_module3 + 
                   lessons_module4 + lessons_module5 + lessons_module6 + lessons_module7)

    cursor.executemany('''
        INSERT OR IGNORE INTO learning_lessons (id, module_id, title, content, duration, lesson_order)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', all_lessons)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")
    print("✅ 7 Learning Modules seeded")
    print("✅ 48 Lessons seeded")
    print("\nNext steps:")
    print("1. Install requirements: pip install -r requirements.txt")
    print("2. Run: python database/init_db.py")
    print("3. Start app: python app.py")

if __name__ == '__main__':
    init_db()
