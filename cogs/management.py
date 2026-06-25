"""
⚙️ Cog: Gerenciamento do Servidor
Configurações, logs e estatísticas
"""

import discord
from discord.ext import commands
from datetime import datetime

from utils.config import Config
from utils.helpers import create_progress_bar

class Management(commands.Cog):
    """Gerenciamento do servidor e configurações do bot"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.group(name="config", aliases=["cfg", "configurar"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def config_group(self, ctx):
        """⚙️ Configurações do bot no servidor"""
        settings = self.db.get_guild_settings(ctx.guild.id)

        embed = discord.Embed(
            title=f"⚙️ Configurações - {ctx.guild.name}",
            color=Config.COLOR_PRIMARY
        )

        log_channel = self.bot.get_channel(settings['log_channel_id']) if settings['log_channel_id'] else None

        embed.add_field(name="🌍 Fuso horário", value=f"`{settings['timezone']}`", inline=True)
        embed.add_field(name="📊 Limite mensagens", value=f"`{settings['max_messages']}`", inline=True)
        embed.add_field(name="📢 Allow @everyone", value="✅ Sim" if settings['allow_everyone'] else "❌ Não", inline=True)
        embed.add_field(name="📝 Canal de logs", value=log_channel.mention if log_channel else "Não configurado", inline=True)

        embed.add_field(
            name="Comandos:",
            value=(
                "`!config log #canal` - Definir canal de logs\n"
                "`!config limite <número>` - Limite de mensagens\n"
                "`!config everyone <on/off>` - Permitir @everyone"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

    @config_group.command(name="log")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """
        📝 Define o canal de logs
        Uso: !config log #canal
        """
        self.db.set_guild_settings(ctx.guild.id, log_channel_id=channel.id)
        await ctx.send(f"✅ Canal de logs definido para {channel.mention}!")

    @config_group.command(name="limite")
    @commands.has_permissions(administrator=True)
    async def set_limit(self, ctx, limit: int):
        """
        📊 Define o limite de mensagens agendadas
        Uso: !config limite 50
        """
        if limit < 1 or limit > 500:
            return await ctx.send("❌ Limite deve ser entre 1 e 500!")

        self.db.set_guild_settings(ctx.guild.id, max_messages=limit)
        await ctx.send(f"✅ Limite de mensagens definido para `{limit}`!")

    @config_group.command(name="everyone")
    @commands.has_permissions(administrator=True)
    async def set_everyone(self, ctx, status: str):
        """
        📢 Ativa/desativa permissão de @everyone
        Uso: !config everyone on
        """
        allow = 1 if status.lower() in ['on', 'sim', 'yes', 'true'] else 0
        self.db.set_guild_settings(ctx.guild.id, allow_everyone=allow)
        await ctx.send(f"✅ Allow @everyone: {'✅ Ativado' if allow else '❌ Desativado'}")

    @commands.command(name="stats", aliases=["estatisticas", "estatisticas"])
    @commands.has_permissions(manage_messages=True)
    async def stats(self, ctx):
        """
        📊 Estatísticas do bot no servidor
        """
        messages = self.db.get_scheduled_messages(guild_id=ctx.guild.id, active_only=False)
        active = len([m for m in messages if m['is_active']])
        inactive = len([m for m in messages if not m['is_active']])
        total_sent = sum(m['send_count'] or 0 for m in messages)

        embed = discord.Embed(
            title=f"📊 Estatísticas - {ctx.guild.name}",
            color=Config.COLOR_INFO,
            timestamp=datetime.now()
        )

        embed.add_field(name="🟢 Ativas", value=f"`{active}`", inline=True)
        embed.add_field(name="⚫ Inativas", value=f"`{inactive}`", inline=True)
        embed.add_field(name="📤 Total envios", value=f"`{total_sent}`", inline=True)
        embed.add_field(name="📊 Total agendadas", value=f"`{len(messages)}`", inline=True)

        if messages:
            channels = {}
            for m in messages:
                ch = m['channel_id']
                channels[ch] = channels.get(ch, 0) + 1
            top_channel = max(channels, key=channels.get)
            ch_obj = self.bot.get_channel(top_channel)
            embed.add_field(name="📺 Canal mais usado", value=ch_obj.mention if ch_obj else f"`{top_channel}`", inline=True)

        embed.set_footer(text=f"Servidor: {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        await ctx.send(embed=embed)

    @commands.command(name="limpar", aliases=["clean", "purge"])
    @commands.has_permissions(administrator=True)
    async def clean_old(self, ctx, days: int = 30):
        """
        🧹 Remove mensagens antigas inativas
        Uso: !limpar 30
        """
        if days < 1:
            return await ctx.send("❌ Dias deve ser maior que 0!")

        cutoff = datetime.now() - timedelta(days=days)
        messages = self.db.get_scheduled_messages(guild_id=ctx.guild.id, active_only=False)
        removed = 0

        for msg in messages:
            if not msg['is_active']:
                created = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00').replace('+00:00', ''))
                if created < cutoff:
                    self.db.delete_message(msg['id'])
                    removed += 1

        await ctx.send(f"🧹 `{removed}` mensagens antigas removidas (mais de {days} dias)!")

async def setup(bot):
    await bot.add_cog(Management(bot))
