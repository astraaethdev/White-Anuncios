"""
📅 Cog: Mensagens Agendadas
Comandos principais para agendar, listar, editar e remover mensagens
"""

import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime, timedelta

from utils.config import Config
from utils.helpers import parse_datetime, format_datetime, truncate_text

class ScheduledMessages(commands.Cog):
    """Sistema completo de agendamento de mensagens"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.group(name="agendar", aliases=["schedule", "ag"], invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def schedule_group(self, ctx):
        """📅 Sistema de agendamento de mensagens"""
        embed = discord.Embed(
            title="📅 Sistema de Agendamento",
            description="Gerencie mensagens automáticas no servidor!",
            color=Config.COLOR_PRIMARY
        )
        embed.add_field(
            name="Comandos disponíveis:",
            value=(
                "`!agendar texto` - Agendar mensagem de texto\n"
                "`!agendar embed` - Agendar mensagem com embed\n"
                "`!agendar anuncio` - Agendar anúncio com @everyone\n"
                "`!agendar lista` - Ver mensagens agendadas\n"
                "`!agendar editar` - Editar mensagem agendada\n"
                "`!agendar remover` - Remover mensagem agendada\n"
                "`!agendar info` - Detalhes de uma mensagem"
            ),
            inline=False
        )
        embed.add_field(
            name="📖 Exemplos:",
            value=(
                "`!agendar texto #geral 15:30 Boa tarde a todos!`\n"
                "`!agendar embed #avisos 25/12/2026 09:00`\n"
                "`!agendar texto #geral 20:00 --recorrencia diaria Boa noite!`"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @schedule_group.command(name="texto", aliases=["text", "t"])
    @commands.has_permissions(manage_messages=True)
    async def schedule_text(self, ctx, channel: discord.TextChannel, datetime_str: str, *, content: str):
        """
        📝 Agenda uma mensagem de texto
        Uso: !agendar texto #canal DD/MM/YYYY HH:MM mensagem
        """
        scheduled_time = parse_datetime(datetime_str)
        if not scheduled_time:
            embed = discord.Embed(
                title="❌ Formato inválido",
                description="Use um dos formatos:\n`DD/MM/YYYY HH:MM` ou `HH:MM`",
                color=Config.COLOR_ERROR
            )
            return await ctx.send(embed=embed)

        if scheduled_time < datetime.now():
            embed = discord.Embed(
                title="⏰ Data no passado",
                description="A data/hora precisa ser no futuro!",
                color=Config.COLOR_WARNING
            )
            return await ctx.send(embed=embed)

        guild_messages = self.db.get_scheduled_messages(guild_id=ctx.guild.id)
        settings = self.db.get_guild_settings(ctx.guild.id)
        if len(guild_messages) >= settings['max_messages']:
            embed = discord.Embed(
                title="⚠️ Limite atingido",
                description=f"Este servidor atingiu o limite de {settings['max_messages']} mensagens agendadas.",
                color=Config.COLOR_WARNING
            )
            return await ctx.send(embed=embed)

        message_id = self.db.add_scheduled_message(
            guild_id=ctx.guild.id,
            channel_id=channel.id,
            author_id=ctx.author.id,
            content=content,
            scheduled_time=scheduled_time.isoformat()
        )

        embed = discord.Embed(
            title="✅ Mensagem Agendada",
            description=f"Sua mensagem foi agendada com sucesso!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="🆔 ID", value=f"`{message_id}`", inline=True)
        embed.add_field(name="📺 Canal", value=channel.mention, inline=True)
        embed.add_field(name="⏰ Data/Hora", value=format_datetime(scheduled_time), inline=True)
        embed.add_field(name="📝 Conteúdo", value=truncate_text(content, 500), inline=False)
        embed.set_footer(text=f"Agendado por {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
        await self._log_action(ctx.guild, f"📅 Nova mensagem agendada (ID: {message_id}) por {ctx.author.mention}")

    @schedule_group.command(name="embed", aliases=["e"])
    @commands.has_permissions(manage_messages=True)
    async def schedule_embed(self, ctx, channel: discord.TextChannel, datetime_str: str):
        """
        🎨 Agenda uma mensagem com embed interativo
        Uso: !agendar embed #canal DD/MM/YYYY HH:MM
        """
        scheduled_time = parse_datetime(datetime_str)
        if not scheduled_time:
            return await ctx.send("❌ Formato de data inválido! Use: `DD/MM/YYYY HH:MM`")

        if scheduled_time < datetime.now():
            return await ctx.send("⏰ A data precisa ser no futuro!")

        await ctx.send("🎨 **Wizard de Embed** - Responda as perguntas (digite `cancelar` a qualquer momento)")

        await ctx.send("📝 Digite o **título** do embed:")
        try:
            title_msg = await self.bot.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Operação cancelada.")

        if title_msg.content.lower() == 'cancelar':
            return await ctx.send("❌ Operação cancelada.")

        await ctx.send("📝 Digite a **descrição** do embed:")
        try:
            desc_msg = await self.bot.wait_for(
                'message',
                timeout=120.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Operação cancelada.")

        if desc_msg.content.lower() == 'cancelar':
            return await ctx.send("❌ Operação cancelada.")

        await ctx.send("🎨 Digite a **cor** do embed (hex, ex: #FF5733) ou digite `pular`:")
        try:
            color_msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Operação cancelada.")

        color = Config.COLOR_PRIMARY
        if color_msg.content.lower() != 'pular':
            try:
                color = int(color_msg.content.replace('#', ''), 16)
            except:
                color = Config.COLOR_PRIMARY

        await ctx.send("🖼️ Envie uma **URL de imagem** ou digite `pular`:")
        try:
            img_msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Operação cancelada.")

        image_url = None
        if img_msg.content.lower() != 'pular' and img_msg.content.startswith('http'):
            image_url = img_msg.content

        await ctx.send("📌 Digite um **rodapé** ou digite `pular`:")
        try:
            footer_msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Operação cancelada.")

        footer = None
        if footer_msg.content.lower() != 'pular':
            footer = footer_msg.content

        embed_data = {
            "title": title_msg.content,
            "description": desc_msg.content,
            "color": color
        }
        if image_url:
            embed_data["image"] = {"url": image_url}
        if footer:
            embed_data["footer"] = {"text": footer}

        await ctx.send("🔄 A mensagem será **recorrente**? Responda: `nao`, `diaria`, `semanal` ou `personalizada`:")
        try:
            rec_msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            rec_msg = type('obj', (object,), {'content': 'nao'})

        recurrence = 'once'
        recurrence_data = None

        if rec_msg.content.lower() == 'diaria':
            recurrence = 'daily'
        elif rec_msg.content.lower() == 'semanal':
            recurrence = 'weekly'
        elif rec_msg.content.lower() == 'personalizada':
            await ctx.send("📅 Digite o intervalo em **dias** (ex: `3` para a cada 3 dias):")
            try:
                interval_msg = await self.bot.wait_for(
                    'message',
                    timeout=60.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                recurrence = 'custom'
                recurrence_data = json.dumps({"interval_days": int(interval_msg.content)})
            except:
                recurrence = 'once'

        message_id = self.db.add_scheduled_message(
            guild_id=ctx.guild.id,
            channel_id=channel.id,
            author_id=ctx.author.id,
            content="",
            scheduled_time=scheduled_time.isoformat(),
            embed_data=json.dumps(embed_data),
            recurrence=recurrence,
            recurrence_data=recurrence_data
        )

        preview_embed = discord.Embed.from_dict(embed_data)
        preview_embed.set_author(name="👁️ Preview do Embed")
        await ctx.send("👁️ **Preview:**", embed=preview_embed)

        embed = discord.Embed(
            title="✅ Embed Agendado",
            description=f"Embed agendado com sucesso!",
            color=Config.COLOR_SUCCESS
        )
        embed.add_field(name="🆔 ID", value=f"`{message_id}`", inline=True)
        embed.add_field(name="📺 Canal", value=channel.mention, inline=True)
        embed.add_field(name="⏰ Data/Hora", value=format_datetime(scheduled_time), inline=True)
        embed.add_field(name="🔄 Recorrência", value=recurrence.replace('once', 'Única').replace('daily', 'Diária').replace('weekly', 'Semanal').replace('custom', 'Personalizada'), inline=True)
        embed.set_footer(text=f"Agendado por {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
        await self._log_action(ctx.guild, f"🎨 Novo embed agendado (ID: {message_id}) por {ctx.author.mention}")

    @schedule_group.command(name="anuncio", aliases=["announcement", "a"])
    @commands.has_permissions(administrator=True)
    async def schedule_announcement(self, ctx, channel: discord.TextChannel, datetime_str: str, *, content: str):
        """
        📢 Agenda um anúncio com @everyone
        Uso: !agendar anuncio #canal DD/MM/YYYY HH:MM mensagem
        """
        scheduled_time = parse_datetime(datetime_str)
        if not scheduled_time:
            return await ctx.send("❌ Formato de data inválido!")

        if scheduled_time < datetime.now():
            return await ctx.send("⏰ A data precisa ser no futuro!")

        full_content = f"@everyone\n\n{content}"

        message_id = self.db.add_scheduled_message(
            guild_id=ctx.guild.id,
            channel_id=channel.id,
            author_id=ctx.author.id,
            content=full_content,
            scheduled_time=scheduled_time.isoformat()
        )

        embed = discord.Embed(
            title="📢 Anúncio Agendado",
            description="Seu anúncio foi agendado com @everyone!",
            color=Config.COLOR_WARNING
        )
        embed.add_field(name="🆔 ID", value=f"`{message_id}`", inline=True)
        embed.add_field(name="📺 Canal", value=channel.mention, inline=True)
        embed.add_field(name="⏰ Data/Hora", value=format_datetime(scheduled_time), inline=True)
        embed.add_field(name="📝 Preview", value=truncate_text(content, 300), inline=False)
        embed.set_footer(text=f"Agendado por {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
        await self._log_action(ctx.guild, f"📢 Anúncio agendado (ID: {message_id}) por {ctx.author.mention}")

    @schedule_group.command(name="lista", aliases=["list", "ls"])
    @commands.has_permissions(manage_messages=True)
    async def list_scheduled(self, ctx):
        """
        📋 Lista todas as mensagens agendadas do servidor
        """
        messages = self.db.get_scheduled_messages(guild_id=ctx.guild.id, active_only=False)

        if not messages:
            embed = discord.Embed(
                title="📭 Sem mensagens agendadas",
                description="Não há mensagens agendadas neste servidor.",
                color=Config.COLOR_INFO
            )
            return await ctx.send(embed=embed)

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
                active_text += f"\n...e mais {len(active) - 10} mensagens"

            embed.add_field(name=f"🟢 Ativas ({len(active)})", value=active_text or "Nenhuma", inline=False)

        if inactive:
            embed.add_field(name=f"⚫ Inativas ({len(inactive)})", value=f"Use `!agendar info <id>` para ver detalhes", inline=False)

        embed.set_footer(text=f"Servidor: {ctx.guild.name}")
        await ctx.send(embed=embed)

    @schedule_group.command(name="info", aliases=["detalhes", "i"])
    @commands.has_permissions(manage_messages=True)
    async def message_info(self, ctx, message_id: int):
        """
        ℹ️ Mostra detalhes de uma mensagem agendada
        Uso: !agendar info <id>
        """
        msg = self.db.get_message_by_id(message_id)

        if not msg or msg['guild_id'] != ctx.guild.id:
            return await ctx.send("❌ Mensagem não encontrada neste servidor!")

        channel = self.bot.get_channel(msg['channel_id'])
        author = self.bot.get_user(msg['author_id'])

        embed = discord.Embed(
            title=f"ℹ️ Detalhes da Mensagem #{message_id}",
            color=Config.COLOR_INFO
        )

        embed.add_field(name="🆔 ID", value=f"`{msg['id']}`", inline=True)
        embed.add_field(name="📺 Canal", value=channel.mention if channel else "N/A", inline=True)
        embed.add_field(name="👤 Autor", value=author.mention if author else f"`{msg['author_id']}`", inline=True)
        embed.add_field(name="⏰ Agendado para", value=format_datetime(datetime.fromisoformat(msg['scheduled_time'])), inline=True)
        embed.add_field(name="🔄 Recorrência", value=msg['recurrence'].replace('once', 'Única').replace('daily', 'Diária').replace('weekly', 'Semanal').replace('custom', 'Personalizada'), inline=True)
        embed.add_field(name="📊 Envios", value=f"{msg['send_count'] or 0} vez(es)", inline=True)
        embed.add_field(name="📌 Status", value="🟢 Ativa" if msg['is_active'] else "⚫ Inativa", inline=True)
        embed.add_field(name="📝 Conteúdo", value=truncate_text(msg['content'] or "[Embed]", 500), inline=False)

        if msg['last_sent']:
            embed.add_field(name="📤 Último envio", value=format_datetime(datetime.fromisoformat(msg['last_sent'])), inline=True)

        embed.set_footer(text=f"Criado em: {msg['created_at']}")
        await ctx.send(embed=embed)

    @schedule_group.command(name="editar", aliases=["edit", "e"])
    @commands.has_permissions(manage_messages=True)
    async def edit_message(self, ctx, message_id: int):
        """
        ✏️ Edita uma mensagem agendada
        Uso: !agendar editar <id>
        """
        msg = self.db.get_message_by_id(message_id)

        if not msg or msg['guild_id'] != ctx.guild.id:
            return await ctx.send("❌ Mensagem não encontrada!")

        if msg['author_id'] != ctx.author.id and not ctx.author.guild_permissions.administrator:
            return await ctx.send("⛔ Você só pode editar suas próprias mensagens!")

        embed = discord.Embed(
            title=f"✏️ Editar Mensagem #{message_id}",
            description="O que deseja editar?\n1️⃣ Conteúdo\n2️⃣ Data/Hora\n3️⃣ Canal\n4️⃣ Cancelar",
            color=Config.COLOR_WARNING
        )
        await ctx.send(embed=embed)

        try:
            choice_msg = await self.bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado!")

        choice = choice_msg.content.strip()

        if choice == '1':
            await ctx.send("📝 Digite o novo conteúdo:")
            try:
                new_msg = await self.bot.wait_for('message', timeout=120.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado!")
            self.db.update_message(message_id, content=new_msg.content)
            await ctx.send("✅ Conteúdo atualizado!")

        elif choice == '2':
            await ctx.send("⏰ Digite a nova data/hora (DD/MM/YYYY HH:MM):")
            try:
                new_time_msg = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado!")

            new_time = parse_datetime(new_time_msg.content)
            if not new_time:
                return await ctx.send("❌ Formato inválido!")

            self.db.update_message(message_id, scheduled_time=new_time.isoformat())
            await ctx.send(f"✅ Data atualizada para {format_datetime(new_time)}!")

        elif choice == '3':
            await ctx.send("📺 Mencione o novo canal:")
            try:
                new_ch_msg = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado!")

            channel = new_ch_msg.channel_mentions[0] if new_ch_msg.channel_mentions else None
            if not channel:
                return await ctx.send("❌ Canal não encontrado!")

            self.db.update_message(message_id, channel_id=channel.id)
            await ctx.send(f"✅ Canal atualizado para {channel.mention}!")

        else:
            await ctx.send("❌ Edição cancelada.")

    @schedule_group.command(name="remover", aliases=["delete", "del", "rm"])
    @commands.has_permissions(manage_messages=True)
    async def remove_message(self, ctx, message_id: int):
        """
        🗑️ Remove uma mensagem agendada
        Uso: !agendar remover <id>
        """
        msg = self.db.get_message_by_id(message_id)

        if not msg or msg['guild_id'] != ctx.guild.id:
            return await ctx.send("❌ Mensagem não encontrada!")

        if msg['author_id'] != ctx.author.id and not ctx.author.guild_permissions.administrator:
            return await ctx.send("⛔ Você só pode remover suas próprias mensagens!")

        embed = discord.Embed(
            title="🗑️ Confirmar Remoção",
            description=f"Deseja realmente remover a mensagem #{message_id}?\nDigite **confirmar** para prosseguir.",
            color=Config.COLOR_ERROR
        )
        await ctx.send(embed=embed)

        try:
            confirm = await self.bot.wait_for(
                'message',
                timeout=30.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Operação cancelada.")

        if confirm.content.lower() == 'confirmar':
            self.db.delete_message(message_id)
            await ctx.send(f"🗑️ Mensagem #{message_id} removida com sucesso!")
            await self._log_action(ctx.guild, f"🗑️ Mensagem #{message_id} removida por {ctx.author.mention}")
        else:
            await ctx.send("❌ Operação cancelada.")

    async def _log_action(self, guild: discord.Guild, message: str):
        """Envia log para canal configurado"""
        settings = self.db.get_guild_settings(guild.id)
        if settings['log_channel_id']:
            channel = self.bot.get_channel(settings['log_channel_id'])
            if channel:
                embed = discord.Embed(
                    description=message,
                    color=Config.COLOR_INFO,
                    timestamp=datetime.now()
                )
                embed.set_author(name="📝 Log do Bot", icon_url=guild.icon.url if guild.icon else None)
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ScheduledMessages(bot))
