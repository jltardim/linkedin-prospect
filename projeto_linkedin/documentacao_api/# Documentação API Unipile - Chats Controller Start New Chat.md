\# Documentação API Unipile \- Chats Controller Start New Chat

\#\# 📋 Visão Geral

O endpoint \*\*Start a new chat\*\* permite iniciar conversas com um ou mais participantes no LinkedIn, WhatsApp, Instagram, Telegram e Twitter. Este é um endpoint crítico para automação de vendas, recrutamento, marketing e atendimento ao cliente.

\*\*Capacidades Principais\*\*:  
\- Iniciar conversas com múltiplos participantes  
\- Enviar mensagens formatadas com HTML (LinkedIn Recruiter)  
\- Suporte a anexos (imagens, documentos)  
\- Mensagens de voz (WhatsApp, LinkedIn)  
\- Mensagens de vídeo (LinkedIn)  
\- Definir assunto da conversa (assuntos específicos)  
\- Suporte a opções específicas para Classic, Recruiter e Sales Navigator

Esta documentação aborda a integração completa para desenvolvimento de aplicações Python que automatizam comunicação em massa via LinkedIn e outras plataformas.

\---

\#\# 🔧 Informações Técnicas Básicas

\#\#\# Endpoint  
\`\`\`  
POST https://{subdomain}.unipile.com:{port}/api/v1/chats  
\`\`\`

\#\#\# Método HTTP  
\`\`\`  
POST  
\`\`\`

\#\#\# Base URL Padrão  
\`\`\`  
https://api26.unipile.com:15609/api/v1/chats  
\`\`\`

\#\#\# Content-Type  
\`\`\`  
multipart/form-data (quando há attachments)  
application/json (sem attachments)  
\`\`\`

\#\#\# Descrição  
Inicia uma nova conversa com um ou mais participantes.

⚠️ \*\*Nota Importante\*\*: A documentação interativa não funciona corretamente para parâmetros específicos do LinkedIn (child parameters). O formato correto é \`linkedin\[inmail\] \= true\`, \`linkedin\[api\]...\`

\---

\#\# 🔐 Autenticação

\#\#\# Headers Obrigatórios  
\`\`\`json  
{  
  "accept": "application/json",  
  "X-API-KEY": "sua\_chave\_api"  
}  
\`\`\`

\#\#\# Headers com Multipart  
\`\`\`python  
headers \= {  
    "accept": "application/json",  
    "X-API-KEY": "YOUR_UNIPILE_API_KEY"  
}  
\# Content-Type é definido automaticamente pelo requests  
\`\`\`

\---

\#\# 📤 Body Parameters

\#\#\# account\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Comprimento Mínimo\*\*: 1  
\- \*\*Descrição\*\*: Um ID de conta Unipile.

\#\#\# text  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: A mensagem que iniciará a nova conversa.

\#\#\#\# Suporte a Formatação HTML (LinkedIn Recruiter)

Para LinkedIn Recruiter, você pode usar tags HTML para melhorar a apresentação:

\- \`\<strong\>\` \- Texto em negrito  
\- \`\<em\>\` \- Texto em itálico  
\- \`\<a href="www.my-link.com"\>\` \- Links externos  
\- \`\<ul\>\` \- Listas não ordenadas  
\- \`\<ol\>\` \- Listas ordenadas  
\- \`\<li\>\` \- Itens de lista

\*\*Tags podem ser aninhadas conforme necessário\*\*

\*\*Exemplo de Mensagem Formatada\*\*:  
\`\`\`html  
Olá,

\<strong\>Oportunidade especial para você\!\</strong\>

Temos as seguintes posições abertas:  
\<ul\>  
\<li\>\<strong\>Python Developer\</strong\> \- São Paulo\</li\>  
\<li\>\<strong\>Data Scientist\</strong\> \- Rio de Janeiro\</li\>  
\<li\>\<em\>E mais...\</em\>\</li\>  
\</ul\>

Visite nosso site: \<a href="https://nossa-empresa.com"\>nossa-empresa.com\</a\>  
\`\`\`

\---

\#\#\# attachments  
\- \*\*Tipo\*\*: \`array of files\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: Array de arquivos para anexar à mensagem.

\*\*Formatos Suportados\*\*:  
\- Imagens: JPG, PNG, GIF, WEBP  
\- Documentos: PDF, DOC, DOCX  
\- Vídeos: MP4, MOV (dependendo da plataforma)

\---

\#\#\# voice\_message  
\- \*\*Tipo\*\*: \`file\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Plataformas\*\*: WhatsApp, LinkedIn  
\- \*\*Formato Recomendado\*\*: \`.m4a\` para LinkedIn  
\- \*\*Descrição\*\*: Arquivo para enviar como mensagem de voz.

\*\*Notas Importantes\*\*:  
\- Para Instagram e Telegram, use o campo \`attachments\`  
\- LinkedIn prefere formato \`.m4a\`  
\- WhatsApp aceita múltiplos formatos de áudio

\---

\#\#\# video\_message  
\- \*\*Tipo\*\*: \`file\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Plataformas\*\*: LinkedIn  
\- \*\*Descrição\*\*: Arquivo para enviar como mensagem de vídeo.

\*\*Limitações\*\*:  
\- Apenas LinkedIn suporta vídeos diretos  
\- Tamanho recomendado: até 25MB  
\- Formatos: MP4, MOV

\---

\#\#\# attendees\_ids  
\- \*\*Tipo\*\*: \`array of strings\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Comprimento Mínimo\*\*: 1  
\- \*\*Descrição\*\*: Um ou mais IDs de participantes.

\#\#\#\# Identificadores por Plataforma

| Plataforma | Tipo de ID |  
|-----------|-----------|  
| LinkedIn | ID de perfil padrão |  
| WhatsApp | Número de telefone formatado |  
| Instagram | \`provider\_messaging\_id\` |  
| Telegram | ID do usuário |  
| LinkedIn Company | \`messaging/id\` |

\*\*Exemplos\*\*:  
\`\`\`python  
\# LinkedIn pessoal  
attendees\_ids \= \["linkedin\_user\_id\_123"\]

\# Instagram  
attendees\_ids \= \["instagram\_messaging\_id\_456"\]

\# LinkedIn Company Messaging  
attendees\_ids \= \["messaging/id\_789"\]

\# Múltiplos participantes  
attendees\_ids \= \["user1", "user2", "user3"\]  
\`\`\`

\---

\#\#\# subject  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: Campo opcional para definir o assunto da conversa.

\*\*Casos de Uso\*\*:  
\- LinkedIn: Define o título do inMail  
\- WhatsApp: Agrupamentos de conversa  
\- Outras plataformas: Contexto adicional

\---

\#\# 📋 Parâmetros LinkedIn (Extra Fields)

\#\#\# Opções Classic  
\`\`\`python  
linkedin \= {  
    \# Parâmetros específicos para LinkedIn Classic  
}  
\`\`\`

\#\#\# Opções Recruiter  
\`\`\`python  
linkedin \= {  
    "recruiter": {  
        \# Parâmetros específicos para LinkedIn Recruiter  
    }  
}  
\`\`\`

\#\#\# Opções Sales Navigator  
\`\`\`python  
linkedin \= {  
    "sales\_navigator": {  
        \# Parâmetros específicos para Sales Navigator  
    }  
}  
\`\`\`

\---

\#\# 📊 Resposta da API (Response)

\#\#\# Estrutura 201 Created  
\`\`\`json  
{  
  "object": "ChatStarted",  
  "chat\_id": "string",  
  "message\_id": "string"  
}  
\`\`\`

\#\#\# Campos da Resposta

| Campo | Tipo | Descrição |  
|-------|------|-----------|  
| \`object\` | string | Tipo de objeto (ChatStarted) |  
| \`chat\_id\` | string | ID único da conversa iniciada (ID Unipile) |  
| \`message\_id\` | string | ID único da mensagem inicial (ID Unipile) |

\*\*Exemplo de Resposta\*\*:  
\`\`\`json  
{  
  "object": "ChatStarted",  
  "chat\_id": "chat\_550e8400e29b41d4a716446655440000",  
  "message\_id": "msg\_6ba7b81090daf4c1a90c0006e4c56029"  
}  
\`\`\`

\---

\#\# 🚨 Códigos de Erro HTTP

\#\#\# 201 \- Created

\*\*Descrição\*\*: Conversa iniciada e mensagem enviada com sucesso.  
\`\`\`json  
{  
  "object": "ChatStarted",  
  "chat\_id": "chat\_id\_123",  
  "message\_id": "message\_id\_456"  
}  
\`\`\`

\---

\#\#\# 400 \- Bad Request

\*\*Descrição\*\*: Parâmetros inválidos ou conteúdo muito grande.

\*\*Tipos de Erro\*\*:  
\- \`errors/invalid\_parameters\` \- Parâmetros inválidos  
\- \`errors/content\_too\_large\` \- Conteúdo excede limite  
\- \`errors/too\_many\_characters\` \- Muito caracteres na mensagem  
\- \`errors/missing\_parameters\` \- Parâmetros obrigatórios faltando  
\`\`\`json  
{  
  "title": "Bad Request",  
  "detail": "The provided content exceeds the character limit.",  
  "type": "errors/content\_too\_large",  
  "status": 400  
}  
\`\`\`

\*\*Causas Comuns\*\*:  
\- Mensagem muito longa (limite varia por plataforma)  
\- IDs de participantes inválidos  
\- Falta o campo \`account\_id\` ou \`attendees\_ids\`

\---

\#\#\# 401 \- Unauthorized

\*\*Descrição\*\*: Falha de autenticação ou conta desconectada.

\*\*Tipos de Erro\*\*:  
\- \`errors/missing\_credentials\` \- Credenciais não fornecidas  
\- \`errors/invalid\_credentials\` \- Credenciais inválidas  
\- \`errors/expired\_credentials\` \- Token expirado  
\- \`errors/disconnected\_account\` \- Conta desconectada  
\- \`errors/checkpoint\_error\` \- Erro de checkpoint  
\`\`\`json  
{  
  "title": "Unauthorized",  
  "detail": "The account appears to be disconnected from the provider service.",  
  "type": "errors/disconnected\_account",  
  "status": 401  
}  
\`\`\`

\*\*Solução\*\*: Reconectar a conta LinkedIn.

\---

\#\#\# 403 \- Forbidden

\*\*Descrição\*\*: Autenticação válida mas permissões/recurso não disponível.

\*\*Tipos de Erro\*\*:  
\- \`errors/feature\_not\_subscribed\` \- Recurso não contratado  
\- \`errors/subscription\_required\` \- Assinatura necessária  
\- \`errors/insufficient\_permissions\` \- Permissões inadequadas  
\- \`errors/unknown\_authentication\_context\` \- Contexto desconhecido  
\`\`\`json  
{  
  "title": "Forbidden",  
  "detail": "The requested feature has either not been subscribed or not been authenticated properly.",  
  "type": "errors/feature\_not\_subscribed",  
  "status": 403  
}  
\`\`\`

\---

\#\#\# 404 \- Not Found

\*\*Descrição\*\*: Recurso não encontrado.

\*\*Tipos de Erro\*\*:  
\- \`errors/resource\_not\_found\` \- Recurso não existe  
\- \`errors/invalid\_resource\_identifier\` \- ID inválido  
\`\`\`json  
{  
  "title": "Not Found",  
  "detail": "The requested resource were not found.",  
  "type": "errors/resource\_not\_found",  
  "status": 404  
}  
\`\`\`

\---

\#\#\# 415 \- Unsupported Media Type

\*\*Descrição\*\*: Formato de mídia não suportado.

\*\*Tipo de Erro\*\*: \`errors/unsupported\_media\_type\`  
\`\`\`json  
{  
  "title": "Unsupported Media Type",  
  "detail": "The media has been rejected by the provider.",  
  "type": "errors/unsupported\_media\_type",  
  "status": 415  
}  
\`\`\`

\*\*Causas\*\*:  
\- Formato de arquivo não suportado  
\- Tamanho de arquivo muito grande  
\- Arquivo corrompido

\---

\#\#\# 422 \- Unprocessable Entity

\*\*Descrição\*\*: Entidade não pode ser processada.

\*\*Tipos de Erro\*\*:  
\- \`errors/invalid\_recipient\` \- Destinatário inválido  
\- \`errors/no\_connection\_with\_recipient\` \- Sem conexão com o destinatário  
\- \`errors/blocked\_recipient\` \- Destinatário bloqueado  
\- \`errors/user\_unreachable\` \- Usuário inacessível  
\- \`errors/insufficient\_credits\` \- Créditos insuficientes  
\- \`errors/cannot\_invite\_attendee\` \- Não é possível convidar participante  
\- \`errors/not\_allowed\_inmail\` \- InMail não permitido  
\- \`errors/already\_connected\` \- Já conectado  
\- \`errors/limit\_exceeded\` \- Limite excedido  
\`\`\`json  
{  
  "title": "Unprocessable Entity",  
  "detail": "The recipient appears not to be first degree connection.",  
  "type": "errors/no\_connection\_with\_recipient",  
  "status": 422  
}  
\`\`\`

\*\*Causas Comuns\*\*:  
\- Destinatário não é conexão de 1º grau  
\- Destinatário bloqueou mensagens  
\- Limite de inMails diários atingido (Recruiter)  
\- Créditos insuficientes

\---

\#\#\# 429 \- Too Many Requests

\*\*Descrição\*\*: Muitas requisições em curto período.

\*\*Tipo de Erro\*\*: \`errors/too\_many\_requests\`  
\`\`\`json  
{  
  "title": "Too Many Requests",  
  "detail": "The provider cannot accept any more requests at the moment. Please try again later.",  
  "type": "errors/too\_many\_requests",  
  "status": 429  
}  
\`\`\`

\*\*Solução\*\*: Implementar backoff exponencial e rate limiting.

\---

\#\#\# 500 \- Internal Server Error

\*\*Descrição\*\*: Erro interno do servidor.

\*\*Tipos de Erro\*\*:  
\- \`errors/unexpected\_error\` \- Erro inesperado  
\- \`errors/provider\_error\` \- Erro do provedor (LinkedIn)  
\- \`errors/authentication\_intent\_error\` \- Erro de intenção de autenticação  
\`\`\`json  
{  
  "title": "Internal Server Error",  
  "detail": "Something went wrong.",  
  "type": "errors/unexpected\_error",  
  "status": 500  
}  
\`\`\`

\---

\#\#\# 503 \- Service Unavailable

\*\*Descrição\*\*: Serviço indisponível.

\*\*Tipos de Erro\*\*:  
\- \`errors/no\_client\_session\` \- Sem sessão cliente  
\- \`errors/network\_down\` \- Rede inativa  
\- \`errors/service\_unavailable\` \- Serviço indisponível  
\`\`\`json  
{  
  "title": "Service Unavailable",  
  "detail": "Network is down on server side. Please wait a moment and retry.",  
  "type": "errors/network\_down",  
  "status": 503  
}  
\`\`\`

\---

\#\#\# 504 \- Gateway Timeout

\*\*Descrição\*\*: Requisição expirou.

\*\*Tipo de Erro\*\*: \`errors/request\_timeout\`  
\`\`\`json  
{  
  "title": "Gateway Timeout",  
  "detail": "Request Timeout. Please try again, and if the issue persists, contact support.",  
  "type": "errors/request\_timeout",  
  "status": 504  
}  
\`\`\`

\---

\#\# 💻 Exemplos Completos em Python

\#\#\# 1\. Exemplo Básico \- Mensagem Simples  
\`\`\`python  
import requests  
import json

\# Configuração  
api\_key \= "YOUR_UNIPILE_API_KEY"  
account\_id \= "seu\_account\_id"  
base\_url \= "https://api26.unipile.com:15609"

\# Dados da requisição  
payload \= {  
    "account\_id": account\_id,  
    "text": "Olá\! Gostaria de conversar sobre uma oportunidade.",  
    "attendees\_ids": \["linkedin\_user\_id\_123"\],  
    "subject": "Oportunidade de Carreira"  
}

headers \= {  
    "accept": "application/json",  
    "X-API-KEY": api\_key  
}

\# Enviar requisição  
response \= requests.post(  
    f"{base\_url}/api/v1/chats",  
    json=payload,  
    headers=headers  
)

if response.status\_code \== 201:  
    result \= response.json()  
    print(f"✅ Chat iniciado\!")  
    print(f"Chat ID: {result\['chat\_id'\]}")  
    print(f"Message ID: {result\['message\_id'\]}")  
else:  
    print(f"❌ Erro: {response.status\_code}")  
    print(response.json())  
\`\`\`

\#\#\# 2\. Exemplo com HTML Formatado (LinkedIn Recruiter)  
\`\`\`python  
import requests

api\_key \= "sua\_chave\_api"  
account\_id \= "seu\_account\_id"  
base\_url \= "https://api26.unipile.com:15609"

\# Mensagem com HTML formatado  
html\_message \= """  
\<strong\>Olá João,\</strong\>

Vimos seu perfil e temos uma \<strong\>oportunidade perfeita\</strong\> para você\!

\<strong\>Posição:\</strong\> Python Developer Senior  
\<strong\>Localização:\</strong\> São Paulo  
\<strong\>Tipo:\</strong\> Full-time

\<strong\>Requisitos:\</strong\>  
\<ul\>  
\<li\>5+ anos de experiência com Python\</li\>  
\<li\>Experiência com Django/FastAPI\</li\>  
\<li\>Conhecimento em Cloud (AWS/GCP)\</li\>  
\</ul\>

Gostaria de conversar mais? \<em\>Responda este inMail\!\</em\>

Visite nossa página: \<a href="https://nossa-empresa.com/careers"\>nossa-empresa.com/careers\</a\>  
"""

payload \= {  
    "account\_id": account\_id,  
    "text": html\_message,  
    "attendees\_ids": \["linkedin\_user\_id\_456"\],  
    "subject": "Oportunidade Python Developer \- São Paulo",  
    "linkedin": {  
        "recruiter": {}  
    }  
}

headers \= {  
    "accept": "application/json",  
    "X-API-KEY": api\_key  
}

response \= requests.post(  
    f"{base\_url}/api/v1/chats",  
    json=payload,  
    headers=headers  
)

if response.status\_code \== 201:  
    print("✅ InMail enviado com sucesso\!")  
    print(response.json())  
else:  
    print(f"❌ Erro: {response.json()}")  
\`\`\`

\#\#\# 3\. Exemplo com Anexos (Multipart)  
\`\`\`python  
import requests

api\_key \= "sua\_chave\_api"  
account\_id \= "seu\_account\_id"  
base\_url \= "https://api26.unipile.com:15609"

headers \= {  
    "accept": "application/json",  
    "X-API-KEY": api\_key  
}

\# Preparar dados multipart  
data \= {  
    "account\_id": account\_id,  
    "text": "Segue em anexo a proposta de acordo.",  
    "attendees\_ids": "linkedin\_user\_id\_789",  \# String para multipart  
    "subject": "Proposta de Colaboração"  
}

\# Abrir arquivo para anexar  
with open("proposta.pdf", "rb") as f:  
    files \= {  
        "attachments": ("proposta.pdf", f, "application/pdf")  
    }  
      
    response \= requests.post(  
        f"{base\_url}/api/v1/chats",  
        data=data,  
        files=files,  
        headers=headers  
    )

if response.status\_code \== 201:  
    print("✅ Mensagem com anexo enviada\!")  
    print(response.json())  
else:  
    print(f"❌ Erro: {response.json()}")  
\`\`\`

\#\#\# 4\. Cliente Completo para Automação  
\`\`\`python  
import requests  
import time  
import random  
from typing import Dict, List, Optional  
import json

class LinkedInChatClient:  
    """  
    Cliente para iniciar chats e enviar mensagens no LinkedIn.  
    Implementa rate limiting e tratamento de erros.  
    """  
      
    def \_\_init\_\_(self, base\_url: str, account\_id: str, api\_key: str):  
        """  
        Inicializa o cliente.  
          
        Args:  
            base\_url: URL base da API  
            account\_id: ID da conta  
            api\_key: Chave de API  
        """  
        self.base\_url \= base\_url  
        self.account\_id \= account\_id  
        self.api\_key \= api\_key  
        self.endpoint \= f"{base\_url}/api/v1/chats"  
          
        self.headers \= {  
            "accept": "application/json",  
            "X-API-KEY": api\_key  
        }  
      
    def start\_chat(  
        self,  
        attendees\_ids: List\[str\],  
        text: str,  
        subject: Optional\[str\] \= None,  
        use\_recruiter: bool \= False,  
        attachments: Optional\[List\[str\]\] \= None,  
        voice\_message: Optional\[str\] \= None  
    ) \-\> Dict:  
        """  
        Inicia um novo chat.  
          
        Args:  
            attendees\_ids: Lista de IDs de participantes  
            text: Mensagem a enviar  
            subject: Assunto (opcional)  
            use\_recruiter: Se usar LinkedIn Recruiter  
            attachments: Lista de caminhos de arquivos  
            voice\_message: Caminho para arquivo de voz  
          
        Returns:  
            Resposta da API  
          
        Raises:  
            requests.exceptions.HTTPError: Para erros HTTP  
        """  
          
        payload \= {  
            "account\_id": self.account\_id,  
            "text": text,  
            "attendees\_ids": attendees\_ids  
        }  
          
        if subject:  
            payload\["subject"\] \= subject  
          
        if use\_recruiter:  
            payload\["linkedin"\] \= {"recruiter": {}}  
          
        try:  
            \# Sem attachments \- usar JSON  
            if not attachments and not voice\_message:  
                response \= requests.post(  
                    self.endpoint,  
                    json=payload,  
                    headers=self.headers,  
                    timeout=30  
                )  
            else:  
                \# Com attachments \- usar multipart  
                data \= payload.copy()  
                data\["attendees\_ids"\] \= attendees\_ids\[0\] if attendees\_ids else ""  
                  
                files \= {}  
                  
                if attachments:  
                    for idx, file\_path in enumerate(attachments):  
                        files\[f"attachments"\] \= open(file\_path, 'rb')  
                  
                if voice\_message:  
                    files\["voice\_message"\] \= open(voice\_message, 'rb')  
                  
                response \= requests.post(  
                    self.endpoint,  
                    data=data,  
                    files=files,  
                    headers=self.headers,  
                    timeout=30  
                )  
              
            response.raise\_for\_status()  
            return response.json()  
          
        except requests.exceptions.HTTPError as e:  
            error\_status \= e.response.status\_code  
            error\_data \= e.response.json()  
            error\_type \= error\_data.get('type', 'unknown')  
              
            if error\_status \== 422:  
                if 'no\_connection' in error\_type:  
                    print("⚠️  Usuário não é conexão de 1º grau")  
                elif 'blocked' in error\_type:  
                    print("⚠️  Usuário bloqueou mensagens")  
                elif 'insufficient\_credits' in error\_type:  
                    print("⚠️  Créditos insuficientes (Recruiter)")  
            elif error\_status \== 429:  
                print("⏳ Rate limit atingido. Aguardando...")  
                time.sleep(random.uniform(30, 60))  
                return self.start\_chat(  
                    attendees\_ids, text, subject,   
                    use\_recruiter, attachments, voice\_message  
                )  
              
            raise  
      
    def send\_bulk\_messages(  
        self,  
        recipients: List\[Dict\],  
        message\_template: str,  
        delay\_min: float \= 2,  
        delay\_max: float \= 5,  
        use\_recruiter: bool \= False  
    ) \-\> Dict:  
        """  
        Envia mensagens em massa com template.  
          
        Args:  
            recipients: Lista de dicts com 'id' e 'name'  
            message\_template: Template da mensagem com {name}  
            delay\_min: Delay mínimo entre mensagens  
            delay\_max: Delay máximo  
            use\_recruiter: Usar Recruiter  
          
        Returns:  
            Estatísticas de envio  
        """  
          
        stats \= {  
            "enviadas": 0,  
            "falhadas": 0,  
            "bloqueadas": 0,  
            "total": len(recipients)  
        }  
          
        for idx, recipient in enumerate(recipients, 1):  
            try:  
                \# Personizar mensagem  
                personalized\_msg \= message\_template.format(  
                    name=recipient.get('name', 'User')  
                )  
                  
                print(f"\[{idx}/{len(recipients)}\] Enviando para {recipient\['name'\]}...")  
                  
                result \= self.start\_chat(  
                    attendees\_ids=\[recipient\['id'\]\],  
                    text=personalized\_msg,  
                    use\_recruiter=use\_recruiter  
                )  
                  
                stats\['enviadas'\] \+= 1  
                print(f"✅ Enviado\! Chat ID: {result\['chat\_id'\]}")  
                  
                \# Delay aleatório  
                delay \= random.uniform(delay\_min, delay\_max)  
                time.sleep(delay)  
              
            except requests.exceptions.HTTPError as e:  
                error\_type \= e.response.json().get('type', '')  
                  
                if 'blocked' in error\_type or 'no\_connection' in error\_type:  
                    stats\['bloqueadas'\] \+= 1  
                    print(f"⚠️  Não foi possível contatar")  
                else:  
                    stats\['falhadas'\] \+= 1  
                    print(f"❌ Erro: {error\_type}")  
          
        print(f"\\\\n📊 Resumo:")  
        print(f"  ✅ Enviadas: {stats\['enviadas'\]}")  
        print(f"  ⚠️  Bloqueadas: {stats\['bloqueadas'\]}")  
        print(f"  ❌ Falhadas: {stats\['falhadas'\]}")  
        print(f"  📋 Total: {stats\['total'\]}")  
          
        return stats  
      
    def send\_recruiter\_inmail(  
        self,  
        candidate\_id: str,  
        candidate\_name: str,  
        position: str,  
        salary\_range: str,  
        company: str  
    ) \-\> Dict:  
        """  
        Envia InMail formatado para candidato.  
          
        Args:  
            candidate\_id: ID do candidato  
            candidate\_name: Nome do candidato  
            position: Posição oferecida  
            salary\_range: Range salarial  
            company: Nome da empresa  
          
        Returns:  
            Resposta da API  
        """  
          
        inmail\_body \= f"""  
\<strong\>Olá {candidate\_name},\</strong\>

Detectamos seu perfil e ficamos \<strong\>muito interessados\</strong\> em sua experiência\!

\<strong\>Detalhes da Posição:\</strong\>

\<ul\>  
\<li\>\<strong\>Cargo:\</strong\> {position}\</li\>  
\<li\>\<strong\>Empresa:\</strong\> {company}\</li\>  
\<li\>\<strong\>Salário:\</strong\> {salary\_range}\</li\>  
\<li\>\<strong\>Tipo:\</strong\> Full-time | Presencial\</li\>  
\</ul\>

Adoraríamos conversar com você sobre essa oportunidade\!

\<strong\>Próximos passos:\</strong\>  
\<ol\>  
\<li\>Responda este InMail\</li\>  
\<li\>Agende uma entrevista\</li\>  
\<li\>Conheça nosso time\!\</li\>  
\</ol\>

Esperamos sua resposta\! 🚀  
"""  
          
        return self.start\_chat(  
            attendees\_ids=\[candidate\_id\],  
            text=inmail\_body,  
            subject=f"Oportunidade: {position} em {company}",  
            use\_recruiter=True  
        )

\# Exemplo de Uso  
if \_\_name\_\_ \== "\_\_main\_\_":  
      
    client \= LinkedInChatClient(  
        base\_url="https://api26.unipile.com:15609",  
        account\_id="seu\_account\_id",  
        api\_key="sua\_chave\_api"  
    )  
      
    \# Caso 1: Mensagem Simples  
    print("=== Caso 1: Mensagem Simples \===")  
    try:  
        result \= client.start\_chat(  
            attendees\_ids=\["linkedin\_user\_id"\],  
            text="Olá\! Gostaria de conversar sobre uma oportunidade.",  
            subject="Oportunidade de Trabalho"  
        )  
        print(f"Chat iniciado: {result\['chat\_id'\]}")  
    except Exception as e:  
        print(f"Erro: {e}")  
      
    \# Caso 2: InMail via Recruiter  
    print("\\\\n=== Caso 2: InMail Recruiter \===")  
    try:  
        result \= client.send\_recruiter\_inmail(  
            candidate\_id="candidate\_123",  
            candidate\_name="João",  
            position="Python Developer",  
            salary\_range="R$ 8.000 \- R$ 12.000",  
            company="Tech Corp"  
        )  
        print(f"✅ InMail enviado\!")  
    except Exception as e:  
        print(f"Erro: {e}")  
      
    \# Caso 3: Envio em Massa  
    print("\\\\n=== Caso 3: Envio em Massa \===")  
    recipients \= \[  
        {"id": "user\_1", "name": "João Silva"},  
        {"id": "user\_2", "name": "Maria Santos"},  
        {"id": "user\_3", "name": "Pedro Costa"}  
    \]  
      
    template \= """  
Olá {name},

Vimos seu perfil e temos uma oportunidade interessante\!

Podemos conversar?  
"""  
      
    try:  
        stats \= client.send\_bulk\_messages(  
            recipients=recipients,  
            message\_template=template,  
            delay\_min=3,  
            delay\_max=7,  
            use\_recruiter=False  
        )  
    except Exception as e:  
        print(f"Erro: {e}")  
\`\`\`

\---

\#\# 🎯 Casos de Uso Práticos

\#\#\# 1\. Automação de Recrutamento  
\`\`\`python  
\# Listar candidatos do banco de dados  
candidates \= \[  
    {"id": "cand\_1", "name": "Ana Silva", "position": "Data Scientist"},  
    {"id": "cand\_2", "name": "Carlos Santos", "position": "ML Engineer"}  
\]

client \= LinkedInChatClient(...)

for candidate in candidates:  
    client.send\_recruiter\_inmail(  
        candidate\_id=candidate\['id'\],  
        candidate\_name=candidate\['name'\],  
        position=candidate\['position'\],  
        salary\_range="R$ 10.000 \- R$ 15.000",  
        company="Tech Corp"  
    )  
    time.sleep(random.uniform(5, 10))  
\`\`\`

\#\#\# 2\. Prospecção de Vendas  
\`\`\`python  
\# Template de prospecção  
prospect\_template \= """  
Olá {name},

Identificamos que sua empresa {company} pode se beneficiar de nossa solução.

Temos ajudado empresas similares a:  
\- ✅ Reduzir custos em 30%  
\- ✅ Aumentar produtividade em 50%  
\- ✅ Melhorar ROI significativamente

Gostaria de agendar uma demo?  
"""

prospects \= load\_prospects("prospects.csv")

stats \= client.send\_bulk\_messages(  
    recipients=prospects,  
    message\_template=prospect\_template,  
    delay\_min=5,  
    delay\_max=15  
)  
\`\`\`

\#\#\# 3\. Seguimento de Leads  
\`\`\`python  
\# Primeira mensagem  
first\_contact \= "Olá\! Vi seu perfil e achei muito interessante. Podemos conversar?"

result \= client.start\_chat(  
    attendees\_ids=\["lead\_id"\],  
    text=first\_contact  
)

\# Aguardar resposta em outro momento  
time.sleep(86400)  \# 24 horas

\# Mensagem de seguimento  
follow\_up \= """  
Olá novamente\!

Apenas verificando se você recebeu minha mensagem anterior.

Tenho uma proposta que pode ser valiosa para você.  
"""

\# Seria feito via send\_message (outro endpoint)  
\`\`\`

\#\#\# 4\. Integração com LinkedIn Search  
\`\`\`python  
\# Buscar pessoas  
search\_client \= LinkedInSearchClient(...)  
results \= search\_client.search\_people\_classic(  
    keywords="Python Developer",  
    location="São Paulo",  
    limit=50  
)

\# Iniciar chats automaticamente  
chat\_client \= LinkedInChatClient(...)

for person in results\['items'\]:  
    try:  
        chat\_client.start\_chat(  
            attendees\_ids=\[person\['public\_identifier'\]\],  
            text="Olá\! Vi seu perfil e tenho uma oportunidade para você.",  
            subject="Oportunidade de Carreira"  
        )  
        time.sleep(random.uniform(5, 10))  
    except Exception as e:  
        print(f"Erro ao contatar {person\['name'\]}: {e}")  
\`\`\`

\---

\#\# ⚙️ Boas Práticas

\#\#\# 1\. Rate Limiting e Throttling  
\`\`\`python  
from datetime import datetime, timedelta

class ThrottledChatClient(LinkedInChatClient):  
    def \_\_init\_\_(self, \*args, max\_requests\_per\_hour=100, \*\*kwargs):  
        super().\_\_init\_\_(\*args, \*\*kwargs)  
        self.max\_requests \= max\_requests\_per\_hour  
        self.requests \= \[\]  
      
    def \_check\_rate\_limit(self):  
        """Verifica se podemos fazer requisição."""  
        now \= datetime.now()  
        \# Remover requisições de 1 hora atrás  
        self.requests \= \[  
            r for r in self.requests   
            if (now \- r).total\_seconds() \< 3600  
        \]  
          
        if len(self.requests) \>= self.max\_requests:  
            wait\_time \= (self.requests\[0\] \+ timedelta(hours=1) \- now).total\_seconds()  
            print(f"⏳ Rate limit. Aguardando {wait\_time:.0f}s...")  
            time.sleep(max(1, wait\_time))  
          
        self.requests.append(now)  
\`\`\`

\#\#\# 2\. Mensagens Personalizadas com Template  
\`\`\`python  
from string import Template

class TemplatedChatClient(LinkedInChatClient):  
    def \_\_init\_\_(self, \*args, \*\*kwargs):  
        super().\_\_init\_\_(\*args, \*\*kwargs)  
        self.templates \= {}  
      
    def add\_template(self, name: str, template\_str: str):  
        """Adiciona um template de mensagem."""  
        self.templates\[name\] \= Template(template\_str)  
      
    def send\_from\_template(self, template\_name: str, attendees\_ids: List\[str\], \*\*kwargs):  
        """Envia mensagem usando template."""  
        if template\_name not in self.templates:  
            raise ValueError(f"Template '{template\_name}' não existe")  
          
        template \= self.templates\[template\_name\]  
        message \= template.substitute(\*\*kwargs)  
          
        return self.start\_chat(  
            attendees\_ids=attendees\_ids,  
            text=message,  
            \*\*{k: v for k, v in kwargs.items() if k not in template.template}  
        )

\# Uso  
client \= TemplatedChatClient(...)  
client.add\_template("recruiter", """  
Olá $name,

Temos a posição de $position disponível\!  
Salário: $salary

Interessado?  
""")

client.send\_from\_template(  
    "recruiter",  
    attendees\_ids=\["user\_id"\],  
    name="João",  
    position="Python Developer",  
    salary="R$ 10k"  
)  
\`\`\`

\#\#\# 3\. Logging e Monitoramento  
\`\`\`python  
import logging

logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s \- %(levelname)s \- %(message)s'  
)  
logger \= logging.getLogger(\_\_name\_\_)

class MonitoredChatClient(LinkedInChatClient):  
    def start\_chat(self, \*args, \*\*kwargs):  
        logger.info(f"Iniciando chat para: {kwargs.get('attendees\_ids')}")  
        try:  
            result \= super().start\_chat(\*args, \*\*kwargs)  
            logger.info(f"Chat iniciado: {result\['chat\_id'\]}")  
            return result  
        except Exception as e:  
            logger.error(f"Erro ao iniciar chat: {e}")  
            raise  
\`\`\`

\---

\#\# 📊 Limites e Quotas

| Limite | Valor | Plataforma |  
|--------|-------|-----------|  
| Caracteres por mensagem | 4.000 | LinkedIn |  
| Tamanho de anexo | 25 MB | Todas |  
| InMails por dia | Limitado | Recruiter |  
| Requisições por hora | Dinâmico | LinkedIn |  
| Participantes por chat | Ilimitado | Todas |

\---

\#\# 📝 Versão da Documentação

\- \*\*Versão\*\*: 1.0  
\- \*\*Data\*\*: Dezembro 2024  
\- \*\*Status\*\*: Documentação Completa e Validada  
\- \*\*Compatibilidade\*\*: Python 3.7+

\---

\*\*Desenvolvido para Vibecoding \- Documentação Profissional para Desenvolvimento Orientado por IA\*\*  
