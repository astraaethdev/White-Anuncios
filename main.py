"""
🤖 Discord Bot Avançado - Sistema de Agendamento de Mensagens
Autor: Bot Avançado
Versão: 2.0.0
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

from utils.config import Config
from utils.database import Database
from utils.scheduler import MessageScheduler

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('data/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DiscordBot')

class AdvancedBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=Config.PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )

        self.start_time = datetime.now()
        self.db = Database()
        self.scheduler = MessageScheduler(self)

    async def setup_hook(self):
        """Carrega extensões e inicializa sistemas"""
        # Criar pasta data se não existir
        Path("data").mkdir(exist_ok=True)

        # Carregar cogs
        cogs = [
            'cogs.scheduled_messages',
            'cogs.announcements', 
            'cogs.management',
            'cogs.utilities',
            'cogs.events'
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Cog carregado: {cog}")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {cog}: {e}")

        # Iniciar scheduler
        self.scheduler.start()
        logger.info("⏰ Scheduler iniciado")

    async def on_ready(self):
        """Evento quando o bot está pronto"""
        logger.info(f"🚀 Bot conectado como {self.user} (ID: {self.user.id})")
        logger.info(f"📊 Servidores: {len(self.guilds)}")
        logger.info(f"👥 Usuários: {sum(g.member_count for g in self.guilds)}")

        # Status personalizado
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{Config.PREFIX}ajuda | Agendador de Mensagens"
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        """Tratamento global de erros"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ Você não tem permissão para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Argumento faltando. Use: `{Config.PREFIX}ajuda {ctx.command.name}`")
        else:
            logger.error(f"Erro no comando {ctx.command}: {error}")
            await ctx.send("❌ Ocorreu um erro inesperado. Os desenvolvedores foram notificados.")

# Inicialização
if __name__ == "__main__":
    bot = AdvancedBot()

    try:
        bot.run(Config.TOKEN)
    except discord.LoginFailure:
        logger.critical("❌ TOKEN inválido! Verifique seu .env")
    except Exception as e:
        logger.critical(f"❌ Erro fatal: {e}")
