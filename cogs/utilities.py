"""
🛠️ Cog: Utilitários (Prefix Commands)
"""

import discord
from discord.ext import commands
from datetime import datetime

from utils.config import Config
from utils.helpers import parse_datetime, format_datetime

class Utilities(commands.Cog):
    """Comandos utilitários via prefix"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """🏓 Verifica a latência do bot"""
        latency = round(self.bot.latency * 1000)
        color = Config.COLOR_SUCCESS if latency < 100 else Config.COLOR_WARNING if latency < 300 else Config.COLOR_ERROR

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: `{latency}ms`",
            color=color
        )
        embed.add_field(name="📊 Status", value="🟢 Excelente" if latency < 100 else "🟡 Bom" if latency < 300 else "🔴 Alto", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="ajuda")
    async def help_command(self, ctx, command_name: str = None):
        """❓ Mostra a ajuda do bot"""
        if command_name:
            command = self.bot.get_command(command_name)
            if not command:
                return await ctx.send(f"❌ Comando `{command_name}` não encontrado!")

            embed = discord.Embed(
                title=f"❓ Ajuda: `{command.name}`",
                description=command.help or "Sem descrição disponível.",
                color=Config.COLOR_INFO
            )
            embed.add_field(name="Aliases", value="Nenhum", inline=False)

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🤖 Bot de Agendamento - Ajuda",
                description="Bot avançado para agendamento de mensagens automáticas!",
                color=Config.COLOR_PRIMARY
            )

            embed.add_field(
                name="📅 Agendamento (Prefix)",
                value=(
                    "`!agendar` - Menu principal\n"
                    "`!agendar texto #canal data mensagem` - Texto\n"
                    "`!agendar embed #canal data` - Wizard embed\n"
                    "`!agendar anuncio #canal data mensagem` - Anúncio\n"
                    "`!agendar lista` - Listar\n"
                    "`!agendar info <id>` - Detalhes\n"
                    "`!agendar editar <id>` - Editar\n"
                    "`!agendar remover <id>` - Remover"
                ),
                inline=False
            )

            embed.add_field(
                name="⚡ Slash Commands (/)",
                value=(
                    "`/agendar-texto` - Texto rápido\n"
                    "`/agendar-embed` - Embed\n"
                    "`/agendar-anuncio` - Anúncio\n"
                    "`/lista` - Listar\n"
                    "`/info` - Detalhes\n"
                    "`/remover` - Remover\n"
                    "`/anuncio-rapido` - Anúncio instantâneo"
                ),
                inline=False
            )

            embed.add_field(
                name="📢 Anúncios",
                value=(
                    "`!anunciar rapido #canal mensagem` - Rápido\n"
                    "`!anunciar embed #canal` - Embed\n"
                    "`!anunciar template #canal nome vars` - Template"
                ),
                inline=False
            )

            embed.add_field(
                name="⚙️ Gerenciamento",
                value=(
                    "`!cfg` - Configurações\n"
                    "`!estatisticas` - Estatísticas\n"
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

            embed.set_footer(text="Prefixo: ! | v2.1.2")
            await ctx.send(embed=embed)

    @commands.command(name="horario")
    async def current_time(self, ctx):
        """🕐 Mostra a hora atual do bot"""
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
