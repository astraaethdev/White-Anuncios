"""
📢 Cog: Anúncios Avançados
Sistema de anúncios com templates, confirmação e estatísticas
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta

from utils.config import Config
from utils.helpers import parse_datetime, format_datetime, truncate_text

class Announcements(commands.Cog):
    """Sistema avançado de anúncios"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.group(name="anuncio", aliases=["announce", "an"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def announce_group(self, ctx):
        """📢 Sistema de anúncios avançado"""
        embed = discord.Embed(
            title="📢 Sistema de Anúncios",
            description="Crie anúncios profissionais para seu servidor!",
            color=Config.COLOR_WARNING
        )
        embed.add_field(
            name="Comandos:",
            value=(
                "`!anuncio rapido` - Anúncio rápido\n"
                "`!anuncio embed` - Anúncio com embed\n"
                "`!anuncio template` - Usar template\n"
                "`!anuncio templates` - Ver templates disponíveis"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @announce_group.command(name="rapido", aliases=["quick", "r"])
    @commands.has_permissions(administrator=True)
    async def quick_announce(self, ctx, channel: discord.TextChannel, *, content: str):
        """
        ⚡ Envia um anúncio rápido com @everyone
        Uso: !anuncio rapido #canal mensagem
        """
        embed = discord.Embed(
            title="📢 Anúncio",
            description=content,
            color=Config.COLOR_WARNING,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await channel.send("@everyone", embed=embed)
        await ctx.send(f"✅ Anúncio enviado em {channel.mention}!")

    @announce_group.command(name="embed", aliases=["e"])
    @commands.has_permissions(administrator=True)
    async def embed_announce(self, ctx, channel: discord.TextChannel):
        """
        🎨 Cria um anúncio com embed interativo
        Uso: !anuncio embed #canal
        """
        await ctx.send("🎨 **Wizard de Anúncio** - Responda as perguntas")

        # Título
        await ctx.send("📝 Digite o **título** do anúncio:")
        try:
            title_msg = await self.bot.wait_for('message', timeout=120.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado!")

        # Descrição
        await ctx.send("📝 Digite a **descrição** do anúncio:")
        try:
            desc_msg = await self.bot.wait_for('message', timeout=180.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado!")

        # Cor
        await ctx.send("🎨 Digite a **cor** (hex, ex: #FF5733) ou `pular`:")
        try:
            color_msg = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            color_msg = type('obj', (object,), {'content': 'pular'})

        color = Config.COLOR_WARNING
        if color_msg.content.lower() != 'pular':
            try:
                color = int(color_msg.content.replace('#', ''), 16)
            except:
                pass

        # Imagem
        await ctx.send("🖼️ Envie uma **URL de imagem** ou `pular`:")
        try:
            img_msg = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            img_msg = type('obj', (object,), {'content': 'pular'})

        # Thumbnail
        await ctx.send("🖼️ Envie uma **URL de thumbnail** ou `pular`:")
        try:
            thumb_msg = await self.bot.wait_for('message', timeout=60.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            thumb_msg = type('obj', (object,), {'content': 'pular'})

        # Criar embed
        embed = discord.Embed(
            title=title_msg.content,
            description=desc_msg.content,
            color=color,
            timestamp=datetime.now()
        )

        if img_msg.content.lower() != 'pular' and img_msg.content.startswith('http'):
            embed.set_image(url=img_msg.content)

        if thumb_msg.content.lower() != 'pular' and thumb_msg.content.startswith('http'):
            embed.set_thumbnail(url=thumb_msg.content)

        embed.set_footer(text=f"Por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        # Preview
        await ctx.send("👁️ **Preview:**", embed=embed)
        await ctx.send("✅ Deseja enviar? Digite **enviar** para confirmar:")

        try:
            confirm = await self.bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Operação cancelada.")

        if confirm.content.lower() == 'enviar':
            await channel.send("@everyone", embed=embed)
            await ctx.send(f"✅ Anúncio enviado em {channel.mention}!")
        else:
            await ctx.send("❌ Envio cancelado.")

    @announce_group.command(name="template", aliases=["t"])
    @commands.has_permissions(administrator=True)
    async def template_announce(self, ctx, channel: discord.TextChannel, template_name: str, *, variables: str = ""):
        """
        📋 Usa um template de anúncio
        Uso: !anuncio template #canal nome_template var1=valor1;var2=valor2
        """
        templates = {
            "boas_vindas": {
                "title": "🎉 Bem-vindo ao {server}!",
                "description": "Olá {user}! Seja muito bem-vindo ao nosso servidor.\n\nLeia as regras em {rules_channel} e aproveite!",
                "color": 0x57F287
            },
            "evento": {
                "title": "🎊 Evento: {nome}",
                "description": "📅 Data: {data}\n⏰ Horário: {hora}\n📍 Local: {local}\n\n{descricao}",
                "color": 0xEB459E
            },
            "atualizacao": {
                "title": "🔄 Atualização do Servidor",
                "description": "**Novidades:**\n{novidades}\n\n**Correções:**\n{correcoes}",
                "color": 0x5865F2
            },
            "sorteio": {
                "title": "🎁 Sorteio: {premio}",
                "description": "🎉 Participe do nosso sorteio!\n\n🏆 Prêmio: {premio}\n📅 Término: {data}\n👥 Vencedores: {vencedores}\n\nReaja com 🎉 para participar!",
                "color": 0xFEE75C
            }
        }

        if template_name not in templates:
            available = ", ".join(f"`{k}`" for k in templates.keys())
            return await ctx.send(f"❌ Template não encontrado! Disponíveis: {available}")

        template = templates[template_name]

        # Parse variáveis
        vars_dict = {}
        if variables:
            for pair in variables.split(';'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    vars_dict[key.strip()] = value.strip()

        # Substituir variáveis
        title = template["title"]
        description = template["description"]

        for key, value in vars_dict.items():
            title = title.replace(f"{{{key}}}", value)
            description = description.replace(f"{{{key}}}", value)

        # Variáveis padrão
        title = title.replace("{server}", ctx.guild.name)
        title = title.replace("{user}", ctx.author.mention)

        embed = discord.Embed(
            title=title,
            description=description,
            color=template["color"],
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send("👁️ **Preview:**", embed=embed)
        await ctx.send("✅ Deseja enviar? Digite **enviar**:")

        try:
            confirm = await self.bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Operação cancelada.")

        if confirm.content.lower() == 'enviar':
            await channel.send("@everyone", embed=embed)
            await ctx.send(f"✅ Anúncio enviado em {channel.mention}!")
        else:
            await ctx.send("❌ Envio cancelado.")

    @announce_group.command(name="templates", aliases=["list"])
    @commands.has_permissions(administrator=True)
    async def list_templates(self, ctx):
        """
        📋 Lista templates disponíveis
        """
        embed = discord.Embed(
            title="📋 Templates de Anúncio",
            description="Templates disponíveis para uso rápido:",
            color=Config.COLOR_INFO
        )

        templates_info = {
            "boas_vindas": "Mensagem de boas-vindas para novos membros",
            "evento": "Anúncio de evento com data e local",
            "atualizacao": "Notas de atualização do servidor",
            "sorteio": "Anúncio de sorteio com reações"
        }

        for name, desc in templates_info.items():
            embed.add_field(name=f"📌 `{name}`", value=desc, inline=False)

        embed.add_field(
            name="📖 Uso:",
            value="`!anuncio template #canal nome_template var1=valor1;var2=valor2`",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Announcements(bot))
