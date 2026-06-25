"""
⚙️ Configurações do Bot
Suporte a Railway (variáveis de ambiente) e .env local
"""

import os

# Tenta carregar .env apenas se existir (desenvolvimento local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """Configurações centralizadas do bot - compatível com Railway e local"""

    # 🔑 Token do Bot (Railway: DISCORD_TOKEN | Local: .env)
    TOKEN = os.getenv("DISCORD_TOKEN", "")

    # 📝 Prefixo dos comandos (Railway: BOT_PREFIX | Local: .env)
    PREFIX = os.getenv("BOT_PREFIX", "!")

    # 👑 IDs dos donos do bot (Railway: OWNER_IDS | Local: .env)
    OWNER_IDS = []
    _owner_ids_str = os.getenv("OWNER_IDS", "")
    if _owner_ids_str:
        try:
            OWNER_IDS = [int(x.strip()) for x in _owner_ids_str.split(",") if x.strip()]
        except ValueError:
            OWNER_IDS = []

    # 🎨 Cores embed
    COLOR_PRIMARY = 0x5865F2      # Roxo Discord
    COLOR_SUCCESS = 0x57F287      # Verde
    COLOR_WARNING = 0xFEE75C      # Amarelo
    COLOR_ERROR = 0xED4245        # Vermelho
    COLOR_INFO = 0xEB459E         # Rosa

    # ⏰ Configurações de agendamento
    MAX_SCHEDULED_MESSAGES = 100  # Máximo de mensagens agendadas por servidor
    DEFAULT_TIMEZONE = "America/Sao_Paulo"

    # 📊 Banco de dados
    DB_PATH = "data/scheduled_messages.db"

    # 🌐 Links úteis (opcional)
    SUPPORT_SERVER = os.getenv("SUPPORT_SERVER", "")
    BOT_INVITE = os.getenv("BOT_INVITE", "")
