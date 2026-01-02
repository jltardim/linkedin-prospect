\# Documentação API Unipile \- LinkedIn Search Controller

\#\# 📋 Visão Geral

A API \*\*Perform LinkedIn Search\*\* do Unipile permite realizar buscas avançadas de pessoas, empresas, posts e jobs no LinkedIn através dos seguintes canais:  
\- \*\*LinkedIn Classic\*\*: API padrão do LinkedIn  
\- \*\*Sales Navigator\*\*: API de vendas com recursos avançados  
\- \*\*LinkedIn Recruiter\*\*: API especializada para recrutamento

Esta documentação aborda a integração completa para desenvolvimento de aplicações Python que realizam scraping qualificado de contatos do LinkedIn.

\---

\#\# 🔧 Informações Técnicas Básicas

\#\#\# Endpoint  
\`\`\`  
POST https://{subdomain}.unipile.com:15609/api/v1/linkedin/search  
\`\`\`

\#\#\# Método HTTP  
\`\`\`  
POST  
\`\`\`

\#\#\# Base URL Padrão  
\`\`\`  
https://api26.unipile.com:15609/api/v1/linkedin/search  
\`\`\`

\#\#\# Referência  
Documentação técnica: https://developer.unipile.com/docs/linkedin-search

\---

\#\# 🔐 Autenticação

\#\#\# Headers Obrigatórios  
\`\`\`json  
{  
  "accept": "application/json",  
  "content-type": "application/json"  
}  
\`\`\`

\#\#\# Headers de Exemplo Completo  
\`\`\`python  
headers \= {  
    "accept": "application/json",  
    "content-type": "application/json",  
    "Header": "YOUR_UNIPILE_API_KEY"  
}  
\`\`\`

\#\#\# Account ID (Obrigatório)  
O parâmetro \`account\_id\` é \*\*obrigatório\*\* em toda requisição e identifica qual conta LinkedIn será utilizada para realizar a busca.

\---

\#\# 📤 Query Parameters

\#\#\# cursor  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Comprimento Mínimo\*\*: 1  
\- \*\*Descrição\*\*: Token para paginação. Use o cursor retornado na resposta anterior para obter a próxima página de resultados. Repita este processo até recuperar todos os resultados.  
\- \*\*Opcional\*\*: Sim  
\- \*\*Padrão\*\*: Nenhum (primeira página)

\#\#\# limit  
\- \*\*Tipo\*\*: \`integer\`  
\- \*\*Intervalo\*\*: 0 a 100  
\- \*\*Padrão\*\*: 10  
\- \*\*Descrição\*\*: Define o número máximo de itens retornados por requisição.  
\- \*\*Notas Importantes\*\*:  
  \- Sales Navigator e Recruiter: até 100 resultados  
  \- LinkedIn Classic: máximo 50 resultados  
  \- Não exceda 50 para Classic sob risco de erro 400

\#\#\# account\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Descrição\*\*: Identificador único da conta autenticada que será utilizada para executar a busca.

\---

\#\# 📨 Parâmetros do Corpo da Requisição (Body)

\#\#\# Estrutura Geral  
\`\`\`json  
{  
  "api": "string (obrigatório)",  
  "category": "string (obrigatório)",  
  "params": {  
    // Parâmetros específicos conforme o tipo de busca  
  }  
}  
\`\`\`

\#\#\# Campo \`api\`  
Define qual plataforma LinkedIn será utilizada:  
\- \`classic\` \- LinkedIn Classic API (padrão)  
\- \`sales\_navigator\` \- LinkedIn Sales Navigator  
\- \`recruiter\` \- LinkedIn Recruiter

\#\#\# Campo \`category\`  
Define o tipo de busca a ser realizada. Veja seção específica para cada tipo.

\---

\#\# 🔍 Tipos de Busca Disponíveis

\#\#\# 1️⃣ Classic \- People (Busca de Pessoas)

\*\*Tipo\*\*: \`api: "classic"\` \+ \`category: "people"\`  
\`\`\`json  
{  
  "api": "classic",  
  "category": "people",  
  "params": {  
    "keywords": "string \- Palavras-chave (nome, habilidades, empresa)",  
    "location": "string \- Localização geográfica",  
    "company": "string \- Empresa atual ou anterior",  
    "school": "string \- Escola/Universidade",  
    "industry": "string \- Indústria profissional",  
    "title": "string \- Cargo/Título profissional",  
    "seniority\_level": "string \- Nível de senioridade",  
    "connection\_degree": "integer \- Grau de conexão (1, 2, 3, etc)"  
  }  
}  
\`\`\`

\*\*Exemplo Prático\*\*:  
\`\`\`json  
{  
  "api": "classic",  
  "category": "people",  
  "params": {  
    "keywords": "Python Developer",  
    "location": "São Paulo, Brazil",  
    "company": "Tech Startups",  
    "industry": "Software",  
    "title": "Senior Developer",  
    "seniority\_level": "Senior"  
  }  
}  
\`\`\`

\*\*Campos Retornados\*\*:  
\- \`public\_identifier\` \- ID público do perfil  
\- \`public\_profile\_url\` \- URL do perfil LinkedIn  
\- \`profile\_picture\_url\` \- URL da foto do perfil  
\- \`profile\_picture\_url\_large\` \- URL da foto em alta resolução  
\- \`member\_urn\` \- URN do membro  
\- \`name\` \- Nome completo  
\- \`first\_name\` \- Primeiro nome  
\- \`last\_name\` \- Sobrenome  
\- \`headline\` \- Descrição/Headline do perfil  
\- \`location\` \- Localização  
\- \`summary\` \- Resumo/Bio  
\- \`experiences\` \- Array de experiências profissionais  
\- \`educations\` \- Array de educação  
\- \`skills\` \- Array de habilidades  
\- \`connections\_count\` \- Número de conexões  
\- \`followers\_count\` \- Número de seguidores  
\- \`similar\_profiles\_url\` \- Link para perfis similares  
\- \`distance\` \- Distância de conexão (graus)

\---

\#\#\# 2️⃣ Classic \- Companies (Busca de Empresas)

\*\*Tipo\*\*: \`api: "classic"\` \+ \`category: "companies"\`  
\`\`\`json  
{  
  "api": "classic",  
  "category": "companies",  
  "params": {  
    "keywords": "string \- Nome ou ramo da empresa",  
    "location": "string \- Localização da empresa",  
    "industry": "string \- Indústria",  
    "company\_size": "string \- Tamanho da empresa",  
    "founded\_year": "integer \- Ano de fundação"  
  }  
}  
\`\`\`

\*\*Exemplo\*\*:  
\`\`\`json  
{  
  "api": "classic",  
  "category": "companies",  
  "params": {  
    "keywords": "Technology",  
    "location": "São Paulo",  
    "industry": "Software Development",  
    "company\_size": "201-500"  
  }  
}  
\`\`\`

\---

\#\#\# 3️⃣ Classic \- Posts (Busca de Posts)

\*\*Tipo\*\*: \`api: "classic"\` \+ \`category: "posts"\`  
\`\`\`json  
{  
  "api": "classic",  
  "category": "posts",  
  "params": {  
    "keywords": "string \- Palavras-chave dos posts",  
    "timeframe": "string \- Período (day, week, month, year)"  
  }  
}  
\`\`\`

\---

\#\#\# 4️⃣ Classic \- Jobs (Busca de Vagas)

\*\*Tipo\*\*: \`api: "classic"\` \+ \`category: "jobs"\`  
\`\`\`json  
{  
  "api": "classic",  
  "category": "jobs",  
  "params": {  
    "keywords": "string \- Título da vaga, habilidades",  
    "location": "string \- Localização",  
    "company": "string \- Nome da empresa",  
    "job\_type": "string \- Tipo de emprego (Full-time, Part-time, etc)",  
    "seniority\_level": "string \- Nível de senioridade",  
    "industry": "string \- Indústria"  
  }  
}  
\`\`\`

\---

\#\#\# 5️⃣ Sales Navigator \- People

\*\*Tipo\*\*: \`api: "sales\_navigator"\` \+ \`category: "people"\`  
\`\`\`json  
{  
  "api": "sales\_navigator",  
  "category": "people",  
  "params": {  
    "keywords": "string \- Palavras-chave",  
    "location": "string \- Localização",  
    "company": "string \- Empresa",  
    "title": "string \- Cargo",  
    "seniority\_level": "string \- Senioridade",  
    "function": "string \- Função",  
    "industry": "string \- Indústria",  
    "company\_size": "string \- Tamanho empresa"  
  }  
}  
\`\`\`

\*\*Recursos Adicionais\*\*:  
\- Mais filtros avançados  
\- Até 100 resultados por página  
\- Leads qualificados

\---

\#\#\# 6️⃣ Sales Navigator \- Companies

\*\*Tipo\*\*: \`api: "sales\_navigator"\` \+ \`category: "companies"\`  
\`\`\`json  
{  
  "api": "sales\_navigator",  
  "category": "companies",  
  "params": {  
    "keywords": "string",  
    "location": "string",  
    "industry": "string",  
    "company\_size": "string",  
    "revenue": "string \- Faixa de receita",  
    "founding\_year": "string"  
  }  
}  
\`\`\`

\---

\#\#\# 7️⃣ Recruiter \- People

\*\*Tipo\*\*: \`api: "recruiter"\` \+ \`category: "people"\`  
\`\`\`json  
{  
  "api": "recruiter",  
  "category": "people",  
  "params": {  
    "keywords": "string",  
    "location": "string",  
    "company": "string",  
    "title": "string",  
    "seniority\_level": "string",  
    "skills": "array \- Habilidades específicas",  
    "experience\_years": "integer \- Anos de experiência",  
    "industry": "string"  
  }  
}  
\`\`\`

\*\*Recursos Especiais\*\*:  
\- Acesso a informações de contato  
\- Até 100 resultados  
\- Dados de candidatos qualificados

\---

\#\#\# 8️⃣ Search from URL

Permite buscar a partir de uma URL LinkedIn direta:  
\`\`\`json  
{  
  "search\_from\_url": "string \- URL completa do LinkedIn"  
}  
\`\`\`

\*\*Exemplo\*\*:  
\`\`\`json  
{  
  "search\_from\_url": "https://www.linkedin.com/search/results/people/?keywords=python%20developer"  
}  
\`\`\`

\---

\#\# 📊 Resposta da API (Response)

\#\#\# Estrutura 200 OK  
\`\`\`json  
{  
  "object": "LinkedinSearch",  
  "items": \[  
    {  
      "object": "SearchResult",  
      "type": "PEOPLE",  
      "id": "string",  
      "public\_identifier": "string",  
      "public\_profile\_url": "string",  
      "profile\_picture\_url": "string",  
      "profile\_picture\_url\_large": "string",  
      "member\_urn": "string",  
      "name": "string",  
      "first\_name": "string",  
      "last\_name": "string",  
      "headline": "string",  
      "location": "string",  
      "summary": "string",  
      "experiences": \[\],  
      "educations": \[\],  
      "skills": \[\],  
      "connections\_count": 500,  
      "followers\_count": 1200,  
      "similar\_profiles\_url": "string",  
      "distance": "1st"  
    }  
  \],  
  "config": {  
    "params": {  
      // Eco dos parâmetros enviados  
    }  
  },  
  "paging": {  
    "start": 0,  
    "page\_count": 1,  
    "total\_count": 25,  
    "cursor": "next\_page\_cursor\_token"  
  }  
}  
\`\`\`

\#\#\# Campos da Resposta

\*\*object\*\*: Tipo de resposta retornada (\`LinkedinSearch\`)

\*\*items\*\*: Array de resultados encontrados. Cada item contém:  
\- \`object\`: Tipo específico (SearchResult)  
\- \`type\`: Tipo do resultado (PEOPLE, COMPANY, POST, JOB)  
\- Campos de dados específicos conforme o tipo

\*\*config\*\*: Confirmação dos parâmetros utilizados

\*\*paging\*\*: Informações de paginação  
\- \`start\`: Índice inicial dos resultados  
\- \`page\_count\`: Quantidade de páginas  
\- \`total\_count\`: Total de resultados encontrados  
\- \`cursor\`: Token para próxima página

\---

\#\# ⏳ Paginação

Para recuperar múltiplas páginas de resultados:  
\`\`\`python  
import requests  
import json

def search\_linkedin\_paginated(base\_url, account\_id, payload, max\_results=None):  
    """  
    Realiza busca no LinkedIn com suporte a paginação.  
      
    Args:  
        base\_url: URL base da API  
        account\_id: ID da conta LinkedIn  
        payload: Parâmetros de busca  
        max\_results: Máximo de resultados (None \= todos)  
      
    Returns:  
        Lista de todos os resultados encontrados  
    """  
    all\_results \= \[\]  
    cursor \= None  
    requests\_made \= 0  
      
    headers \= {  
        "accept": "application/json",  
        "content-type": "application/json",  
        "Header": "your\_auth\_token\_here"  
    }  
      
    params \= {  
        "account\_id": account\_id,  
        "limit": 50  \# Máximo para Classic  
    }  
      
    while True:  
        if cursor:  
            params\["cursor"\] \= cursor  
          
        response \= requests.post(  
            f"{base\_url}?account\_id={account\_id}",  
            headers=headers,  
            json=payload,  
            params=params  
        )  
          
        response.raise\_for\_status()  
        data \= response.json()  
          
        all\_results.extend(data.get("items", \[\]))  
        requests\_made \+= 1  
          
        \# Verificar se há próxima página  
        paging \= data.get("paging", {})  
        cursor \= paging.get("cursor")  
          
        if not cursor:  
            break  \# Sem mais páginas  
          
        if max\_results and len(all\_results) \>= max\_results:  
            all\_results \= all\_results\[:max\_results\]  
            break  
      
    return all\_results  
\`\`\`

\---

\#\# 🚨 Códigos de Erro HTTP

\#\#\# 200 \- OK

\*\*Descrição\*\*: Requisição realizada com sucesso.  
\`\`\`json  
{  
  "status": 200,  
  "message": "Request succeeded."  
}  
\`\`\`

\---

\#\#\# 400 \- Bad Request

\*\*Descrição\*\*: Um ou mais parâmetros são inválidos ou faltando.

\*\*Tipo de Erro\*\*: \`errors/invalid\_parameters\`  
\`\`\`json  
{  
  "title": "Invalid parameters",  
  "detail": "Descrição do erro específico",  
  "instance": "string",  
  "type": "errors/invalid\_parameters",  
  "status": 400  
}  
\`\`\`

\*\*Causas Comuns\*\*:  
\- Parâmetros obrigatórios não preenchidos  
\- Format de dados inválido  
\- Limit \> 50 para LinkedIn Classic  
\- Caracteres não escapados na requisição

\---

\#\#\# 401 \- Unauthorized

\*\*Descrição\*\*: Falha de autenticação ou conta desconectada.

\*\*Tipos de Erro\*\*:  
\- \`errors/missing\_credentials\` \- Credenciais não fornecidas  
\- \`errors/invalid\_credentials\` \- Credenciais inválidas  
\- \`errors/expired\_credentials\` \- Token expirado  
\- \`errors/disconnected\_account\` \- Conta desconectada do LinkedIn  
\- \`errors/insufficient\_privileges\` \- Privilégios insuficientes  
\`\`\`json  
{  
  "title": "Unauthorized",  
  "detail": "The account appears to be disconnected from the provider service.",  
  "instance": "string",  
  "type": "errors/disconnected\_account",  
  "status": 401  
}  
\`\`\`

\*\*Solução\*\*:  
\- Reconectar a conta LinkedIn  
\- Verificar token de autenticação  
\- Renovar credenciais

\---

\#\#\# 403 \- Forbidden

\*\*Descrição\*\*: Autenticação válida mas permissões insuficientes.

\*\*Tipos de Erro\*\*:  
\- \`errors/insufficient\_permissions\` \- Permissões inadequadas  
\- \`errors/account\_restricted\` \- Conta restrita pelo LinkedIn  
\- \`errors/account\_mismatch\` \- Conta não corresponde  
\- \`errors/feature\_not\_subscribed\` \- Recurso não contratado  
\- \`errors/subscription\_required\` \- Assinatura necessária  
\- \`errors/unknown\_authentication\_context\` \- Contexto de autenticação desconhecido  
\- \`errors/session\_mismatch\` \- Sessão não corresponde  
\- \`errors/resource\_access\_restricted\` \- Acesso ao recurso restrito  
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

\*\*Descrição\*\*: Recurso solicitado não encontrado.

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

\#\#\# 500 \- Internal Server Error

\*\*Descrição\*\*: Erro interno do servidor.

\*\*Tipos de Erro\*\*:  
\- \`errors/unexpected\_error\` \- Erro inesperado  
\- \`errors/provider\_error\` \- Erro do provedor (LinkedIn)  
\- \`errors/authentication\_intent\_error\` \- Erro na intenção de autenticação  
\`\`\`json  
{  
  "title": "Internal Server Error",  
  "detail": "Something went wrong. {{moreDetails}}",  
  "type": "errors/unexpected\_error",  
  "status": 500  
}  
\`\`\`

\*\*Solução\*\*: Aguarde e tente novamente. Contate suporte se persistir.

\---

\#\#\# 503 \- Service Unavailable

\*\*Descrição\*\*: Serviço indisponível.

\*\*Tipos de Erro\*\*:  
\- \`errors/no\_client\_session\` \- Sem sessão cliente  
\- \`errors/no\_channel\` \- Sem canal  
\- \`errors/no\_handler\` \- Handler faltando  
\- \`errors/network\_down\` \- Rede inativa  
\- \`errors/service\_unavailable\` \- Serviço indisponível  
\`\`\`json  
{  
  "title": "Service Unavailable",  
  "detail": "No client session is currently running.",  
  "type": "errors/no\_client\_session",  
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

\#\# 💻 Exemplo Completo em Python  
\`\`\`python  
import requests  
import json  
from typing import Dict, List, Optional

class LinkedInSearchClient:  
    """  
    Cliente para integração com API Unipile LinkedIn Search.  
    Desenvolvido para scraping qualificado de contatos.  
    """  
      
    def \_\_init\_\_(self, base\_url: str, account\_id: str, auth\_token: str):  
        """  
        Inicializa o cliente.  
          
        Args:  
            base\_url: URL base da API (ex: https://api26.unipile.com:15609)  
            account\_id: ID da conta LinkedIn autenticada  
            auth\_token: Token de autenticação  
        """  
        self.base\_url \= base\_url  
        self.account\_id \= account\_id  
        self.auth\_token \= auth\_token  
        self.endpoint \= f"{base\_url}/api/v1/linkedin/search"  
          
        self.headers \= {  
            "accept": "application/json",  
            "content-type": "application/json",  
            "Header": auth\_token  
        }  
      
    def search\_people\_classic(  
        self,  
        keywords: Optional\[str\] \= None,  
        location: Optional\[str\] \= None,  
        company: Optional\[str\] \= None,  
        title: Optional\[str\] \= None,  
        limit: int \= 10,  
        cursor: Optional\[str\] \= None  
    ) \-\> Dict:  
        """  
        Busca pessoas usando LinkedIn Classic API.  
          
        Args:  
            keywords: Palavras-chave de busca  
            location: Localização geográfica  
            company: Empresa  
            title: Cargo/Título  
            limit: Máximo de resultados (max 50\)  
            cursor: Token de paginação  
          
        Returns:  
            Resposta da API com resultados  
        """  
          
        params \= {}  
        if keywords:  
            params\["keywords"\] \= keywords  
        if location:  
            params\["location"\] \= location  
        if company:  
            params\["company"\] \= company  
        if title:  
            params\["title"\] \= title  
          
        payload \= {  
            "api": "classic",  
            "category": "people",  
            "params": params  
        }  
          
        query\_params \= {  
            "account\_id": self.account\_id,  
            "limit": min(limit, 50\)  \# Classic máximo 50  
        }  
          
        if cursor:  
            query\_params\["cursor"\] \= cursor  
          
        response \= requests.post(  
            self.endpoint,  
            headers=self.headers,  
            json=payload,  
            params=query\_params  
        )  
          
        response.raise\_for\_status()  
        return response.json()  
      
    def search\_companies\_classic(  
        self,  
        keywords: Optional\[str\] \= None,  
        location: Optional\[str\] \= None,  
        limit: int \= 10  
    ) \-\> Dict:  
        """Busca empresas usando LinkedIn Classic."""  
          
        params \= {}  
        if keywords:  
            params\["keywords"\] \= keywords  
        if location:  
            params\["location"\] \= location  
          
        payload \= {  
            "api": "classic",  
            "category": "companies",  
            "params": params  
        }  
          
        query\_params \= {  
            "account\_id": self.account\_id,  
            "limit": min(limit, 50\)  
        }  
          
        response \= requests.post(  
            self.endpoint,  
            headers=self.headers,  
            json=payload,  
            params=query\_params  
        )  
          
        response.raise\_for\_status()  
        return response.json()  
      
    def search\_people\_sales\_navigator(  
        self,  
        keywords: Optional\[str\] \= None,  
        location: Optional\[str\] \= None,  
        company: Optional\[str\] \= None,  
        title: Optional\[str\] \= None,  
        limit: int \= 50,  
        cursor: Optional\[str\] \= None  
    ) \-\> Dict:  
        """  
        Busca pessoas usando Sales Navigator (até 100 resultados).  
        Fornece dados mais qualificados para vendas e recrutamento.  
        """  
          
        params \= {}  
        if keywords:  
            params\["keywords"\] \= keywords  
        if location:  
            params\["location"\] \= location  
        if company:  
            params\["company"\] \= company  
        if title:  
            params\["title"\] \= title  
          
        payload \= {  
            "api": "sales\_navigator",  
            "category": "people",  
            "params": params  
        }  
          
        query\_params \= {  
            "account\_id": self.account\_id,  
            "limit": min(limit, 100\)  \# Sales Navigator até 100  
        }  
          
        if cursor:  
            query\_params\["cursor"\] \= cursor  
          
        response \= requests.post(  
            self.endpoint,  
            headers=self.headers,  
            json=payload,  
            params=query\_params  
        )  
          
        response.raise\_for\_status()  
        return response.json()  
      
    def get\_all\_results(  
        self,  
        search\_params: Dict,  
        max\_results: Optional\[int\] \= None,  
        api: str \= "classic"  
    ) \-\> List\[Dict\]:  
        """  
        Recupera todos os resultados com paginação automática.  
          
        Args:  
            search\_params: Parâmetros de busca  
            max\_results: Limite total de resultados  
            api: Qual API usar (classic, sales\_navigator, recruiter)  
          
        Returns:  
            Lista de todos os resultados encontrados  
        """  
          
        all\_results \= \[\]  
        cursor \= None  
          
        while True:  
            payload \= {  
                "api": api,  
                "category": search\_params.get("category", "people"),  
                "params": search\_params.get("params", {})  
            }  
              
            query\_params \= {  
                "account\_id": self.account\_id,  
                "limit": 50 if api \== "classic" else 100  
            }  
              
            if cursor:  
                query\_params\["cursor"\] \= cursor  
              
            response \= requests.post(  
                self.endpoint,  
                headers=self.headers,  
                json=payload,  
                params=query\_params  
            )  
              
            response.raise\_for\_status()  
            data \= response.json()  
              
            all\_results.extend(data.get("items", \[\]))  
              
            \# Verificar paginação  
            paging \= data.get("paging", {})  
            cursor \= paging.get("cursor")  
              
            if not cursor:  
                break  
              
            if max\_results and len(all\_results) \>= max\_results:  
                all\_results \= all\_results\[:max\_results\]  
                break  
          
        return all\_results

\# Exemplo de Uso  
if \_\_name\_\_ \== "\_\_main\_\_":  
      
    client \= LinkedInSearchClient(  
        base\_url="https://api26.unipile.com:15609",  
        account\_id="seu\_account\_id",  
        auth\_token="seu\_token\_aqui"  
    )  
      
    \# Busca simples  
    print("=== Busca Clássica por Python Developers \===")  
    try:  
        results \= client.search\_people\_classic(  
            keywords="Python Developer",  
            location="São Paulo",  
            limit=10  
        )  
          
        print(f"Total encontrado: {results\['paging'\]\['total\_count'\]}")  
        for person in results\['items'\]:  
            print(f"- {person\['name'\]} ({person\['headline'\]})")  
      
    except requests.exceptions.HTTPError as e:  
        print(f"Erro HTTP: {e.response.status\_code}")  
        print(f"Detalhes: {e.response.json()}")  
      
    \# Busca com Sales Navigator  
    print("\\\\n=== Busca Sales Navigator \===")  
    try:  
        results \= client.search\_people\_sales\_navigator(  
            keywords="CTO",  
            location="São Paulo",  
            limit=25  
        )  
          
        print(f"Total encontrado: {results\['paging'\]\['total\_count'\]}")  
        for person in results\['items'\]:  
            print(f"- {person\['name'\]} ({person\['headline'\]})")  
      
    except requests.exceptions.HTTPError as e:  
        print(f"Erro: {e.response.json()}")  
      
    \# Busca com paginação completa  
    print("\\\\n=== Busca Completa com Paginação \===")  
    try:  
        all\_people \= client.get\_all\_results(  
            search\_params={  
                "category": "people",  
                "params": {  
                    "keywords": "Data Scientist",  
                    "location": "Brazil"  
                }  
            },  
            max\_results=500,  
            api="sales\_navigator"  
        )  
          
        print(f"Total de resultados coletados: {len(all\_people)}")  
          
        \# Processar e exportar  
        with open("linkedin\_contacts.json", "w", encoding="utf-8") as f:  
            json.dump(all\_people, f, ensure\_ascii=False, indent=2)  
          
        print("Resultados salvos em linkedin\_contacts.json")  
      
    except Exception as e:  
        print(f"Erro durante busca: {str(e)}")  
\`\`\`

\---

\#\# 🎯 Casos de Uso Práticos

\#\#\# 1\. Prospecção de Clientes B2B  
\`\`\`python  
\# Buscar decisores em empresas de tecnologia  
prospects \= client.search\_people\_classic(  
    keywords="CTO OR VP Technology",  
    company="Technology Companies",  
    location="São Paulo",  
    limit=50  
)  
\`\`\`

\#\#\# 2\. Recrutamento e Talent Acquisition  
\`\`\`python  
\# Buscar Python developers sênior  
developers \= client.search\_people\_sales\_navigator(  
    keywords="Python",  
    title="Senior Developer OR Tech Lead",  
    limit=100  
)  
\`\`\`

\#\#\# 3\. Pesquisa de Mercado  
\`\`\`python  
\# Analisar concorrentes  
competitors \= client.search\_companies\_classic(  
    keywords="SaaS Platform",  
    location="Brazil",  
    limit=50  
)  
\`\`\`

\#\#\# 4\. Lista Qualificada para Vendas  
\`\`\`python  
\# Criar base de contatos qualificados  
qualified\_leads \= client.get\_all\_results(  
    search\_params={  
        "category": "people",  
        "params": {  
            "keywords": "Marketing Manager",  
            "company": "E-commerce",  
            "seniority\_level": "Senior"  
        }  
    },  
    max\_results=1000,  
    api="sales\_navigator"  
)  
\`\`\`

\---

\#\# ⚙️ Boas Práticas para Development

\#\#\# 1\. Tratamento de Erros Robusto  
\`\`\`python  
def safe\_search(client, \*\*kwargs):  
    """Busca com tratamento de erros."""  
    try:  
        return client.search\_people\_classic(\*\*kwargs)  
    except requests.exceptions.HTTPError as e:  
        error\_data \= e.response.json()  
        error\_type \= error\_data.get('type', 'unknown')  
          
        if 'disconnected\_account' in error\_type:  
            \# Reconectar conta  
            print("Conta desconectada. Reconectar necessário.")  
        elif 'limit\_too\_high' in error\_type:  
            \# Reduzir limit  
            kwargs\['limit'\] \= 25  
            return safe\_search(client, \*\*kwargs)  
        else:  
            raise  
\`\`\`

\#\#\# 2\. Rate Limiting e Throttling  
\`\`\`python  
import time  
from functools import wraps

def rate\_limit(min\_interval=1):  
    """Decorator para rate limiting."""  
    def decorator(func):  
        last\_called \= \[0.0\]  
          
        @wraps(func)  
        def wrapper(\*args, \*\*kwargs):  
            elapsed \= time.time() \- last\_called\[0\]  
            if elapsed \< min\_interval:  
                time.sleep(min\_interval \- elapsed)  
              
            result \= func(\*args, \*\*kwargs)  
            last\_called\[0\] \= time.time()  
            return result  
          
        return wrapper  
    return decorator

@rate\_limit(min\_interval=2)  
def search\_with\_limit(client, \*\*kwargs):  
    """Busca com rate limiting."""  
    return client.search\_people\_classic(\*\*kwargs)  
\`\`\`

\#\#\# 3\. Persistência e Cache  
\`\`\`python  
import json  
import hashlib

def cache\_search\_results(search\_params, api="classic"):  
    """Cacheia resultados de busca."""  
    params\_hash \= hashlib.md5(  
        json.dumps(search\_params, sort\_keys=True).encode()  
    ).hexdigest()  
      
    cache\_file \= f"cache\_{api}\_{params\_hash}.json"  
      
    try:  
        with open(cache\_file, 'r') as f:  
            return json.load(f)  
    except FileNotFoundError:  
        return None

def save\_cache(search\_params, results, api="classic"):  
    """Salva resultados em cache."""  
    params\_hash \= hashlib.md5(  
        json.dumps(search\_params, sort\_keys=True).encode()  
    ).hexdigest()  
      
    cache\_file \= f"cache\_{api}\_{params\_hash}.json"  
      
    with open(cache\_file, 'w') as f:  
        json.dump(results, f)  
\`\`\`

\---

\#\# 📈 Performance e Otimização

| API | Limite/Página | Ideal Para | Velocidade |  
|-----|--------------|-----------|-----------|  
| Classic | 50 | Teste, prototipagem | Rápida |  
| Sales Navigator | 100 | Listas qualificadas | Média |  
| Recruiter | 100 | Talent acquisition | Média |

\*\*Dicas\*\*:  
\- Use Classic para testes iniciais  
\- Use Sales Navigator para produção  
\- Implemente cache para buscas repetidas  
\- Respeite rate limits do LinkedIn

\---

\#\# 🔗 Recursos Adicionais

\- \[Documentação Oficial\](https://developer.unipile.com/docs/linkedin-search)  
\- \[API Reference Completa\](https://developer.unipile.com/reference/linkedincontroller\_search)  
\- \[Guia de LinkedIn Search\](https://developer.unipile.com/docs/linkedin-search)

\---

\#\# 📝 Versão da Documentação

\- \*\*Versão\*\*: 1.0  
\- \*\*Data\*\*: Dezembro 2024  
\- \*\*Status\*\*: Documentação Completa e Validada  
\- \*\*Compatibilidade\*\*: Python 3.7+

\---

\#\# 📞 Suporte

Para questões técnicas ou problemas com a API, consulte:  
1\. Documentação oficial da Unipile  
2\. Exemplos de código nesta documentação  
3\. Contato com suporte Unipile

\---

\*\*Desenvolvido para Vibecoding \- Documentação Profissional para Desenvolvimento Orientado por IA\*\*  
