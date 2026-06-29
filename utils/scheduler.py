"""
⏰ Sistema de Agendamento Inteligente
"""

import discord
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from discord.ext import tasks

logger = logging.getLogger('DiscordBot')

class MessageScheduler:
    """Gerenciador de agendamento de mensagens"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self._running = False
        self._last_checked = {}  # Evita enviar a mesma mensagem 2x no mesmo minuto

    def start(self):
        """Inicia o loop de verificação"""
        if not self._running:
            self.check_scheduled_messages.start()
            self._running = True
            logger.info("✅ Scheduler iniciado")

    def stop(self):
        """Para o loop de verificação"""
        if self._running:
            self.check_scheduled_messages.cancel()
            self._running = False
            logger.info("🛑 Scheduler parado")

    @tasks.loop(seconds=10)
    async def check_scheduled_messages(self):
        """Verifica e envia mensagens agendadas a cada 10 segundos"""
        try:
            now = datetime.now()
            messages = self.db.get_scheduled_messages(active_only=True)

            logger.info(f"⏰ Scheduler check - {now.strftime('%H:%M:%S')} - {len(messages)} mensagens ativas")

            for msg in messages:
                try:
                    scheduled_time = datetime.fromisoformat(msg['scheduled_time'])
                except Exception as e:
                    logger.error(f"❌ Erro ao parsear data da msg {msg['id']}: {e}")
                    continue

                # Comparar ano, mês, dia, hora, minuto (ignorar segundos)
                now_key = (now.year, now.month, now.day, now.hour, now.minute)
                sched_key = (scheduled_time.year, scheduled_time.month, scheduled_time.day, scheduled_time.hour, scheduled_time.minute)

                # Verificar se já enviamos essa mensagem neste minuto
                last_sent_key = f"{msg['id']}_{now_key}"
                if last_sent_key in self._last_checked:
                    continue

                # Verifica se é hora de enviar (mesmo minuto exato)
                if now_key == sched_key:
                    logger.info(f"🎯 Hora de enviar msg {msg['id']}! Agendado: {scheduled_time.strftime('%d/%m %H:%M')} | Agora: {now.strftime('%d/%m %H:%M')}")
                    await self._send_message(msg)
                    self._last_checked[last_sent_key] = True

        except Exception as e:
            logger.error(f"Erro no scheduler: {e}")

    async def _send_message(self, msg: dict):
        """Envia uma mensagem agendada"""
        try:
            channel = self.bot.get_channel(msg['channel_id'])
            if not channel:
                logger.warning(f"Canal {msg['channel_id']} não encontrado")
                self.db.log_message(msg['id'], msg['guild_id'], msg['channel_id'], 
                                   'failed', 'Canal não encontrado')
                return

            # Preparar embed se existir
            embed = None
            if msg['embed_data']:
                try:
                    import json
                    embed_data = json.loads(msg['embed_data'])
                    embed = discord.Embed.from_dict(embed_data)
                except:
                    pass

            # Enviar mensagem
            if embed:
                await channel.send(content=msg['content'] or None, embed=embed)
            else:
                await channel.send(content=msg['content'])

            # Atualizar contador
            send_count = (msg['send_count'] or 0) + 1
            self.db.update_message(
                msg['id'], 
                last_sent=datetime.now().isoformat(),
                send_count=send_count
            )

            # Log de sucesso
            self.db.log_message(msg['id'], msg['guild_id'], msg['channel_id'], 'success')
            logger.info(f"✅ Mensagem {msg['id']} enviada no canal {msg['channel_id']}")

            # Tratar recorrência
            await self._handle_recurrence(msg)

        except discord.Forbidden:
            logger.error(f"❌ Sem permissão para enviar no canal {msg['channel_id']}")
            self.db.log_message(msg['id'], msg['guild_id'], msg['channel_id'], 
                               'failed', 'Sem permissão')
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem {msg['id']}: {e}")
            self.db.log_message(msg['id'], msg['guild_id'], msg['channel_id'], 
                               'failed', str(e))

    async def _handle_recurrence(self, msg: dict):
        """Processa recorrência da mensagem"""
        recurrence = msg['recurrence']

        if recurrence == 'once':
            self.db.update_message(msg['id'], is_active=0)
            logger.info(f"📝 Mensagem {msg['id']} (única) desativada")

        elif recurrence == 'daily':
            next_time = datetime.fromisoformat(msg['scheduled_time']) + timedelta(days=1)
            self.db.update_message(msg['id'], scheduled_time=next_time.isoformat())
            logger.info(f"🔄 Mensagem {msg['id']} reagendada para {next_time}")

        elif recurrence == 'weekly':
            next_time = datetime.fromisoformat(msg['scheduled_time']) + timedelta(weeks=1)
            self.db.update_message(msg['id'], scheduled_time=next_time.isoformat())
            logger.info(f"🔄 Mensagem {msg['id']} reagendada para {next_time}")

        elif recurrence == 'loop':
            next_time = datetime.fromisoformat(msg['scheduled_time']) + timedelta(weeks=1)
            self.db.update_message(msg['id'], scheduled_time=next_time.isoformat())
            logger.info(f"🔁 LOOP: Mensagem {msg['id']} reagendada para {next_time}")

        elif recurrence == 'custom':
            try:
                import json
                data = json.loads(msg['recurrence_data'] or '{}')
                interval_days = data.get('interval_days', 1)
                next_time = datetime.fromisoformat(msg['scheduled_time']) + timedelta(days=interval_days)
                self.db.update_message(msg['id'], scheduled_time=next_time.isoformat())
                logger.info(f"🔄 Mensagem {msg['id']} reagendada para {next_time}")
            except:
                self.db.update_message(msg['id'], is_active=0)

        elif recurrence == 'count':
            try:
                import json
                data = json.loads(msg['recurrence_data'] or '{}')
                max_count = data.get('max_count', 1)

                if msg['send_count'] >= max_count:
                    self.db.update_message(msg['id'], is_active=0)
                    logger.info(f"📝 Mensagem {msg['id']} atingiu limite de {max_count} envios")
                else:
                    next_time = datetime.fromisoformat(msg['scheduled_time']) + timedelta(days=1)
                    self.db.update_message(msg['id'], scheduled_time=next_time.isoformat())
            except:
                self.db.update_message(msg['id'], is_active=0)

    @check_scheduled_messages.before_loop
    async def before_check(self):
        """Espera o bot estar pronto antes de iniciar"""
        await self.bot.wait_until_ready()
