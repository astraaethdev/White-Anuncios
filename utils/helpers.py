"""
🛠️ Funções auxiliares
"""

import re
from datetime import datetime, timedelta
from typing import Optional

def parse_datetime(date_string: str) -> Optional[datetime]:
    """
    Parse de data/hora em vários formatos (fuso horário de Brasília)
    Formatos suportados:
    - DD/MM/YYYY HH:MM
    - DD-MM-YYYY HH:MM
    - YYYY-MM-DD HH:MM
    - HH:MM (data de hoje)
    """
    formats = [
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d/%m/%y %H:%M",
        "%H:%M"
    ]

    for fmt in formats:
        try:
            result = datetime.strptime(date_string, fmt)
            if fmt == "%H:%M":
                # Usa data de hoje (Brasília)
                now = datetime.now()
                result = result.replace(year=now.year, month=now.month, day=now.day)
            return result
        except ValueError:
            continue

    return None

def format_datetime(dt: datetime) -> str:
    """Formata datetime para exibição"""
    return dt.strftime("%d/%m/%Y às %H:%M")

def is_valid_url(url: str) -> bool:
    """Verifica se é uma URL válida"""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def truncate_text(text: str, max_length: int = 100) -> str:
    """Trunca texto se necessário"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Cria uma barra de progresso"""
    if total == 0:
        return "□" * length
    filled = int(length * current / total)
    return "■" * filled + "□" * (length - filled)
