"""
🎉 Cog: Eventos
Handlers de eventos do bot
"""

import discord
from discord.ext import commands
from datetime import datetime

from utils.config import Config

class Events(commands.Cog):
    """Eventos do bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Quando um membro entra no servidor"""
        pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Quando o bot entra em um novo servidor"""
        self.bot.db.set_guild_settings(guild.id)

        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🤖 Bot de Agendamento",
                    description="Obrigado por me adicionar!\n\nUse `!ajuda` para ver os comandos disponíveis.",
                    color=Config.COLOR_PRIMARY
                )
                embed.add_field(
                    name="🚀 Primeiros passos:",
                    value=(
                        "1. Use `!config log #canal` para definir logs\n"
                        "2. Use `!agendar` para começar a agendar mensagens"
                    ),
                    inline=False
                )
                await channel.send(embed=embed)
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Quando o bot é removido de um servidor"""
        pass

async def setup(bot):
    await bot.add_cog(Events(bot))
