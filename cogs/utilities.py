"""
🛠️ Cog: Utilitários
Comandos úteis e helpers
"""

import discord
from discord.ext import commands
import asyncio
from datetime import datetime

from utils.config import Config
from utils.helpers import parse_datetime, format_datetime

class Utilities(commands.Cog):
    """Comandos utilitários"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        🏓 Verifica a latência do bot
        """
        latency = round(self.bot.latency * 1000)

        color = Config.COLOR_SUCCESS if latency < 100 else Config.COLOR_WARNING if latency < 300 else Config.COLOR_ERROR

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: `{latency}ms`",
            color=color
        )
        embed.add_field(name="📊 Status", value="🟢 Excelente" if latency < 100 else "🟡 Bom" if latency < 300 else "🔴 Alto", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="ajuda", aliases=["help", "h"])
    async def help_command(self, ctx, command_name: str = None):
        """
        ❓ Mostra a ajuda do bot
        Uso: !ajuda [comando]
        """
        if command_name:
            command = self.bot.get_command(command_name)
            if not command:
                return await ctx.send(f"❌ Comando `{command_name}` não encontrado!")

            embed = discord.Embed(
                title=f"❓ Ajuda: `{command.name}`",
                description=command.help or "Sem descrição disponível.",
                color=Config.COLOR_INFO
            )
            embed.add_field(name="Aliases", value=", ".join(f"`{a}`" for a in command.aliases) if command.aliases else "Nenhum", inline=False)

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🤖 Bot de Agendamento - Ajuda",
                description="Bot avançado para agendamento de mensagens automáticas no Discord!",
                color=Config.COLOR_PRIMARY
            )

            embed.add_field(
                name="📅 Agendamento",
                value=(
                    "`!agendar` - Menu principal\n"
                    "`!agendar texto` - Mensagem de texto\n"
                    "`!agendar embed` - Mensagem com embed\n"
                    "`!agendar anuncio` - Anúncio com @everyone\n"
                    "`!agendar lista` - Listar agendadas\n"
                    "`!agendar info <id>` - Detalhes\n"
                    "`!agendar editar <id>` - Editar\n"
                    "`!agendar remover <id>` - Remover"
                ),
                inline=False
            )

            embed.add_field(
                name="📢 Anúncios",
                value=(
                    "`!anuncio rapido` - Anúncio rápido\n"
                    "`!anuncio embed` - Anúncio com embed\n"
                    "`!anuncio template` - Usar template"
                ),
                inline=False
            )

            embed.add_field(
                name="⚙️ Gerenciamento",
                value=(
                    "`!config` - Configurações\n"
                    "`!stats` - Estatísticas\n"
                    "`!limpar` - Limpar antigas"
                ),
                inline=False
            )

            embed.add_field(
                name="🛠️ Utilitários",
                value=(
                    "`!ping` - Latência\n"
                    "`!ajuda` - Esta mensagem"
                ),
                inline=False
            )

            embed.set_footer(text=f"Prefixo: {Config.PREFIX} | v2.0.0")
            await ctx.send(embed=embed)

    @commands.command(name="horario", aliases=["time", "hora"])
    async def current_time(self, ctx):
        """
        🕐 Mostra a hora atual do bot
        """
        now = datetime.now()
        embed = discord.Embed(
            title="🕐 Hora Atual",
            description=f"**{now.strftime('%d/%m/%Y %H:%M:%S')}**",
            color=Config.COLOR_INFO
        )
        embed.set_footer(text="Fuso horário do servidor do bot")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))
