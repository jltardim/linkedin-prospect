\# Documentação API Unipile \- Users Controller Get Profile By Identifier

\#\# 📋 Visão Geral

O endpoint \*\*Retrieve a Profile\*\* permite recuperar informações detalhadas de um perfil do LinkedIn de qualquer usuário. Este é um dos endpoints mais versáteis para acessar dados de contatos, pois suporta múltiplas redes sociais e oferece controle fino sobre quais seções de dados recuperar.

\*\*Redes Sociais Suportadas\*\*:  
\- LinkedIn  
\- WhatsApp  
\- Instagram  
\- Telegram  
\- Twitter

Esta documentação aborda a integração completa para desenvolvimento de aplicações Python que recuperam perfis qualificados do LinkedIn com dados estruturados e detalhados.

\---

\#\# 🔧 Informações Técnicas Básicas

\#\#\# Endpoint  
\`\`\`  
GET https://{subdomain}.unipile.com:{port}/api/v1/users/{identifier}  
\`\`\`

\#\#\# Método HTTP  
\`\`\`  
GET  
\`\`\`

\#\#\# Base URL Padrão  
\`\`\`  
https://api26.unipile.com:15609/api/v1/users/{identifier}  
\`\`\`

\#\#\# Documentação Oficial  
Consulte sobre limites e restrições: https://developer.unipile.com/docs/provider-limits-and-restrictions

\---

\#\# 🔐 Autenticação

\#\#\# Headers Obrigatórios  
\`\`\`json  
{  
  "accept": "application/json",  
  "X-API-KEY": "seu\_token\_aqui"  
}  
\`\`\`

\#\#\# Exemplo Completo  
\`\`\`python  
headers \= {  
    "accept": "application/json",  
    "X-API-KEY": "YOUR_UNIPILE_API_KEY"  
}  
\`\`\`

\---

\#\# 📍 Path Parameters

\#\#\# identifier  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Descrição\*\*: Pode ser o ID interno do provedor OU o ID público do provedor do usuário solicitado.  
\- \*\*Exemplos\*\*:  
  \- ID Público: \`"john-doe-123"\`  
  \- ID Interno: \`"123456789"\`  
  \- LinkedIn Public ID: \`"johndoe"\`

\---

\#\# 🔍 Query Parameters

\#\#\# linkedin\_sections  
\- \*\*Tipo\*\*: \`array of strings\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Descrição\*\*: Lista de seções de perfil do LinkedIn para recuperar dados detalhados. O LinkedIn pode limitar requisições pesadas de seções completas, portanto escolha apenas as seções que realmente precisa.

\#\#\#\# Opções de Seletores

\*\*Seletores de Preview\*\* (dados condensados):  
\- Use \`\*\_preview\` para obter TODAS as seções com dados preview (primeiras entradas como aparecem na UI do LinkedIn)  
\- Mais rápido e com menos risco de throttling

\*\*Seletores de Dados Completos\*\*:  
\- Use \`\*\` para obter TODAS as seções com dados completos (NÃO recomendado se você faz muitas chamadas de perfil em pouco tempo)  
\- Mais pesado, maior risco de throttling

\*\*Seletores Específicos\*\*:  
Você pode solicitar seções específicas individuais:  
\- \`experience\` \- Experiência profissional completa  
\- \`skills\` \- Habilidades profissionais  
\- \`education\` \- Educação e certificações  
\- \`recommendations\` \- Recomendações recebidas  
\- \`publications\` \- Publicações e artigos  
\- \`certifications\` \- Certificações profissionais  
\- \`languages\` \- Idiomas  
\- \`interests\` \- Interesses  
\- \`causes\` \- Causas apoiadas  
\- \`volunteer\` \- Trabalho voluntário  
\- \`about\` \- Seção "Sobre"  
\- \`featured\` \- Items em destaque  
\- \`honours\_awards\` \- Honrarias e prêmios

\*\*Combinações Recomendadas\*\*:  
\`\`\`python  
\# Combinação balanceada (recomendada)  
\["\*\_preview", "experience", "skills"\]

\# Apenas preview (mais rápido)  
\["\*\_preview"\]

\# Dados completos (completo)  
\["\*"\]

\# Casos de uso específicos  
\["experience", "skills", "education"\]  
\["recommendations", "certifications"\]  
\`\`\`

\#\#\#\# Comportamento de Throttling

Se o LinkedIn limitar sua requisição:  
\- Você receberá um campo \`throttled\_sections\` na resposta listando seções que foram bloqueadas  
\- Essas seções virão vazias na resposta  
\- \*\*Solução\*\*: Adicione delay aleatório entre as chamadas e não solicite tantas seções simultaneamente

\*\*Exemplo de Tratamento\*\*:  
\`\`\`python  
def handle\_throttled\_sections(response, sections\_requested):  
    throttled \= response.get("throttled\_sections", \[\])  
    if throttled:  
        print(f"Seções limitadas: {throttled}")  
        \# Retentar depois com intervalo maior  
        time.sleep(random.uniform(5, 15))  
        return False  
    return True  
\`\`\`

\---

\#\#\# linkedin\_api  
\- \*\*Tipo\*\*: \`string enum\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Padrão\*\*: \`classic\`  
\- \*\*Descrição\*\*: Define qual API do LinkedIn será usada para recuperar o perfil. Recursos relativos devem estar subscritos.

\#\#\#\# Valores Permitidos

| Valor | Descrição | Melhor Para | Dados Disponíveis |  
|-------|-----------|-----------|-------------------|  
| \`classic\` | LinkedIn API Clássica | Perfis gerais, análise de contatos | Dados básicos e completos |  
| \`recruiter\` | LinkedIn Recruiter API | Recrutamento e talent acquisition | Dados de candidatos, informações de carreira |  
| \`sales\_navigator\` | Sales Navigator API | Prospecção, vendas | Dados qualificados para vendas, informações detalhadas |

\---

\#\#\# notify  
\- \*\*Tipo\*\*: \`boolean\`  
\- \*\*Obrigatório\*\*: Não  
\- \*\*Padrão\*\*: \`false\`  
\- \*\*Descrição\*\*: Define se a visita do perfil será notificada ao usuário visualizado ou não.

\#\#\#\# Valores  
\`\`\`  
true   \- Notificar o usuário (aparecerá que você visitou seu perfil)  
false  \- Não notificar (visita anônima)  
\`\`\`

\#\#\#\# Considerações

\- \`true\`: O usuário saberá que você acessou seu perfil  
\- \`false\`: Visita anônima (recomendado para prospecção)  
\- Padrão seguro: sempre use \`false\` para não alertar

\---

\#\#\# account\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Descrição\*\*: O ID da conta que será utilizada para executar a requisição.

\---

\#\# 📊 Resposta da API (Response)

\#\#\# Estrutura 200 OK

A resposta contém informações completas do perfil. A estrutura varia conforme a rede social (LinkedIn, WhatsApp, Instagram, Telegram, Twitter).

\#\#\#\# Resposta LinkedIn (Exemplo Completo)  
\`\`\`json  
{  
  "provider": "LINKEDIN",  
  "provider\_id": "string",  
  "public\_identifier": "string",  
  "first\_name": "string",  
  "last\_name": "string",  
  "headline": "string",  
  "summary": "string",  
  "contact\_info": {  
    "emails": \[  
      "string"  
    \],  
    "phones": \[  
      "string"  
    \],  
    "addresses": \[  
      "string"  
    \],  
    "websites": \[  
      "string"  
    \],  
    "im\_accounts": \[  
      "string"  
    \]  
  },  
  "profile\_picture\_url": "string",  
  "profile\_picture\_url\_large": "string",  
  "background\_cover\_url": "string",  
  "location": "string",  
  "open\_to\_work": true,  
  "followers\_count": 0,  
  "connections\_count": 0,  
  "experiences": \[  
    {  
      "title": "string",  
      "company": "string",  
      "start\_date": "string",  
      "end\_date": "string",  
      "duration": "string",  
      "location": "string",  
      "description": "string"  
    }  
  \],  
  "educations": \[  
    {  
      "school": "string",  
      "field\_of\_study": "string",  
      "start\_date": "string",  
      "end\_date": "string",  
      "grade": "string",  
      "activities": "string"  
    }  
  \],  
  "skills": \[  
    {  
      "name": "string",  
      "endorsements\_count": 0  
    }  
  \],  
  "recommendations": \[  
    "string"  
  \],  
  "certifications": \[  
    {  
      "name": "string",  
      "issuer": "string",  
      "issue\_date": "string",  
      "expiration\_date": "string"  
    }  
  \],  
  "languages": \[  
    "string"  
  \],  
  "interests": \[  
    "string"  
  \],  
  "causes": \[  
    "string"  
  \],  
  "volunteer\_experience": \[  
    "string"  
  \],  
  "publications": \[  
    {  
      "title": "string",  
      "description": "string",  
      "published\_date": "string",  
      "publication\_url": "string"  
    }  
  \],  
  "featured": \[  
    {  
      "title": "string",  
      "url": "string",  
      "description": "string"  
    }  
  \],  
  "honours\_awards": \[  
    {  
      "title": "string",  
      "issuer": "string",  
      "issue\_date": "string"  
    }  
  \],  
  "throttled\_sections": \[\]  
}  
\`\`\`

\#\#\#\# Campos Principais

| Campo | Tipo | Descrição |  
|-------|------|-----------|  
| \`provider\` | string | Rede social (LINKEDIN, WHATSAPP, INSTAGRAM, TELEGRAM, TWITTER) |  
| \`provider\_id\` | string | ID único do usuário no provedor |  
| \`public\_identifier\` | string | Identificador público (vanity URL) |  
| \`first\_name\` | string | Primeiro nome |  
| \`last\_name\` | string | Sobrenome |  
| \`headline\` | string | Título/Descrição profissional |  
| \`summary\` | string | Bio/Resumo do perfil |  
| \`contact\_info\` | object | Informações de contato (emails, telefones, etc) |  
| \`profile\_picture\_url\` | string | URL da foto do perfil |  
| \`location\` | string | Localização geográfica |  
| \`open\_to\_work\` | boolean | Se está aberto a oportunidades |  
| \`followers\_count\` | number | Número de seguidores |  
| \`connections\_count\` | number | Número de conexões |  
| \`experiences\` | array | Histórico profissional |  
| \`educations\` | array | Histórico educacional |  
| \`skills\` | array | Habilidades profissionais |  
| \`certifications\` | array | Certificações |  
| \`languages\` | array | Idiomas |  
| \`throttled\_sections\` | array | Seções limitadas pelo LinkedIn (não retornaram dados) |

\#\#\#\# Dados de Experiência Profissional  
\`\`\`json  
{  
  "title": "Senior Python Developer",  
  "company": "Tech Company",  
  "start\_date": "2020-01",  
  "end\_date": "2023-12",  
  "duration": "3 years 11 months",  
  "location": "São Paulo, Brazil",  
  "description": "Desenvolveu aplicações Python..."  
}  
\`\`\`

\#\#\#\# Dados de Educação  
\`\`\`json  
{  
  "school": "University of São Paulo",  
  "field\_of\_study": "Computer Science",  
  "start\_date": "2016-01",  
  "end\_date": "2020-12",  
  "grade": "GPA 3.8",  
  "activities": "Python Club President"  
}  
\`\`\`

\#\#\#\# Dados de Habilidades  
\`\`\`json  
{  
  "name": "Python",  
  "endorsements\_count": 45  
}  
\`\`\`

\---

\#\# 🚨 Códigos de Erro HTTP

\#\#\# 200 \- OK

\*\*Descrição\*\*: Perfil recuperado com sucesso.  
\`\`\`json  
{  
  "provider": "LINKEDIN",  
  "provider\_id": "string",  
  "public\_identifier": "string",  
  ...  
}  
\`\`\`

\---

\#\#\# 401 \- Unauthorized

\*\*Descrição\*\*: Falha de autenticação ou conta desconectada.

\*\*Tipos de Erro\*\*:  
\- \`errors/missing\_credentials\` \- Credenciais não fornecidas  
\- \`errors/invalid\_credentials\` \- Credenciais inválidas  
\- \`errors/expired\_credentials\` \- Token expirado  
\- \`errors/disconnected\_account\` \- Conta desconectada do LinkedIn  
\- \`errors/insufficient\_privileges\` \- Privilégios insuficientes  
\- \`errors/multiple\_sessions\` \- Múltiplas sessões detectadas  
\- \`errors/wrong\_account\` \- Conta incorreta  
\- \`errors/checkpoint\_error\` \- Erro de checkpoint (verificação)  
\`\`\`json  
{  
  "title": "Unauthorized",  
  "detail": "The account appears to be disconnected from the provider service.",  
  "type": "errors/disconnected\_account",  
  "status": 401  
}  
\`\`\`

\*\*Solução\*\*:  
\- Reconectar a conta LinkedIn  
\- Renovar token de autenticação  
\- Verificar se o checkpoint foi resolvido

\---

\#\#\# 403 \- Forbidden

\*\*Descrição\*\*: Autenticação válida mas permissões insuficientes.

\*\*Tipos de Erro\*\*:  
\- \`errors/insufficient\_permissions\` \- Permissões inadequadas  
\- \`errors/account\_restricted\` \- Conta restrita pelo LinkedIn  
\- \`errors/account\_mismatch\` \- Conta não corresponde à requisição  
\- \`errors/feature\_not\_subscribed\` \- Recurso não contratado  
\- \`errors/subscription\_required\` \- Assinatura necessária  
\- \`errors/unknown\_authentication\_context\` \- Contexto desconhecido  
\- \`errors/session\_mismatch\` \- Sessão não corresponde  
\- \`errors/resource\_access\_restricted\` \- Acesso restrito  
\- \`errors/action\_required\` \- Ação adicional necessária  
\`\`\`json  
{  
  "title": "Forbidden",  
  "detail": "Valid authentication but insufficient permissions to perform the request.",  
  "type": "errors/insufficient\_permissions",  
  "status": 403  
}  
\`\`\`

\---

\#\#\# 404 \- Not Found

\*\*Descrição\*\*: Perfil não encontrado.

\*\*Tipos de Erro\*\*:  
\- \`errors/resource\_not\_found\` \- Recurso não existe  
\- \`errors/invalid\_resource\_identifier\` \- ID inválido  
\`\`\`json  
{  
  "title": "Not Found",  
  "detail": "The requested resource were not found. User not found",  
  "type": "errors/resource\_not\_found",  
  "status": 404  
}  
\`\`\`

\*\*Causas\*\*:  
\- Identifier inválido ou incorreto  
\- Usuário deletado ou desativado  
\- Perfil privado ou bloqueado

\---

\#\#\# 422 \- Unprocessable Entity

\*\*Descrição\*\*: Entidade não pode ser processada.

\*\*Tipos de Erro\*\*:  
\- \`errors/invalid\_account\` \- Conta não é válida para este recurso  
\- \`errors/invalid\_recipient\` \- Destinatário inválido  
\- \`errors/user\_unreachable\` \- Usuário inacessível  
\`\`\`json  
{  
  "title": "Unprocessable Entity",  
  "detail": "Provided account is not designed for this feature.",  
  "type": "errors/invalid  
