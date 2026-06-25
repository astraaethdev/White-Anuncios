"""
⚡ Cog: Slash Commands (Application Commands)
Comandos modernos com auto-complete e interface interativa
"""

import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime, timedelta

from utils.config import Config
from utils.helpers import parse_datetime, format_datetime, truncate_text

class SlashCommands(commands.Cog):
    """Slash commands modernos do Discord"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    # ═══════════════════════════════════════════════════════════
    # 📅 AGENDAMENTO
    # ═══════════════════════════════════════════════════════════

    @app_commands.command(name="agendar-texto", description="📅 Agenda uma mensagem de texto")
    @app_commands.describe(
        canal="Canal onde a mensagem será enviada",
        data="Data/hora (DD/MM/YYYY HH:MM ou HH:MM)",
        mensagem="Conteúdo da mensagem",
        recorrencia="Tipo de recorrência"
    )
    @app_commands.choices(recorrencia=[
        app_commands.Choice(name="Única", value="once"),
        app_commands.Choice(name="Diária", value="daily"),
        app_commands.Choice(name="Semanal", value="weekly")
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_agendar_texto(self, interaction: discord.Interaction, 
                                   canal: discord.TextChannel, 
                                   data: str, 
                                   mensagem: str,
                                   recorrencia: app_commands.Choice[str] = None):
        """Agenda uma mensagem de texto via slash command"""

        scheduled_time = parse_datetime(data)
        if not scheduled_time:
            return await interaction.response.send_message(
                "❌ Formato inválido! Use: `DD/MM/YYYY HH:MM` ou `HH:MM`", 
                ephemeral=True
            )

        if scheduled_time < datetime.now():
            return await interaction.response.send_message(
                "⏰ A data/hora precisa ser no futuro!", 
                ephemeral=True
            )

        guild_messages = self.db.get_scheduled_messages(guild_id=interaction.guild_id)
        settings = self.db.get_guild_settings(interaction.guild_id)
        if len(guild_messages) >= settings['max_messages']:
            return await interaction.response.send_message(
                f"⚠️ Limite de {settings['max_messages']} mensagens atingido!", 
                ephemeral=True
            )

        rec = recorrencia.value if recorrencia else 'once'

        message_id = self.db.add_scheduled_message(
            guild_id=interaction.guild_id,
            channel_id=canal.id,
            author_id=interaction.user.id,
            content=mensagem,
            scheduled_time=scheduled_time.isoformat(),
            recurrence=rec
        )

        embed = discord.Embed(
            title="✅ Mensagem Agendada",
            description=f"Sua mensagem foi agendada com sucesso!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="🆔 ID", value=f"`{message_id}`", inline=True)
        embed.add_field(name="📺 Canal", value=canal.mention, inline=True)
        embed.add_field(name="⏰ Data/Hora", value=format_datetime(scheduled_time), inline=True)
        embed.add_field(name="🔄 Recorrência", value=rec.replace('once', 'Única').replace('daily', 'Diária').replace('weekly', 'Semanal'), inline=True)
        embed.add_field(name="📝 Conteúdo", value=truncate_text(mensagem, 500), inline=False)
        embed.set_footer(text=f"Agendado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="agendar-embed", description="🎨 Agenda uma mensagem com embed")
    @app_commands.describe(
        canal="Canal onde o embed será enviado",
        data="Data/hora (DD/MM/YYYY HH:MM ou HH:MM)",
        titulo="Título do embed",
        descricao="Descrição do embed",
        cor="Cor em hex (ex: #FF5733)",
        imagem="URL da imagem (opcional)",
        recorrencia="Tipo de recorrência"
    )
    @app_commands.choices(recorrencia=[
        app_commands.Choice(name="Única", value="once"),
        app_commands.Choice(name="Diária", value="daily"),
        app_commands.Choice(name="Semanal", value="weekly")
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_agendar_embed(self, interaction: discord.Interaction,
                                   canal: discord.TextChannel,
                                   data: str,
                                   titulo: str,
                                   descricao: str,
                                   cor: str = None,
                                   imagem: str = None,
                                   recorrencia: app_commands.Choice[str] = None):
        """Agenda um embed via slash command"""

        scheduled_time = parse_datetime(data)
        if not scheduled_time:
            return await interaction.response.send_message(
                "❌ Formato de data inválido!", ephemeral=True
            )

        if scheduled_time < datetime.now():
            return await interaction.response.send_message(
                "⏰ A data precisa ser no futuro!", ephemeral=True
            )

        # Parse cor
        embed_color = Config.COLOR_PRIMARY
        if cor:
            try:
                embed_color = int(cor.replace('#', ''), 16)
            except:
                pass

        embed_data = {
            "title": titulo,
            "description": descricao,
            "color": embed_color
        }
        if imagem:
            embed_data["image"] = {"url": imagem}

        rec = recorrencia.value if recorrencia else 'once'

        message_id = self.db.add_scheduled_message(
            guild_id=interaction.guild_id,
            channel_id=canal.id,
            author_id=interaction.user.id,
            content="",
            scheduled_time=scheduled_time.isoformat(),
            embed_data=json.dumps(embed_data),
            recurrence=rec
        )

        preview = discord.Embed.from_dict(embed_data)
        preview.set_author(name="👁️ Preview")

        embed = discord.Embed(
            title="✅ Embed Agendado",
            description=f"Embed agendado com sucesso!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="🆔 ID", value=f"`{message_id}`", inline=True)
        embed.add_field(name="📺 Canal", value=canal.mention, inline=True)
        embed.add_field(name="⏰ Data/Hora", value=format_datetime(scheduled_time), inline=True)

        await interaction.response.send_message(embeds=[embed, preview])

    @app_commands.command(name="agendar-anuncio", description="📢 Agenda um anúncio com @everyone")
    @app_commands.describe(
        canal="Canal do anúncio",
        data="Data/hora (DD/MM/YYYY HH:MM)",
        mensagem="Conteúdo do anúncio"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_agendar_anuncio(self, interaction: discord.Interaction,
                                     canal: discord.TextChannel,
                                     data: str,
                                     mensagem: str):
        """Agenda um anúncio com @everyone"""

        scheduled_time = parse_datetime(data)
        if not scheduled_time:
            return await interaction.response.send_message(
                "❌ Formato de data inválido!", ephemeral=True
            )

        if scheduled_time < datetime.now():
            return await interaction.response.send_message(
                "⏰ A data precisa ser no futuro!", ephemeral=True
            )

        full_content = f"@everyone\n\n{mensagem}"

        message_id = self.db.add_scheduled_message(
            guild_id=interaction.guild_id,
            channel_id=canal.id,
            author_id=interaction.user.id,
            content=full_content,
            scheduled_time=scheduled_time.isoformat()
        )

        embed = discord.Embed(
            title="📢 Anúncio Agendado",
            description="Anúncio com @everyone agendado!",
            color=Config.COLOR_WARNING
        )
        embed.add_field(name="🆔 ID", value=f"`{message_id}`", inline=True)
        embed.add_field(name="📺 Canal", value=canal.mention, inline=True)
        embed.add_field(name="⏰ Data/Hora", value=format_datetime(scheduled_time), inline=True)
        embed.add_field(name="📝 Preview", value=truncate_text(mensagem, 300), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="lista", description="📋 Lista mensagens agendadas")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_lista(self, interaction: discord.Interaction):
        """Lista mensagens agendadas via slash command"""

        messages = self.db.get_scheduled_messages(guild_id=interaction.guild_id, active_only=False)

        if not messages:
            embed = discord.Embed(
                title="📭 Sem mensagens agendadas",
                color=Config.COLOR_INFO
            )
            return await interaction.response.send_message(embed=embed)

        active = [m for m in messages if m['is_active']]
        inactive = [m for m in messages if not m['is_active']]

        embed = discord.Embed(
            title=f"📋 Mensagens Agendadas ({len(messages)} total)",
            color=Config.COLOR_PRIMARY
        )

        if active:
            active_text = ""
            for msg in active[:10]:
                channel = self.bot.get_channel(msg['channel_id'])
                ch_name = channel.mention if channel else f"`{msg['channel_id']}`"
                time_str = format_datetime(datetime.fromisoformat(msg['scheduled_time']))
                preview = truncate_text(msg['content'] or "[Embed]", 40)
                active_text += f"`#{msg['id']}` {ch_name} | {time_str} | {preview}\n"

            if len(active) > 10:
                active_text += f"\n...e mais {len(active) - 10}"

            embed.add_field(name=f"🟢 Ativas ({len(active)})", value=active_text, inline=False)

        if inactive:
            embed.add_field(name=f"⚫ Inativas ({len(inactive)})", value="Mensagens já enviadas", inline=False)

        embed.set_footer(text=f"Servidor: {interaction.guild.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remover", description="🗑️ Remove uma mensagem agendada")
    @app_commands.describe(mensagem_id="ID da mensagem a remover")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_remover(self, interaction: discord.Interaction, mensagem_id: int):
        """Remove uma mensagem agendada"""

        msg = self.db.get_message_by_id(mensagem_id)

        if not msg or msg['guild_id'] != interaction.guild_id:
            return await interaction.response.send_message(
                "❌ Mensagem não encontrada!", ephemeral=True
            )

        if msg['author_id'] != interaction.user.id and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "⛔ Você só pode remover suas próprias mensagens!", ephemeral=True
            )

        self.db.delete_message(mensagem_id)

        embed = discord.Embed(
            title="🗑️ Mensagem Removida",
            description=f"Mensagem #{mensagem_id} removida com sucesso!",
            color=Config.COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="ℹ️ Detalhes de uma mensagem agendada")
    @app_commands.describe(mensagem_id="ID da mensagem")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_info(self, interaction: discord.Interaction, mensagem_id: int):
        """Mostra detalhes de uma mensagem"""

        msg = self.db.get_message_by_id(mensagem_id)

        if not msg or msg['guild_id'] != interaction.guild_id:
            return await interaction.response.send_message(
                "❌ Mensagem não encontrada!", ephemeral=True
            )

        channel = self.bot.get_channel(msg['channel_id'])
        author = self.bot.get_user(msg['author_id'])

        embed = discord.Embed(
            title=f"ℹ️ Detalhes da Mensagem #{mensagem_id}",
            color=Config.COLOR_INFO
        )

        embed.add_field(name="🆔 ID", value=f"`{msg['id']}`", inline=True)
        embed.add_field(name="📺 Canal", value=channel.mention if channel else "N/A", inline=True)
        embed.add_field(name="👤 Autor", value=author.mention if author else f"`{msg['author_id']}`", inline=True)
        embed.add_field(name="⏰ Agendado para", value=format_datetime(datetime.fromisoformat(msg['scheduled_time'])), inline=True)
        embed.add_field(name="🔄 Recorrência", value=msg['recurrence'].replace('once', 'Única').replace('daily', 'Diária').replace('weekly', 'Semanal'), inline=True)
        embed.add_field(name="📊 Envios", value=f"{msg['send_count'] or 0} vez(es)", inline=True)
        embed.add_field(name="📌 Status", value="🟢 Ativa" if msg['is_active'] else "⚫ Inativa", inline=True)
        embed.add_field(name="📝 Conteúdo", value=truncate_text(msg['content'] or "[Embed]", 500), inline=False)

        if msg['last_sent']:
            embed.add_field(name="📤 Último envio", value=format_datetime(datetime.fromisoformat(msg['last_sent'])), inline=True)

        embed.set_footer(text=f"Criado em: {msg['created_at']}")
        await interaction.response.send_message(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # 📢 ANÚNCIOS RÁPIDOS
    # ═══════════════════════════════════════════════════════════

    @app_commands.command(name="anuncio-rapido", description="⚡ Envia um anúncio rápido com @everyone")
    @app_commands.describe(
        canal="Canal do anúncio",
        mensagem="Conteúdo do anúncio"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_anuncio_rapido(self, interaction: discord.Interaction,
                                    canal: discord.TextChannel,
                                    mensagem: str):
        """Envia anúncio rápido"""

        embed = discord.Embed(
            title="📢 Anúncio",
            description=mensagem,
            color=Config.COLOR_WARNING,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await canal.send("@everyone", embed=embed)
        await interaction.response.send_message(f"✅ Anúncio enviado em {canal.mention}!")

    @app_commands.command(name="anuncio-embed", description="🎨 Envia um anúncio com embed")
    @app_commands.describe(
        canal="Canal do anúncio",
        titulo="Título do anúncio",
        descricao="Descrição",
        cor="Cor em hex (opcional)",
        imagem="URL da imagem (opcional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_anuncio_embed(self, interaction: discord.Interaction,
                                   canal: discord.TextChannel,
                                   titulo: str,
                                   descricao: str,
                                   cor: str = None,
                                   imagem: str = None):
        """Envia anúncio com embed"""

        embed_color = Config.COLOR_WARNING
        if cor:
            try:
                embed_color = int(cor.replace('#', ''), 16)
            except:
                pass

        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=embed_color,
            timestamp=datetime.now()
        )
        if imagem:
            embed.set_image(url=imagem)
        embed.set_footer(text=f"Por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await canal.send("@everyone", embed=embed)
        await interaction.response.send_message(f"✅ Anúncio embed enviado em {canal.mention}!")

    # ═══════════════════════════════════════════════════════════
    # ⚙️ GERENCIAMENTO
    # ═══════════════════════════════════════════════════════════

    @app_commands.command(name="config", description="⚙️ Configurações do servidor")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_config(self, interaction: discord.Interaction):
        """Mostra configurações do servidor"""

        settings = self.db.get_guild_settings(interaction.guild_id)
        log_channel = self.bot.get_channel(settings['log_channel_id']) if settings['log_channel_id'] else None

        embed = discord.Embed(
            title=f"⚙️ Configurações - {interaction.guild.name}",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(name="🌍 Fuso horário", value=f"`{settings['timezone']}`", inline=True)
        embed.add_field(name="📊 Limite mensagens", value=f"`{settings['max_messages']}`", inline=True)
        embed.add_field(name="📢 Allow @everyone", value="✅ Sim" if settings['allow_everyone'] else "❌ Não", inline=True)
        embed.add_field(name="📝 Canal de logs", value=log_channel.mention if log_channel else "Não configurado", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stats", description="📊 Estatísticas do servidor")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_stats(self, interaction: discord.Interaction):
        """Mostra estatísticas"""

        messages = self.db.get_scheduled_messages(guild_id=interaction.guild_id, active_only=False)
        active = len([m for m in messages if m['is_active']])
        inactive = len([m for m in messages if not m['is_active']])
        total_sent = sum(m['send_count'] or 0 for m in messages)

        embed = discord.Embed(
            title=f"📊 Estatísticas - {interaction.guild.name}",
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

        embed.set_footer(text=f"Servidor: {interaction.guild.name}")
        await interaction.response.send_message(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # 🛠️ UTILITÁRIOS
    # ═══════════════════════════════════════════════════════════

    @app_commands.command(name="ping", description="🏓 Verifica a latência do bot")
    async def slash_ping(self, interaction: discord.Interaction):
        """Verifica latência"""
        latency = round(self.bot.latency * 1000)
        color = Config.COLOR_SUCCESS if latency < 100 else Config.COLOR_WARNING if latency < 300 else Config.COLOR_ERROR

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: `{latency}ms`",
            color=color
        )
        embed.add_field(name="📊 Status", value="🟢 Excelente" if latency < 100 else "🟡 Bom" if latency < 300 else "🔴 Alto", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ajuda", description="❓ Mostra a ajuda do bot")
    async def slash_ajuda(self, interaction: discord.Interaction):
        """Ajuda geral"""

        embed = discord.Embed(
            title="🤖 Bot de Agendamento - Ajuda",
            description="Bot avançado para agendamento de mensagens automáticas!",
            color=Config.COLOR_PRIMARY
        )

        embed.add_field(
            name="📅 Agendamento",
            value=(
                "`/agendar-texto` - Mensagem de texto\n"
                "`/agendar-embed` - Mensagem com embed\n"
                "`/agendar-anuncio` - Anúncio com @everyone\n"
                "`/lista` - Listar agendadas\n"
                "`/info` - Detalhes de mensagem\n"
                "`/remover` - Remover mensagem"
            ),
            inline=False
        )

        embed.add_field(
            name="📢 Anúncios",
            value=(
                "`/anuncio-rapido` - Anúncio instantâneo\n"
                "`/anuncio-embed` - Anúncio com embed"
            ),
            inline=False
        )

        embed.add_field(
            name="⚙️ Gerenciamento",
            value=(
                "`/config` - Configurações\n"
                "`/stats` - Estatísticas"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠️ Utilitários",
            value=(
                "`/ping` - Latência\n"
                "`/ajuda` - Esta mensagem"
            ),
            inline=False
        )

        embed.set_footer(text="v2.1.0 | Slash Commands")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="horario", description="🕐 Mostra a hora atual")
    async def slash_horario(self, interaction: discord.Interaction):
        """Hora atual"""
        now = datetime.now()
        embed = discord.Embed(
            title="🕐 Hora Atual",
            description=f"**{now.strftime('%d/%m/%Y %H:%M:%S')}**",
            color=Config.COLOR_INFO
        )
        embed.set_footer(text="Fuso horário do servidor do bot")
        await interaction.response.send_message(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # 🔄 ERROR HANDLERS
    # ═══════════════════════════════════════════════════════════

    @slash_agendar_texto.error
    @slash_agendar_embed.error
    @slash_agendar_anuncio.error
    @slash_lista.error
    @slash_remover.error
    @slash_info.error
    @slash_config.error
    @slash_stats.error
    @slash_anuncio_rapido.error
    @slash_anuncio_embed.error
    async def on_slash_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Tratamento de erros nos slash commands"""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "⛔ Você não tem permissão para usar este comando.", 
                ephemeral=True
            )
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ Aguarde {error.retry_after:.0f} segundos para usar este comando.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Ocorreu um erro inesperado.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
