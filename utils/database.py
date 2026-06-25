"""
🗄️ Sistema de Banco de Dados SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger('DiscordBot')

class Database:
    """Gerenciamento do banco de dados SQLite"""

    def __init__(self, db_path: str = "data/scheduled_messages.db"):
        self.db_path = db_path
        Path("data").mkdir(exist_ok=True)
        self._init_db()

    def _get_connection(self):
        """Retorna uma conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Inicializa as tabelas do banco"""
        with self._get_connection() as conn:
            # Tabela de mensagens agendadas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    author_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embed_data TEXT,
                    scheduled_time TEXT NOT NULL,
                    recurrence TEXT DEFAULT 'once',
                    recurrence_data TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_sent TEXT,
                    send_count INTEGER DEFAULT 0
                )
            """)

            # Tabela de logs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS message_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    status TEXT,
                    error_message TEXT,
                    sent_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de configurações do servidor
            conn.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    timezone TEXT DEFAULT 'America/Sao_Paulo',
                    max_messages INTEGER DEFAULT 50,
                    allow_everyone INTEGER DEFAULT 0,
                    log_channel_id INTEGER,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("🗄️ Banco de dados inicializado")

    def add_scheduled_message(self, guild_id: int, channel_id: int, author_id: int,
                              content: str, scheduled_time: str, embed_data: str = None,
                              recurrence: str = 'once', recurrence_data: str = None) -> int:
        """Adiciona uma mensagem agendada"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO scheduled_messages 
                (guild_id, channel_id, author_id, content, embed_data, 
                 scheduled_time, recurrence, recurrence_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (guild_id, channel_id, author_id, content, embed_data,
                  scheduled_time, recurrence, recurrence_data))
            conn.commit()
            return cursor.lastrowid

    def get_scheduled_messages(self, guild_id: int = None, active_only: bool = True) -> List[Dict]:
        """Retorna mensagens agendadas"""
        query = "SELECT * FROM scheduled_messages WHERE 1=1"
        params = []

        if guild_id:
            query += " AND guild_id = ?"
            params.append(guild_id)
        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY scheduled_time ASC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_message_by_id(self, message_id: int) -> Optional[Dict]:
        """Retorna uma mensagem específica pelo ID"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM scheduled_messages WHERE id = ?", 
                (message_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_message(self, message_id: int, **kwargs):
        """Atualiza campos de uma mensagem"""
        allowed_fields = ['content', 'embed_data', 'scheduled_time', 
                         'recurrence', 'recurrence_data', 'is_active', 
                         'last_sent', 'send_count']

        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [message_id]

        with self._get_connection() as conn:
            conn.execute(
                f"UPDATE scheduled_messages SET {set_clause} WHERE id = ?",
                values
            )
            conn.commit()

    def delete_message(self, message_id: int):
        """Remove uma mensagem agendada"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM scheduled_messages WHERE id = ?", (message_id,))
            conn.commit()

    def log_message(self, message_id: int, guild_id: int, channel_id: int, 
                    status: str, error_message: str = None):
        """Registra log de envio"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO message_logs (message_id, guild_id, channel_id, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, guild_id, channel_id, status, error_message))
            conn.commit()

    def get_guild_settings(self, guild_id: int) -> Dict:
        """Retorna configurações do servidor"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM guild_settings WHERE guild_id = ?", 
                (guild_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            # Retorna padrões
            return {
                'guild_id': guild_id,
                'timezone': 'America/Sao_Paulo',
                'max_messages': 50,
                'allow_everyone': 0,
                'log_channel_id': None
            }

    def set_guild_settings(self, guild_id: int, **kwargs):
        """Atualiza configurações do servidor"""
        allowed = ['timezone', 'max_messages', 'allow_everyone', 'log_channel_id']
        updates = {k: v for k, v in kwargs.items() if k in allowed}

        with self._get_connection() as conn:
            # Verifica se existe
            exists = conn.execute(
                "SELECT 1 FROM guild_settings WHERE guild_id = ?", 
                (guild_id,)
            ).fetchone()

            if exists:
                set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
                values = list(updates.values()) + [guild_id]
                conn.execute(
                    f"UPDATE guild_settings SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE guild_id = ?",
                    values
                )
            else:
                fields = ['guild_id'] + list(updates.keys())
                placeholders = ', '.join(['?'] * len(fields))
                values = [guild_id] + list(updates.values())
                conn.execute(
                    f"INSERT INTO guild_settings ({', '.join(fields)}) VALUES ({placeholders})",
                    values
                )
            conn.commit()
