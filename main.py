"""
🤖 Discord Bot Avançado - Sistema de Agendamento de Mensagens
Autor: Bot Avançado
Versão: 2.1.2 (Guild + Global Sync)
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

# ID do servidor para sync instantâneo dos slash commands
GUILD_ID = 1508876618196713532

# Criar pasta data se não existir (ESSENCIAL para Railway!)
Path("data").mkdir(parents=True, exist_ok=True)

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
        Path("data").mkdir(parents=True, exist_ok=True)

        # Carregar cogs
        cogs = [
            'cogs.scheduled_messages',
            'cogs.announcements', 
            'cogs.management',
            'cogs.utilities',
            'cogs.events',
            'cogs.slash_commands'
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Cog carregado: {cog}")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {cog}: {e}")

        # ═══════════════════════════════════════════════════════════
        # SYNC INSTANTÂNEO NA GUILD (aparece na hora)
        # ═══════════════════════════════════════════════════════════
        try:
            guild = discord.Object(id=GUILD_ID)
            synced_guild = await self.tree.sync(guild=guild)
            logger.info(f"⚡ Guild sync ({GUILD_ID}): {len(synced_guild)} comandos instantâneos")
        except Exception as e:
            logger.error(f"❌ Erro no guild sync: {e}")

        # ═══════════════════════════════════════════════════════════
        # SYNC GLOBAL (aparece em todos os servidores, mas demora ~1h)
        # ═══════════════════════════════════════════════════════════
        try:
            synced_global = await self.tree.sync()
            logger.info(f"🌍 Global sync: {len(synced_global)} comandos (pode demorar até 1h para aparecer)")
        except Exception as e:
            logger.error(f"❌ Erro no global sync: {e}")

        # Iniciar scheduler
        self.scheduler.start()
        logger.info("⏰ Scheduler iniciado")

    async def on_ready(self):
        """Evento quando o bot está pronto"""
        logger.info(f"🚀 Bot conectado como {self.user} (ID: {self.user.id})")
        logger.info(f"📊 Servidores: {len(self.guilds)}")
        logger.info(f"👥 Usuários: {sum(g.member_count for g in self.guilds)}")

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="/ajuda | Agendador de Mensagens"
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        """Tratamento global de erros (prefix commands)"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ Você não tem permissão para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Argumento faltando. Use: `{Config.PREFIX}ajuda {ctx.command.name}`")
        else:
            logger.error(f"Erro no comando {ctx.command}: {error}")
            await ctx.send("❌ Ocorreu um erro inesperado.")

# Inicialização
if __name__ == "__main__":
    bot = AdvancedBot()

    try:
        bot.run(Config.TOKEN)
    except discord.LoginFailure:
        logger.critical("❌ TOKEN inválido! Verifique sua variável DISCORD_TOKEN no Railway")
    except Exception as e:
        logger.critical(f"❌ Erro fatal: {e}")
