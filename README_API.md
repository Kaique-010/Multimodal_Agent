# 🚀 API do Agente Multimodal

API REST construída com FastAPI para expor o agente inteligente multimodal para frontends e outras aplicações.

## 📋 Endpoints Disponíveis

### 1. **Health Check**

```
GET /
GET /health
```

Verifica se a API está funcionando.

**Resposta:**

```json
{
  "status": "healthy",
  "message": "API está operacional"
}
```

### 2. **Chat com o Agente**

```
POST /chat
```

Endpoint principal para interagir com o agente.

**Request Body:**

```json
{
  "message": "Como emitir uma nota fiscal?",
  "thread_id": "user-123" // opcional
}
```

**Response:**

```json
{
  "response": "Para emitir uma nota fiscal...",
  "thread_id": "user-123"
}
```

### 3. **Listar Ferramentas**

```
GET /tools
```

Lista todas as ferramentas disponíveis no agente.

**Resposta:**

```json
{
  "tools": [
    {
      "name": "rag_url_resposta",
      "description": "Extrai conteúdo de uma URL e responde perguntas usando RAG"
    }
  ]
}
```

## 🛠️ Como Usar

### 1. **Iniciar o Servidor**

```bash
python api_server.py
```

O servidor estará disponível em: `http://localhost:8000`

### 2. **Documentação Interativa**

Acesse: `http://localhost:8000/docs` para ver a documentação Swagger.

### 3. **Testar a API**

```bash
python test_api.py
```

## 💻 Exemplo de Uso em JavaScript

```javascript
// Função para enviar mensagem ao agente
async function chatWithAgent(message, threadId = 'default') {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      thread_id: threadId,
    }),
  })

  const data = await response.json()
  return data.response
}

// Exemplo de uso
chatWithAgent('Como emitir uma nota fiscal?').then((response) =>
  console.log(response)
)
```

## 🔧 Exemplo de Uso em Python

```python
import requests

def chat_with_agent(message, thread_id="default"):
    url = "http://localhost:8000/chat"
    payload = {
        "message": message,
        "thread_id": thread_id
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]

# Exemplo de uso
response = chat_with_agent("Como emitir uma nota fiscal?")
print(response)
```

## 🌐 Configuração CORS

A API está configurada para aceitar requisições de qualquer origem (`allow_origins=["*"]`).

**Para produção**, altere em `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://meusite.com"],  # Especificar domínios
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🔒 Segurança

- Configure variáveis de ambiente no arquivo `.env`
- Em produção, use HTTPS
- Implemente autenticação se necessário
- Limite as origens CORS

## 📊 Ferramentas do Agente

O agente possui 5 ferramentas principais:

1. **rag_url_resposta_vetorial** - Busca vetorial em manuais
2. **rag_url_resposta** - Extração de conteúdo de URLs
3. **inspector_faiss** - Inspeção do índice FAISS
4. **faiss_condicional_qa** - QA com limiar de similaridade
5. **salvar_dataset_finetuning** - Coleta de dados para treinamento

## 🚀 Deploy com Gunicorn e Nginx

### 1. **Configuração do Gunicorn**

Instale o Gunicorn:

```bash
pip install gunicorn
```

Crie o arquivo `gunicorn.conf.py`:

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

Execute com Gunicorn:

```bash
gunicorn -c gunicorn.conf.py api_server:app
```

### 2. **Configuração do Nginx**

Crie o arquivo `/etc/nginx/sites-available/spartacus-api`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    # Logs
    access_log /var/log/nginx/spartacus-api.access.log;
    error_log /var/log/nginx/spartacus-api.error.log;

    # Proxy para Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Arquivos estáticos (se houver)
    location /static/ {
        alias /caminho/para/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Compressão
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

Ative o site:

```bash
sudo ln -s /etc/nginx/sites-available/spartacus-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. **Configuração SSL com Let's Encrypt**

Instale o Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

Obtenha o certificado SSL:

```bash
sudo certbot --nginx -d seu-dominio.com
```

### 4. **Serviço Systemd**

Crie o arquivo `/etc/systemd/system/spartacus-api.service`:

```ini
[Unit]
Description=Spartacus API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/Multimodal
Environment=PATH=/caminho/para/venv/bin
ExecStart=/caminho/para/venv/bin/gunicorn -c gunicorn.conf.py api_server:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Ative o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable spartacus-api
sudo systemctl start spartacus-api
sudo systemctl status spartacus-api
```

### 5. **Variáveis de Ambiente para Produção**

Crie o arquivo `.env.production`:

```bash
# OpenAI
OPENAI_API_KEY=sua_chave_aqui

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Configurações do modelo
CHAT_MODEL=gpt-4o-mini
TEMPERATURE=0

# Configurações de segurança
ALLOWED_HOSTS=["seu-dominio.com"]
SECRET_KEY=sua_chave_secreta_aqui
```

### 6. **Monitoramento e Logs**

Configure rotação de logs no `/etc/logrotate.d/spartacus-api`:

```
/var/log/nginx/spartacus-api.*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
```

### 7. **Script de Deploy Automatizado**

Crie o arquivo `deploy.sh`:

```bash
#!/bin/bash

# Deploy script para Spartacus API
set -e

echo "🚀 Iniciando deploy da Spartacus API..."

# Atualizar código
git pull origin main

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Testar configuração
python -c "import api_server; print('✅ Configuração OK')"

# Reiniciar serviços
sudo systemctl restart spartacus-api
sudo systemctl reload nginx

# Verificar status
sleep 5
curl -f http://localhost:8000/health || exit 1

echo "✅ Deploy concluído com sucesso!"
```

### 8. **Backup e Recuperação**

Script de backup `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backup/spartacus-api"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
cp db/manuais.db $BACKUP_DIR/manuais_$DATE.db

# Backup dos índices FAISS
cp -r faiss/ $BACKUP_DIR/faiss_$DATE/

# Backup das configurações
cp -r configuracoes/ $BACKUP_DIR/config_$DATE/

echo "✅ Backup criado em $BACKUP_DIR"
```

### 9. **Checklist de Deploy**

- [ ] Servidor configurado com Python 3.8+
- [ ] Nginx instalado e configurado
- [ ] Gunicorn instalado
- [ ] Certificado SSL configurado
- [ ] Variáveis de ambiente definidas
- [ ] Serviço systemd criado
- [ ] Logs configurados
- [ ] Backup automatizado
- [ ] Monitoramento ativo
- [ ] Teste de carga realizado

### 10. **Comandos Úteis**

```bash
# Verificar status dos serviços
sudo systemctl status spartacus-api nginx

# Ver logs em tempo real
sudo journalctl -u spartacus-api -f
sudo tail -f /var/log/nginx/spartacus-api.access.log

# Reiniciar serviços
sudo systemctl restart spartacus-api
sudo systemctl reload nginx

# Testar configuração
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "teste", "thread_id": "deploy-test"}'
```

## 🐳 Deploy com Docker (Alternativa)

Para deploy com Docker, considere usar:

- **Gunicorn** com workers
- **Docker** para containerização
- **Nginx** como proxy reverso
- **Variáveis de ambiente** para configurações sensíveis
