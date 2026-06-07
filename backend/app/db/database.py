import sqlite3
import json
import os
from typing import Optional
from datetime import datetime
from app.config import settings


DB_PATH: str = settings.database_path


def _get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            agent_id TEXT UNIQUE NOT NULL,
            strategy TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            config TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            performance TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS trades (
            time TEXT NOT NULL,
            trade_id TEXT PRIMARY KEY,
            agent_id TEXT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            qty REAL NOT NULL,
            price REAL NOT NULL,
            order_type TEXT NOT NULL,
            fee REAL,
            pnl REAL,
            status TEXT DEFAULT 'pending',
            exchange TEXT NOT NULL,
            metadata TEXT
        );

        CREATE TABLE IF NOT EXISTS decision_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT DEFAULT (datetime('now')),
            agent_id TEXT,
            symbol TEXT,
            action TEXT,
            confidence REAL,
            reasoning TEXT,
            risk_check_passed INTEGER,
            executed INTEGER DEFAULT 0,
            execution_result TEXT
        );

        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            starting_balance REAL,
            ending_balance REAL,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            total_fees REAL DEFAULT 0,
            max_drawdown_pct REAL DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


def execute(query: str, params: tuple = ()) -> list:
    conn = _get_db()
    try:
        cur = conn.execute(query, params)
        conn.commit()
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute_many(query: str, params_list: list):
    conn = _get_db()
    try:
        conn.executemany(query, params_list)
        conn.commit()
    finally:
        conn.close()
