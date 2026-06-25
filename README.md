# 🤖 Bot Discord Avançado - Agendador de Mensagens

Um bot Discord completo e avançado para agendamento automático de mensagens, anúncios e embeds em horários definidos.

> 🚀 **Pronto para Railway!** Configure as variáveis de ambiente no painel do Railway e deploy com 1 clique.

---

## ✨ Funcionalidades

### 📅 Agendamento de Mensagens
- **Mensagens de texto** - Agende mensagens simples para qualquer canal
- **Mensagens com Embed** - Crie embeds interativos com título, descrição, cor, imagem e rodapé
- **Anúncios com @everyone** - Envie anúncios importantes para toda a comunidade
- **Recorrência** - Configure mensagens diárias, semanais ou com intervalo personalizado
- **Edição e remoção** - Gerencie mensagens agendadas facilmente

### 📢 Sistema de Anúncios
- **Anúncio rápido** - Envie anúncios instantâneos
- **Anúncio com embed** - Crie anúncios profissionais com wizard interativo
- **Templates** - Use templates pré-definidos (boas-vindas, eventos, atualizações, sorteios)

### ⚙️ Gerenciamento
- **Configurações por servidor** - Fuso horário, limite de mensagens, canal de logs
- **Estatísticas** - Acompanhe mensagens ativas, inativas e enviadas
- **Limpeza automática** - Remova mensagens antigas automaticamente

---

## 🚀 Deploy no Railway (Recomendado)

### 1. Crie um projeto no Railway
- Acesse [railway.app](https://railway.app) e faça login
- Clique em **"New Project"** → **"Deploy from GitHub repo"**

### 2. Configure as Variáveis de Ambiente
No painel do Railway, vá em **Variables** e adicione:

| Variável | Valor | Obrigatório |
|----------|-------|-------------|
| `DISCORD_TOKEN` | Seu token do bot | ✅ Sim |
| `BOT_PREFIX` | `!` (ou outro) | ❌ Não (padrão: `!`) |
| `OWNER_IDS` | `123456789,987654321` | ❌ Não |

> 💡 **Como obter o token:**
> 1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
> 2. Crie uma nova aplicação
> 3. Vá em "Bot" e clique em "Add Bot"
> 4. Copie o token e cole no Railway

### 3. Deploy automático
O Railway detectará automaticamente o `nixpacks.toml` e fará o deploy.

---

## 🖥️ Rodando Localmente

### 1. Clone o projeto
```bash
git clone <url-do-projeto>
cd discord_bot
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o ambiente
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite `.env` com suas configurações:
```env
DISCORD_TOKEN=seu_token_aqui
BOT_PREFIX=!
OWNER_IDS=123456789
```

### 4. Execute
```bash
python main.py
```

---

## 📖 Comandos

### 📅 Agendamento
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!agendar` | Menu principal de agendamento | Gerenciar Mensagens |
| `!agendar texto #canal DD/MM/YYYY HH:MM mensagem` | Agenda mensagem de texto | Gerenciar Mensagens |
| `!agendar embed #canal DD/MM/YYYY HH:MM` | Agenda embed interativo | Gerenciar Mensagens |
| `!agendar anuncio #canal DD/MM/YYYY HH:MM mensagem` | Agenda anúncio com @everyone | Administrador |
| `!agendar lista` | Lista mensagens agendadas | Gerenciar Mensagens |
| `!agendar info <id>` | Detalhes de uma mensagem | Gerenciar Mensagens |
| `!agendar editar <id>` | Edita uma mensagem | Gerenciar Mensagens |
| `!agendar remover <id>` | Remove uma mensagem | Gerenciar Mensagens |

### 📢 Anúncios
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!anuncio rapido #canal mensagem` | Anúncio instantâneo | Administrador |
| `!anuncio embed #canal` | Anúncio com embed | Administrador |
| `!anuncio template #canal nome vars` | Usa template | Administrador |
| `!anuncio templates` | Lista templates | Administrador |

### ⚙️ Gerenciamento
| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `!config` | Configurações do servidor | Administrador |
| `!config log #canal` | Define canal de logs | Administrador |
| `!config limite <número>` | Limite de mensagens | Administrador |
| `!config everyone <on/off>` | Permite @everyone | Administrador |
| `!stats` | Estatísticas | Gerenciar Mensagens |
| `!limpar <dias>` | Limpa mensagens antigas | Administrador |

### 🛠️ Utilitários
| Comando | Descrição |
|---------|-----------|
| `!ping` | Verifica latência |
| `!ajuda` | Ajuda geral |
| `!ajuda <comando>` | Ajuda específica |
| `!horario` | Hora atual do bot |

---

## 📋 Exemplos

### Agendar mensagem de texto
```
!agendar texto #geral 25/12/2026 09:00 Feliz Natal a todos! 🎄
```

### Agendar embed
```
!agendar embed #avisos 01/01/2026 00:00
```
O bot irá fazer perguntas interativas para criar o embed.

### Agendar anúncio
```
!agendar anuncio #anuncios 20/12/2026 18:00 Evento especial hoje às 20h!
```

### Usar template
```
!anuncio template #geral evento nome=Campeonato;data=25/12;hora=20:00;local=#eventos;descricao=Participe!
```

---

## 🔄 Recorrência

Ao agendar uma mensagem, o bot perguntará sobre recorrência:
- **Única** - Envia uma vez e remove
- **Diária** - Envia todos os dias no mesmo horário
- **Semanal** - Envia toda semana
- **Personalizada** - Define intervalo em dias

---

## 🗄️ Banco de Dados

O bot usa SQLite para armazenar:
- Mensagens agendadas
- Logs de envio
- Configurações por servidor

Arquivo: `data/scheduled_messages.db`

> ⚠️ No Railway, o banco SQLite fica no disco efêmero. Se o container reiniciar, os dados podem ser perdidos. Para produção, considere migrar para PostgreSQL.

---

## 📁 Estrutura do Projeto

```
discord_bot/
├── main.py                    # Arquivo principal
├── .env.example               # Exemplo de configurações locais
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
├── railway.json               # Config do Railway
├── nixpacks.toml              # Build do Railway
├── Procfile                   # Processo do Railway
├── data/                      # Banco de dados e logs
│   ├── scheduled_messages.db
│   └── bot.log
├── utils/                     # Utilitários
│   ├── config.py              # Configurações (Railway + .env)
│   ├── database.py            # Banco de dados
│   ├── scheduler.py           # Sistema de agendamento
│   └── helpers.py             # Funções auxiliares
└── cogs/                      # Módulos de comandos
    ├── scheduled_messages.py  # Agendamento principal
    ├── announcements.py       # Anúncios avançados
    ├── management.py          # Gerenciamento
    ├── utilities.py           # Utilitários
    └── events.py              # Eventos
```

---

## 🛡️ Permissões Recomendadas

Para funcionamento completo, o bot precisa de:
- ✅ Ler mensagens
- ✅ Enviar mensagens
- ✅ Enviar embeds
- ✅ Mencionar @everyone
- ✅ Ler histórico de mensagens
- ✅ Gerenciar mensagens

---

## 📝 Notas sobre Railway

- O bot usa **variáveis de ambiente** do Railway, não `.env`
- O arquivo `config.py` lê `os.getenv()` que funciona tanto no Railway quanto localmente
- O `nixpacks.toml` configura o build e start automático
- O `railway.json` define política de restart em caso de falha

---

## 💬 Suporte

Em caso de dúvidas ou problemas:
1. Verifique se o `DISCORD_TOKEN` está correto nas variáveis do Railway
2. Confira as permissões do bot no Discord Developer Portal
3. Veja os logs no painel do Railway
