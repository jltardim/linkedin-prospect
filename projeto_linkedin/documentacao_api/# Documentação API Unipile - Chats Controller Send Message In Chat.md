\# Documentação API Unipile \- Chats Controller Send Message In Chat

\#\# 📋 Visão Geral

O endpoint \*\*Send a message in a chat\*\* permite enviar mensagens em conversas existentes no LinkedIn, WhatsApp, Instagram, Telegram e Twitter. Este é um endpoint crítico para comunicação contínua, chatbots, atendimento ao cliente e automação de conversas.

\*\*Capacidades Principais\*\*:  
\- Enviar mensagens em chats existentes  
\- Suporte a anexos (imagens, documentos, vídeos)  
\- Mensagens de voz (WhatsApp, LinkedIn)  
\- Mensagens de vídeo (LinkedIn)  
\- Citação/resposta de mensagens específicas  
\- Suporte a threads (Slack)  
\- Simulação de digitação (WhatsApp)  
\- Validação de segurança com account\_id

Esta documentação aborda a integração completa para desenvolvimento de aplicações Python que implementam chatbots, respostas automáticas e automação de comunicação.

\---

\#\# 🔧 Informações Técnicas Básicas

\#\#\# Endpoint  
\`\`\`  
POST https://{subdomain}.unipile.com:{port}/api/v1/chats/{chat\_id}/messages  
\`\`\`

\#\#\# Método HTTP  
\`\`\`  
POST  
\`\`\`

\#\#\# Base URL Padrão  
\`\`\`  
https://api26.unipile.com:15609/api/v1/chats/{chat\_id}/messages  
\`\`\`

\#\#\# Content-Type  
\`\`\`  
multipart/form-data (quando há anexos)  
application/json (sem anexos)  
\`\`\`

\#\#\# Descrição  
Envia uma mensagem para um chat específico com a possibilidade de anexar arquivos.

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
\# Content-Type é definido automaticamente  
\`\`\`

\---

\#\# 📍 Path Parameters

\#\#\# chat\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Descrição\*\*: O ID do chat onde enviar a mensagem.

\*\*Formato\*\*: ID único retornado ao iniciar um chat ou ao recuperar chats

\*\*Exemplo\*\*:  
\`\`\`  
POST /api/v1/chats/chat\_550e8400e29b41d4a716446655440000/messages  
\`\`\`

\---

\#\# 📤 Body Parameters

\#\#\# text  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Depende  
\- \*\*Descrição\*\*: O conteúdo da mensagem a enviar.

\*\*Obrigatoriedade\*\*:  
\- Obrigatório se nenhum outro tipo de mídia for enviado (voice\_message, video\_message, attachment)  
\- Opcional se houver anexos

\*\*Limites\*\*:  
\- LinkedIn: até 4.000 caracteres  
\- WhatsApp: até 1.024 caracteres  
\- Instagram: até 1.000 caracteres

\*\*Exemplo\*\*:  
\`\`\`python  
"text": "Obrigado pela sua mensagem\! Como posso ajudar?"  
\`\`\`

\---

\#\#\# account\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: Um account\_id pode ser especificado para evitar que o usuário envie mensagens em chats que não pertencem à conta.

\*\*Uso de Segurança\*\*:  
\- Previne que aplicações mal-intencionadas acessem chats de outras contas  
\- Recomendado sempre incluir

\*\*Exemplo\*\*:  
\`\`\`python  
"account\_id": "account\_123456"  
\`\`\`

\---

\#\#\# thread\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Plataformas\*\*: Slack (apenas)  
\- \*\*Descrição\*\*: O ID da thread para enviar a mensagem.

\*\*Notas\*\*:  
\- Específico para Slack  
\- Deixe vazio para enviar na conversa principal  
\- Obtenha o thread\_id ao recuperar mensagens de thread

\*\*Exemplo\*\*:  
\`\`\`python  
"thread\_id": "1234567890.123456"  
\`\`\`

\---

\#\#\# quote\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: O ID de uma mensagem para citar/responder.

\*\*Comportamento\*\*:  
\- Cria uma resposta/citação da mensagem especificada  
\- A mensagem original é exibida no contexto  
\- Funciona em todas as plataformas

\*\*Exemplo\*\*:  
\`\`\`python  
"quote\_id": "msg\_6ba7b81090daf4c1a90c0006e4c56029"  
\`\`\`

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

\*\*Exemplo\*\*:  
\`\`\`python  
files \= {  
    "voice\_message": open("nota\_de\_voz.m4a", "rb")  
}  
\`\`\`

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

\*\*Exemplo\*\*:  
\`\`\`python  
files \= {  
    "video\_message": open("apresentacao.mp4", "rb")  
}  
\`\`\`

\---

\#\#\# attachments  
\- \*\*Tipo\*\*: \`array of files\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: Array de arquivos para anexar à mensagem.

\*\*Formatos Suportados\*\*:  
\- Imagens: JPG, PNG, GIF, WEBP  
\- Documentos: PDF, DOC, DOCX, XLS, XLSX  
\- Vídeos: MP4, MOV (dependendo da plataforma)  
\- Áudio: MP3, WAV, M4A (Instagram, Telegram)

\*\*Exemplo\*\*:  
\`\`\`python  
files \= {  
    "attachments": \[  
        open("documento.pdf", "rb"),  
        open("imagem.jpg", "rb")  
    \]  
}  
\`\`\`

\---

\#\#\# typing\_duration  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Plataformas\*\*: WhatsApp (apenas)  
\- \*\*Descrição\*\*: Defina uma duração em milissegundos para simular um status de digitação.

\*\*Comportamento\*\*:  
\- Simula que o usuário está digitando  
\- Aguarda a duração especificada antes de enviar a mensagem  
\- Melhora experiência do usuário

\*\*Exemplo\*\*:  
\`\`\`python  
"typing\_duration": "3000"  \# 3 segundos de digitação simulada  
\`\`\`

\---

\#\# 📊 Resposta da API (Response)

\#\#\# Estrutura 201 Created  
\`\`\`json  
{  
  "object": "MessageSent",  
  "message\_id": "string"  
}  
\`\`\`

\#\#\# Campos da Resposta

| Campo | Tipo | Descrição |  
|-------|------|-----------|  
| \`object\` | string | Tipo de objeto (MessageSent) |  
| \`message\_id\` | string | ID único da mensagem enviada (ID Unipile) |

\*\*Exemplo de Resposta\*\*:  
\`\`\`json  
{  
  "object": "MessageSent",  
  "message\_id": "msg\_6ba7b81090daf4c1a90c0006e4c56029"  
}  
\`\`\`

\---

\#\# 🚨 Códigos de Erro HTTP

\#\#\# 201 \- Created

\*\*Descrição\*\*: Mensagem enviada com sucesso.  
\`\`\`json  
{  
  "object": "MessageSent",  
  "message\_id": "msg\_id\_123"  
}  
\`\`\`

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

\*\*Solução\*\*: Reconectar a conta.

\---

\#\#\# 403 \- Forbidden

\*\*Descrição\*\*: Autenticação válida mas permissões/recurso não disponível.

\*\*Tipos de Erro\*\*:  
\- \`errors/feature\_not\_subscribed\` \- Recurso não contratado  
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

\*\*Descrição\*\*: Chat, thread ou recurso não encontrado.

\*\*Tipos de Erro\*\*:  
\- \`errors/resource\_not\_found\` \- Recurso não existe  
\- \`errors/invalid\_resource\_identifier\` \- ID inválido  
\`\`\`json  
{  
  "title": "Not Found",  
  "detail": "Account, chat or thread not found",  
  "type": "errors/resource\_not\_found",  
  "status": 404  
}  
\`\`\`

\*\*Causas\*\*:  
\- Chat ID inválido ou inexistente  
\- Thread ID inválido (Slack)  
\- Chat foi deletado

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

\*\*Descrição\*\*: Mensagem não passou na validação.

\*\*Tipos de Erro\*\*:  
\- \`errors/invalid\_message\` \- Mensagem inválida  
\- \`errors/unprocessable\_entity\` \- Entidade não processável  
\- \`errors/invalid\_thread\` \- Thread inválida  
\- \`errors/cant\_send\_message\` \- Não pode enviar mensagem  
\- \`errors/limit\_exceeded\` \- Limite excedido  
\`\`\`json  
{  
  "title": "Unprocessable Entity",  
  "detail": "Provider cannot execute request because of an invalid message.",  
  "type": "errors/invalid\_message",  
  "status": 422  
}  
\`\`\`

\*\*Causas Comuns\*\*:  
\- Mensagem vazia (sem text e sem mídia)  
\- Quote ID inválido  
\- Chat ou thread não encontrado  
\- Limite de caracteres excedido

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

\*\*Solução\*\*: Implementar backoff exponencial.

\---

\#\#\# 500 \- Internal Server Error

\*\*Descrição\*\*: Erro interno do servidor.

\*\*Tipos de Erro\*\*:  
\- \`errors/unexpected\_error\` \- Erro inesperado  
\- \`errors/provider\_error\` \- Erro do provedor  
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
api\_key \= "sua\_chave\_api"  
account\_id \= "seu\_account\_id"  
base\_url \= "https://api26.unipile.com:15609"  
chat\_id \= "chat\_550e8400e29b41d4a716446655440000"

\# Dados da requisição  
payload \= {  
    "account\_id": account\_id,  
    "text": "Obrigado pela sua mensagem\! Como posso ajudar?"  
}

headers \= {  
    "accept": "application/json",  
    "X-API-KEY": api\_key  
}

\# Enviar requisição  
response \= requests.post(  
    f"{base\_url}/api/v1/chats/{chat\_id}/messages",  
    json=payload,  
    headers=headers  
)

if response.status\_code \== 201:  
    result \= response.json()  
    print(f"✅ Mensagem enviada\!")  
    print(f"Message ID: {result\['message\_id'\]}")  
else:  
    print(f"❌ Erro: {response.status\_code}")  
    print(response.json())  
\`\`\`

\#\#\# 2\. Exemplo com Citação/Resposta  
\`\`\`python  
import requests

api\_key \= "sua\_chave\_api"  
account\_id \= "seu\_account\_id"  
base\_url \= "https://api26.unipile.com:15609"  
chat\_id \= "chat\_id\_123"

\# Responder a uma mensagem específica  
payload \= {  
    "account\_id": account\_id,  
    "text": "Ótimo\! Vamos agendar uma reunião?",  
    "quote\_id": "msg\_6ba7b81090daf4c1a90c0006e4c56029"  \# ID da mensagem a responder  
}

headers \= {  
    "accept": "application/json",  
    "X-API-KEY": api\_key  
}

response \= requests.post(  
    f"{base\_url}/api/v1/chats/{chat\_id}/messages",  
    json=payload,  
    headers=headers  
)

if response.status\_code \== 201:  
    print("✅ Resposta enviada\!")  
    print(response.json())  
else:  
    print(f"❌ Erro: {response.json()}")  
\`\`\`

\#\#\# 3\. Exemplo com Anexos  
\`\`\`python  
import requests

api\_key \= "sua\_chave\_api"  
account\_id \= "seu\_account\_id"  
base\_url \= "https://api26.unipile.com:15609"  
chat\_id \= "chat\_id\_456"

headers \= {  
    "accept": "application/json",  
    "X-API-KEY": api\_key  
}

data \= {  
    "account\_id": account\_id,  
    "text": "Segue em anexo o documento solicitado."  
}

\# Preparar múltiplos anexos  
with open("documento.pdf", "rb") as pdf\_file:  
    with open("imagem.jpg", "rb") as img\_file:  
        files \= {  
            "attachments": \[  
                ("documento.pdf", pdf\_file, "application/pdf"),  
                ("imagem.jpg", img\_file, "image/jpeg")  
            \]  
        }  
          
        response \= requests.post(  
            f"{base\_url}/api/v1/chats/{chat\_id}/messages",  
            data=data,  
            files=files,  
            headers=headers  
        )

if response.status\_code \== 201:  
    print("✅ Mensagem com anexos enviada\!")  
    print(response.json())  
else:  
    print(f"❌ Erro: {response.json()}")  
\`\`\`

\#\#\# 4\. Cliente Completo para Chatbot  
\`\`\`python  
import requests  
import time  
import random  
from typing import Dict, Optional, List  
from enum import Enum

class MessageType(Enum):  
    """Tipos de mensagens suportados."""  
    TEXT \= "text"  
    VOICE \= "voice"  
    VIDEO \= "video"  
    ATTACHMENT \= "attachment"

class LinkedInMessageClient:  
    """  
    Cliente para enviar mensagens em chats do LinkedIn.  
    Implementa padrões de chatbot e automação.  
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
          
        self.headers \= {  
            "accept": "application/json",  
            "X-API-KEY": api\_key  
        }  
      
    def send\_message(  
        self,  
        chat\_id: str,  
        text: Optional\[str\] \= None,  
        quote\_id: Optional\[str\] \= None,  
        attachments: Optional\[List\[str\]\] \= None,  
        voice\_message: Optional\[str\] \= None,  
        typing\_duration: Optional\[int\] \= None,  
        thread\_id: Optional\[str\] \= None  
    ) \-\> Dict:  
        """  
        Envia uma mensagem em um chat.  
          
        Args:  
            chat\_id: ID do chat  
            text: Conteúdo da mensagem  
            quote\_id: ID da mensagem para responder  
            attachments: Lista de caminhos de arquivos  
            voice\_message: Caminho para arquivo de voz  
            typing\_duration: Duração da digitação simulada (ms)  
            thread\_id: ID da thread (Slack)  
          
        Returns:  
            Resposta da API  
          
        Raises:  
            requests.exceptions.HTTPError: Para erros HTTP  
        """  
          
        payload \= {  
            "account\_id": self.account\_id  
        }  
          
        if text:  
            payload\["text"\] \= text  
          
        if quote\_id:  
            payload\["quote\_id"\] \= quote\_id  
          
        if thread\_id:  
            payload\["thread\_id"\] \= thread\_id  
          
        if typing\_duration:  
            payload\["typing\_duration"\] \= str(typing\_duration)  
          
        try:  
            \# Sem mídia \- usar JSON  
            if not attachments and not voice\_message:  
                response \= requests.post(  
                    f"{self.base\_url}/api/v1/chats/{chat\_id}/messages",  
                    json=payload,  
                    headers=self.headers,  
                    timeout=30  
                )  
            else:  
                \# Com mídia \- usar multipart  
                files \= {}  
                  
                if attachments:  
                    file\_list \= \[\]  
                    for file\_path in attachments:  
                        file\_list.append(open(file\_path, 'rb'))  
                    files\["attachments"\] \= file\_list  
                  
                if voice\_message:  
                    files\["voice\_message"\] \= open(voice\_message, 'rb')  
                  
                response \= requests.post(  
                    f"{self.base\_url}/api/v1/chats/{chat\_id}/messages",  
                    data=payload,  
                    files=files,  
                    headers=self.headers,  
                    timeout=30  
                )  
              
            response.raise\_for\_status()  
            return response.json()  
          
        except requests.exceptions.HTTPError as e:  
            error\_status \= e.response.status\_code  
            error\_data \= e.response.json()  
            error\_type \= error\_data.get('type', '')  
              
            if error\_status \== 429:  
                print("⏳ Rate limit. Aguardando...")  
                time.sleep(random.uniform(5, 15))  
                return self.send\_message(  
                    chat\_id, text, quote\_id, attachments,  
                    voice\_message, typing\_duration, thread\_id  
                )  
            elif error\_status \== 404:  
                print(f"❌ Chat não encontrado: {chat\_id}")  
            elif error\_status \== 422:  
                print(f"⚠️  Mensagem inválida: {error\_type}")  
              
            raise  
      
    def send\_with\_typing(  
        self,  
        chat\_id: str,  
        text: str,  
        typing\_duration\_ms: int \= 2000  
    ) \-\> Dict:  
        """  
        Envia mensagem com simulação de digitação (WhatsApp).  
          
        Args:  
            chat\_id: ID do chat  
            text: Conteúdo da mensagem  
            typing\_duration\_ms: Duração da digitação em ms  
          
        Returns:  
            Resposta da API  
        """  
          
        return self.send\_message(  
            chat\_id=chat\_id,  
            text=text,  
            typing\_duration=typing\_duration\_ms  
        )  
      
    def send\_reply(  
        self,  
        chat\_id: str,  
        text: str,  
        reply\_to\_message\_id: str  
    ) \-\> Dict:  
        """  
        Envia uma resposta a uma mensagem específica.  
          
        Args:  
            chat\_id: ID do chat  
            text: Conteúdo da resposta  
            reply\_to\_message\_id: ID da mensagem a responder  
          
        Returns:  
            Resposta da API  
        """  
          
        return self.send\_message(  
            chat\_id=chat\_id,  
            text=text,  
            quote\_id=reply\_to\_message\_id  
        )  
      
    def send\_bulk\_messages(  
        self,  
        messages: List\[Dict\],  
        delay\_min: float \= 2,  
        delay\_max: float \= 5  
    ) \-\> Dict:  
        """  
        Envia múltiplas mensagens sequencialmente.  
          
        Args:  
            messages: Lista de dicts com 'chat\_id' e 'text'  
            delay\_min: Delay mínimo entre mensagens  
            delay\_max: Delay máximo  
          
        Returns:  
            Estatísticas de envio  
        """  
          
        stats \= {  
            "enviadas": 0,  
            "falhadas": 0,  
            "total": len(messages)  
        }  
          
        for idx, msg in enumerate(messages, 1):  
            try:  
                print(f"\[{idx}/{len(messages)}\] Enviando mensagem...")  
                  
                self.send\_message(  
                    chat\_id=msg\['chat\_id'\],  
                    text=msg\['text'\]  
                )  
                  
                stats\['enviadas'\] \+= 1  
                  
                \# Delay  
                delay \= random.uniform(delay\_min, delay\_max)  
                time.sleep(delay)  
              
            except Exception as e:  
                stats\['falhadas'\] \+= 1  
                print(f"❌ Erro: {e}")  
          
        print(f"\\\\n📊 Resumo:")  
        print(f"  ✅ Enviadas: {stats\['enviadas'\]}")  
        print(f"  ❌ Falhadas: {stats\['falhadas'\]}")  
        print(f"  📋 Total: {stats\['total'\]}")  
          
        return stats

class ChatBot:  
    """  
    Implementação simples de um ChatBot automático.  
    """  
      
    def \_\_init\_\_(self, client: LinkedInMessageClient):  
        """  
        Inicializa o chatbot.  
          
        Args:  
            client: Cliente de mensagens  
        """  
        self.client \= client  
        self.responses \= {}  
      
    def add\_response(self, keyword: str, response: str):  
        """  
        Adiciona uma resposta automática para um keyword.  
          
        Args:  
            keyword: Palavra-chave para ativar a resposta  
            response: Texto da resposta  
        """  
        self.responses\[keyword.lower()\] \= response  
      
    def process\_message(self, chat\_id: str, message: str, message\_id: str) \-\> bool:  
        """  
        Processa uma mensagem recebida e responde se houver keyword match.  
          
        Args:  
            chat\_id: ID do chat  
            message: Conteúdo da mensagem  
            message\_id: ID da mensagem  
          
        Returns:  
            True se respondeu, False caso contrário  
        """  
          
        message\_lower \= message.lower()  
          
        for keyword, response in self.responses.items():  
            if keyword in message\_lower:  
                try:  
                    self.client.send\_reply(  
                        chat\_id=chat\_id,  
                        text=response,  
                        reply\_to\_message\_id=message\_id  
                    )  
                    return True  
                except Exception as e:  
                    print(f"Erro ao responder: {e}")  
                    return False  
          
        return False

\# Exemplo de Uso  
if \_\_name\_\_ \== "\_\_main\_\_":  
      
    client \= LinkedInMessageClient(  
        base\_url="https://api26.unipile.com:15609",  
        account\_id="seu\_account\_id",  
        api\_key="sua\_chave\_api"  
    )  
      
    \# Caso 1: Mensagem Simples  
    print("=== Caso 1: Mensagem Simples \===")  
    try:  
        result \= client.send\_message(  
            chat\_id="chat\_id\_123",  
            text="Obrigado pela sua mensagem\!"  
        )  
        print(f"✅ Mensagem enviada: {result\['message\_id'\]}")  
    except Exception as e:  
        print(f"❌ Erro: {e}")  
      
    \# Caso 2: Resposta com Citação  
    print("\\\\n=== Caso 2: Resposta com Citação \===")  
    try:  
        result \= client.send\_reply(  
            chat\_id="chat\_id\_123",  
            text="Ótimo\! Vamos agendar uma reunião?",  
            reply\_to\_message\_id="msg\_id\_456"  
        )  
        print(f"✅ Resposta enviada\!")  
    except Exception as e:  
        print(f"❌ Erro: {e}")  
      
    \# Caso 3: ChatBot Automático  
    print("\\\\n=== Caso 3: ChatBot Automático \===")  
    bot \= ChatBot(client)  
    bot.add\_response("olá", "Olá\! Como posso ajudar?")  
    bot.add\_response("preço", "Nossos preços variam. Gostaria de mais informações?")  
    bot.add\_response("horário", "Atendemos 24/7\!")  
      
    \# Simular mensagem recebida  
    bot.process\_message(  
        chat\_id="chat\_id\_123",  
        message="Olá, qual é o horário de atendimento?",  
        message\_id="msg\_id\_789"  
    )  
      
    \# Caso 4: Envio em Massa  
    print("\\\\n=== Caso 4: Envio em Massa \===")  
    messages \= \[  
        {"chat\_id": "chat\_1", "text": "Olá\! Como vai?"},  
        {"chat\_id": "chat\_2", "text": "Tudo bem? Tenho novidades\!"},  
        {"chat\_id": "chat\_3", "text": "Precisamos conversar sobre o projeto."}  
    \]  
      
    try:  
        stats \= client.send\_bulk\_messages(  
            messages=messages,  
            delay\_min=2,  
            delay\_max=5  
        )  
    except Exception as e:  
        print(f"❌ Erro: {e}")  
\`\`\`

\---

\#\# 🎯 Casos de Uso Práticos

\#\#\# 1\. Suporte ao Cliente Automático  
\`\`\`python  
\# Respostas automáticas para perguntas frequentes  
bot \= ChatBot(client)

faq \= {  
    "rastreamento": "Você pode rastrear seu pedido em: www.exemplo.com/track",  
    "devolução": "Aceitamos devoluções em até 30 dias.",  
    "contato": "Email: suporte@exemplo.com | Tel: (11) 9999-9999",  
    "horário": "Segunda a sexta: 9h-18h | Sábado: 9h-13h"  
}

for keyword, answer in faq.items():  
    bot.add\_response(keyword, answer)

\# Processar mensagens recebidas  
incoming\_message \= {  
    "chat\_id": "chat\_123",  
    "content": "Qual o horário de atendimento?",  
    "message\_id": "msg\_456"  
}

bot.process\_message(  
    incoming\_message\['chat\_id'\],  
    incoming\_message\['content'\],  
    incoming\_message\['message\_id'\]  
)  
\`\`\`

\#\#\# 2\. Seguimento de Leads  
\`\`\`python  
\# Enviar seguimentos automáticos  
follow\_ups \= \[  
    {  
        "chat\_id": "chat\_lead\_1",  
        "text": "Olá\! Verificando se você recebeu minha mensagem anterior."  
    },  
    {  
        "chat\_id": "chat\_lead\_2",  
        "text": "Gostaria de agendar uma reunião para discutir a proposta?"  
    }  
\]

client.send\_bulk\_messages(follow\_ups, delay\_min=5, delay\_max=10)  
\`\`\`

\#\#\# 3\. Envio de Documentos  
\`\`\`python  
\# Enviar documento solicitado  
client.send\_message(  
    chat\_id="chat\_123",  
    text="Aqui está o documento solicitado:",  
    attachments=\["contrato.pdf", "termos.pdf"\]  
)  
\`\`\`

\#\#\# 4\. Notificações com Contexto  
\`\`\`python  
\# Enviar notificação em resposta a mensagem anterior  
client.send\_reply(  
    chat\_id="chat\_456",  
    text="Seu pedido foi confirmado\! Rastreie aqui: www.link.com",  
    reply\_to\_message\_id="msg\_da\_pergunta"  
)  
\`\`\`

\---

\#\# ⚙️ Boas Práticas

\#\#\# 1\. Tratamento de Erros Robusto  
\`\`\`python  
def send\_with\_retry(client, chat\_id, text, max\_retries=3):  
    """Envia com retry automático."""  
    for attempt in range(max\_retries):  
        try:  
            return client.send\_message(chat\_id, text)  
        except requests.exceptions.HTTPError as e:  
            if e.response.status\_code \== 429:  \# Rate limit  
                wait \= (2 \*\* attempt) \+ random.uniform(0, 1\)  
                time.sleep(wait)  
            elif e.response.status\_code \>= 500:  \# Server error  
                time.sleep(2 \*\* attempt)  
            else:  
                raise  
      
    raise Exception("Falhou após retries")  
\`\`\`

\#\#\# 2\. Queue de Mensagens  
\`\`\`python  
from queue import Queue  
import threading

class MessageQueue:  
    """Fila de mensagens com processamento assíncrono."""  
      
    def \_\_init\_\_(self, client, max\_workers=3):  
        self.client \= client  
        self.queue \= Queue()  
        self.workers \= \[\]  
          
        for \_ in range(max\_workers):  
            worker \= threading.Thread(target=self.\_worker, daemon=True)  
            worker.start()  
            self.workers.append(worker)  
      
    def add(self, chat\_id: str, text: str):  
        """Adiciona mensagem à fila."""  
        self.queue.put({"chat\_id": chat\_id, "text": text})  
      
    def \_worker(self):  
        """Processa mensagens da fila."""  
        while True:  
            msg \= self.queue.get()  
            try:  
                self.client.send\_message(msg\["chat\_id"\], msg\["text"\])  
            except Exception as e:  
                print(f"Erro ao processar: {e}")  
            finally:  
                self.queue.task\_done()

\# Uso  
queue \= MessageQueue(client, max\_workers=5)  
queue.add("chat\_1", "Mensagem 1")  
queue.add("chat\_2", "Mensagem 2")  
\`\`\`

\#\#\# 3\. Logging Estruturado  
\`\`\`python  
import logging

logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s \- %(name)s \- %(levelname)s \- %(message)s'  
)  
logger \= logging.getLogger(\_\_name\_\_)

class LoggedMessageClient(LinkedInMessageClient):  
    def send\_message(self, \*args, \*\*kwargs):  
        logger.info(f"Enviando para chat: {args\[0\] if args else kwargs.get('chat\_id')}")  
        try:  
            result \= super().send\_message(\*args, \*\*kwargs)  
            logger.info(f"Sucesso: {result\['message\_id'\]}")  
            return result  
        except Exception as e:  
            logger.error(f"Erro: {e}")  
            raise  
\`\`\`

\---

\#\# 📊 Limites e Quotas

| Limite | Valor | Plataforma |  
|--------|-------|-----------|  
| Caracteres por mensagem | 4.000 | LinkedIn |  
| Caracteres por mensagem | 1.024 | WhatsApp |  
| Tamanho de anexo | 25 MB | Todas |  
| Requisições por minuto | Dinâmico | LinkedIn |  
| Arquivos por mensagem | Ilimitado | Todas |

\---

\#\# 📝 Versão da Documentação

\- \*\*Versão\*\*: 1.0  
\- \*\*Data\*\*: Dezembro 2024  
\- \*\*Status\*\*: Documentação Completa e Validada  
\- \*\*Compatibilidade\*\*: Python 3.7+

\---

\*\*Desenvolvido para Vibecoding \- Documentação Profissional para Desenvolvimento Orientado por IA\*\*  
