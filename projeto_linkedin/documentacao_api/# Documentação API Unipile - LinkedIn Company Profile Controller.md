\# Documentação API Unipile \- LinkedIn Company Profile Controller

\#\# 📋 Visão Geral

O endpoint \*\*Retrieve a Company Profile\*\* permite obter informações detalhadas e estruturadas de qualquer empresa do LinkedIn. Este é um endpoint essencial para inteligência empresarial, análise de concorrentes, pesquisa B2B e enriquecimento de dados corporativos.

\*\*Características Principais\*\*:  
\- Recuperar dados completos de empresa  
\- Análise de permissões de acesso administrativo  
\- Dados de financiamento e investimento  
\- Informações de localização e contato  
\- Dados de crescimento e insights  
\- Informações de aquisição empresarial

Esta documentação aborda a integração completa para desenvolvimento de aplicações Python que coletam e analisam dados de empresas do LinkedIn.

\---

\#\# 🔧 Informações Técnicas Básicas

\#\#\# Endpoint  
\`\`\`  
GET https://{subdomain}.unipile.com:{port}/api/v1/linkedin/company/{identifier}  
\`\`\`

\#\#\# Método HTTP  
\`\`\`  
GET  
\`\`\`

\#\#\# Base URL Padrão  
\`\`\`  
https://api26.unipile.com:15609/api/v1/linkedin/company/{identifier}  
\`\`\`

\#\#\# Descrição  
Recupera um perfil de empresa a partir de seu nome ou ID.

\---

\#\# 🔐 Autenticação

\#\#\# Headers Obrigatórios  
\`\`\`json  
{  
  "accept": "application/json",  
  "X-API-KEY": "sua\_chave\_api"  
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
\- \*\*Descrição\*\*: Identificador da empresa. Pode ser:  
  \- ID público da empresa  
  \- ID interno da empresa  
  \- URN (Uniform Resource Name) da empresa

\*\*Exemplos\*\*:  
\- ID Público: \`"google"\`  
\- ID Interno: \`"123456789"\`  
\- LinkedIn URN: \`"urn:li:organization:1441"\`  
\- Nome da empresa: \`"Google"\`

\---

\#\# 🔍 Query Parameters

\#\#\# account\_id  
\- \*\*Tipo\*\*: \`string\`  
\- \*\*Obrigatório\*\*: Sim ✓  
\- \*\*Descrição\*\*: O ID da conta LinkedIn que será utilizada para executar a requisição.

\---

\#\# 📊 Resposta da API (Response 200 OK)

\#\#\# Estrutura Completa da Resposta  
\`\`\`json  
{  
  "object": "CompanyProfile",  
  "id": "string",  
  "name": "string",  
  "description": "string",  
  "entity\_urn": "string",  
  "public\_identifier": "string",  
  "profile\_url": "string",  
  "tagline": "string",  
  "followers\_count": 0,  
  "is\_following": true,  
  "is\_employee": true,  
  "hashtags": \[  
    {  
      "title": "string"  
    }  
  \],  
  "messaging": {  
    "is\_enabled": true,  
    "id": "string",  
    "entity\_urn": "string"  
  },  
  "claimed": true,  
  "viewer\_permissions": {  
    "canMembersInviteToFollow": true,  
    "canReadContentSuggestions": true,  
    "canReadMessages": true,  
    "canUpdateOrganizationProfile": true,  
    "canCreateOrganicShare": true,  
    "canReadAdminDashboard": true,  
    "canReadOrganizationActivity": true,  
    "canEditCurators": true,  
    "canManageOrganizationalPageFollow": true,  
    "canReadOrganizationFollowerAnalytics": true,  
    "canInviteMemberToFollow": true,  
    "canReadOrganizationLeadsAnalytics": true,  
    "canEditPendingAdministrators": true,  
    "canManageMessagingAccess": true,  
    "canSeeEmployeeExperienceAsMember": true,  
    "canEmployeesInviteToFollow": true,  
    "canSeeOrganizationAdministrativePage": true,  
    "canManageAdminRoles": true,  
    "canEditOrganizationDetails": true,  
    "canApproveContent": true,  
    "canViewTeamPerformance": true,  
    "canManageOrganizationSettings": true,  
    "canAccessAdvancedAnalytics": true,  
    "canModerateComments": true,  
    "canCreateAds": true,  
    "canManageAdBudgets": true,  
    "canEditPageTheme": true,  
    "canPublishNewsletters": true,  
    "canEditCustomTabs": true,  
    "canManageIntegrations": true,  
    "canAssignRoles": true,  
    "canApprovePendingMembers": true,  
    "canEditCareerPageSettings": true,  
    "canViewBillingInformation": true  
  },  
  "organization\_type": "string",  
  "locations": \[  
    {  
      "is\_headquarter": true,  
      "country": "string",  
      "city": "string",  
      "postal\_code": "string",  
      "street": \[  
        "string"  
      \],  
      "description": "string",  
      "area": "string",  
      "logo": "string",  
      "localized\_description": \[  
        {  
          "locale": "string",  
          "value": "string"  
        }  
      \],  
      "localized\_name": \[  
        {  
          "locale": "string",  
          "value": "string"  
        }  
      \],  
      "localized\_tagline": \[  
        {  
          "locale": "string",  
          "value": "string"  
        }  
      \]  
    }  
  \],  
  "industry": \[  
    "string"  
  \],  
  "activities": \[  
    "string"  
  \],  
  "employee\_count": 0,  
  "employee\_count\_range": {  
    "from": 0,  
    "to": 0  
  },  
  "website": "string",  
  "foundation\_date": "string",  
  "phone": "string",  
  "insights": {  
    "employeesCount": {  
      "value": 0  
    }  
  },  
  "acquired\_by": {  
    "id": "string",  
    "name": "string",  
    "public\_identifier": "string",  
    "profile\_url": "string"  
  },  
  "crunchbase\_funding": {  
    "last\_updated\_at": "string",  
    "company\_url": "string",  
    "rounds": {  
      "funding\_type": "string",  
      "announced\_date": "string",  
      "url": "string",  
      "funding\_type": "string",  
      "investors\_count": 0,  
      "lead\_investors": \[  
        {  
          "name": "string",  
          "url": "string",  
          "logo": "string"  
        }  
      \],  
      "money\_raised": {  
        "amount": 0,  
        "currency": "string"  
      }  
    }  
  }  
}  
\`\`\`

\#\#\# Seções Principais

\#\#\#\# Informações Básicas

| Campo | Tipo | Descrição |  
|-------|------|-----------|  
| \`object\` | string | Tipo de objeto (CompanyProfile) |  
| \`id\` | string | ID único da empresa |  
| \`name\` | string | Nome da empresa |  
| \`description\` | string | Descrição detalhada |  
| \`entity\_urn\` | string | URN da empresa |  
| \`public\_identifier\` | string | ID público/vanity URL |  
| \`profile\_url\` | string | URL do perfil LinkedIn |  
| \`tagline\` | string | Tagline/slogan da empresa |

\#\#\#\# Estatísticas de Engajamento

| Campo | Tipo | Descrição |  
|-------|------|-----------|  
| \`followers\_count\` | number | Total de seguidores |  
| \`is\_following\` | boolean | Se você segue a empresa |  
| \`is\_employee\` | boolean | Se você trabalha lá |  
| \`employee\_count\` | number | Número de funcionários |  
| \`employee\_count\_range\` | object | Range de contagem (ex: 1000-5000) |

\#\#\#\# Localização  
\`\`\`json  
{  
  "is\_headquarter": true,  
  "country": "Brazil",  
  "city": "São Paulo",  
  "postal\_code": "01311-100",  
  "street": \["Av. Paulista, 1578"\],  
  "description": "Headquarters"  
}  
\`\`\`

\#\#\#\# Dados de Financiamento (Crunchbase)  
\`\`\`json  
{  
  "funding\_type": "Series A",  
  "announced\_date": "2023-06-15",  
  "url": "https://crunchbase.com/...",  
  "investors\_count": 5,  
  "lead\_investors": \[  
    {  
      "name": "Sequoia Capital",  
      "url": "https://...",  
      "logo": "https://..."  
    }  
  \],  
  "money\_raised": {  
    "amount": 10000000,  
    "currency": "USD"  
  }  
}  
\`\`\`

\#\#\#\# Permissões do Visualizador

A resposta inclui 30+ campos booleanos indicando quais ações o usuário autenticado pode realizar:

\- \`canReadAdminDashboard\` \- Acessar dashboard administrativo  
\- \`canEditOrganizationDetails\` \- Editar detalhes da empresa  
\- \`canApproveContent\` \- Aprovar conteúdo  
\- \`canViewTeamPerformance\` \- Ver performance do time  
\- \`canManageOrganizationSettings\` \- Gerenciar configurações  
\- \`canAccessAdvancedAnalytics\` \- Acessar análises avançadas  
\- \`canCreateAds\` \- Criar anúncios  
\- \`canPublishNewsletters\` \- Publicar newsletters  
\- E mais 20+ permissões...

\---

\#\# 🚨 Códigos de Erro HTTP

\#\#\# 200 \- OK

\*\*Descrição\*\*: Perfil de empresa recuperado com sucesso.  
\`\`\`json  
{  
  "object": "CompanyProfile",  
  "id": "123456",  
  "name": "Google Brazil",  
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
\- \`errors/disconnected\_account\` \- Conta desconectada  
\- \`errors/insufficient\_privileges\` \- Privilégios insuficientes  
\- \`errors/multiple\_sessions\` \- Múltiplas sessões  
\- \`errors/checkpoint\_error\` \- Erro de checkpoint  
\`\`\`json  
{  
  "title": "Unauthorized",  
  "detail": "The account appears to be disconnected from the provider service.",  
  "type": "errors/disconnected\_account",  
  "status": 401  
}  
\`\`\`

\*\*Solução\*\*: Reconectar a conta LinkedIn, renovar token.

\---

\#\#\# 403 \- Forbidden

\*\*Descrição\*\*: Autenticação válida mas permissões insuficientes.

\*\*Tipos de Erro\*\*:  
\- \`errors/insufficient\_permissions\` \- Permissões inadequadas  
\- \`errors/account\_restricted\` \- Conta restrita pelo LinkedIn  
\- \`errors/account\_mismatch\` \- Conta não corresponde  
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

\*\*Descrição\*\*: Empresa não encontrada.

\*\*Tipos de Erro\*\*:  
\- \`errors/resource\_not\_found\` \- Recurso não existe  
\- \`errors/invalid\_resource\_identifier\` \- ID inválido  
\`\`\`json  
{  
  "title": "Not Found",  
  "detail": "The requested resource were not found. Company not found",  
  "type": "errors/resource\_not\_found",  
  "status": 404  
}  
\`\`\`

\*\*Causas\*\*:  
\- Identifier/ID inválido  
\- Empresa não existe no LinkedIn  
\- Perfil deletado ou desativado

\---

\#\#\# 422 \- Unprocessable Entity

\*\*Descrição\*\*: Entidade não pode ser processada.

\*\*Tipos de Erro\*\*:  
\- \`errors/invalid\_account\` \- Conta não é válida para este recurso  
\- \`errors/unprocessable\_entity\` \- Entidade não processável  
\`\`\`json  
{  
  "title": "Unprocessable Entity",  
  "detail": "Provided account is not designed for this feature.",  
  "type": "errors/invalid\_account",  
  "status": 422  
}  
\`\`\`

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

\#\# 💻 Exemplo Completo em Python  
\`\`\`python  
import requests  
import json  
import time  
import random  
from typing import Dict, List, Optional  
from dataclasses import dataclass

@dataclass  
class CompanyLocation:  
    """Representa uma localização de empresa."""  
    is\_headquarter: bool  
    country: str  
    city: str  
    postal\_code: str \= ""  
    street: List\[str\] \= None  
    description: str \= ""

@dataclass  
class FundingRound:  
    """Representa uma rodada de financiamento."""  
    funding\_type: str  
    announced\_date: str  
    investors\_count: int  
    money\_raised: Dict \= None

class LinkedInCompanyClient:  
    """  
    Cliente para recuperar perfis de empresas do LinkedIn via Unipile.  
    Implementa tratamento robusto de erros e análise de dados.  
    """  
      
    def \_\_init\_\_(self, base\_url: str, account\_id: str, api\_key: str):  
        """  
        Inicializa o cliente.  
          
        Args:  
            base\_url: URL base da API  
            account\_id: ID da conta LinkedIn  
            api\_key: Chave de API  
        """  
        self.base\_url \= base\_url  
        self.account\_id \= account\_id  
        self.api\_key \= api\_key  
        self.endpoint\_base \= f"{base\_url}/api/v1/linkedin/company"  
          
        self.headers \= {  
            "accept": "application/json",  
            "X-API-KEY": api\_key  
        }  
      
    def get\_company\_profile(self, identifier: str) \-\> Dict:  
        """  
        Recupera o perfil completo de uma empresa.  
          
        Args:  
            identifier: ID, nome ou URN da empresa  
          
        Returns:  
            Dados completos do perfil da empresa  
          
        Raises:  
            requests.exceptions.HTTPError: Para erros HTTP  
        """  
          
        url \= f"{self.endpoint\_base}/{identifier}"  
        params \= {"account\_id": self.account\_id}  
          
        try:  
            response \= requests.get(  
                url,  
                headers=self.headers,  
                params=params,  
                timeout=30  
            )  
              
            response.raise\_for\_status()  
            return response.json()  
          
        except requests.exceptions.HTTPError as e:  
            error\_status \= e.response.status\_code  
            error\_data \= e.response.json()  
            error\_type \= error\_data.get('type', 'unknown')  
              
            if error\_status \== 404:  
                print(f"❌ Empresa não encontrada: {identifier}")  
            elif error\_status \== 401:  
                print(f"🔐 Erro de autenticação: {error\_type}")  
            elif error\_status \== 403:  
                print(f"🚫 Acesso negado: {error\_type}")  
              
            raise  
      
    def extract\_company\_summary(self, company: Dict) \-\> Dict:  
        """  
        Extrai informações resumidas da empresa.  
          
        Args:  
            company: Dados completos da empresa  
          
        Returns:  
            Resumo estruturado  
        """  
          
        \# Localização  
        locations \= company.get('locations', \[\])  
        headquarters \= next(  
            (l for l in locations if l.get('is\_headquarter')),   
            locations\[0\] if locations else {}  
        )  
          
        \# Financiamento  
        crunchbase \= company.get('crunchbase\_funding', {})  
        funding\_rounds \= crunchbase.get('rounds', \[\])  
        total\_funding \= sum(  
            r.get('money\_raised', {}).get('amount', 0\)   
            for r in funding\_rounds   
            if isinstance(r, dict)  
        )  
          
        return {  
            "nome": company.get('name'),  
            "id": company.get('id'),  
            "public\_id": company.get('public\_identifier'),  
            "descricao": company.get('description', '')\[:200\] \+ "...",  
            "type\_organizacao": company.get('organization\_type'),  
            "tagline": company.get('tagline'),  
            "website": company.get('website'),  
            "telefone": company.get('phone'),  
            "setor": company.get('industry', \[\]),  
            "atividades": company.get('activities', \[\]),  
            "funcionarios": company.get('employee\_count'),  
            "range\_funcionarios": company.get('employee\_count\_range'),  
            "seguidores": company.get('followers\_count'),  
            "headquarters": {  
                "pais": headquarters.get('country'),  
                "cidade": headquarters.get('city'),  
                "endereco": headquarters.get('street', \[\]),  
            },  
            "financiamento": {  
                "total": total\_funding,  
                "rodadas": len(funding\_rounds),  
                "ultima\_atualizacao": crunchbase.get('last\_updated\_at'),  
            },  
            "acquisicoes": company.get('acquired\_by'),  
            "permissoes": {  
                "pode\_editar": company.get('viewer\_permissions', {}).get('canEditOrganizationDetails'),  
                "pode\_acessar\_dashboard": company.get('viewer\_permissions', {}).get('canReadAdminDashboard'),  
                "pode\_criar\_ads": company.get('viewer\_permissions', {}).get('canCreateAds'),  
            }  
        }  
      
    def analyze\_company\_growth(self, company: Dict) \-\> Dict:  
        """  
        Analisa crescimento e trajetória da empresa.  
          
        Args:  
            company: Dados da empresa  
          
        Returns:  
            Análise de crescimento  
        """  
          
        employee\_count \= company.get('employee\_count', 0\)  
        followers \= company.get('followers\_count', 0\)  
        crunchbase \= company.get('crunchbase\_funding', {})  
        rounds \= crunchbase.get('rounds', \[\])  
          
        \# Determinar estágio  
        if not rounds:  
            stage \= "Bootstrapped/Privado"  
        else:  
            last\_round \= rounds\[-1\] if isinstance(rounds, list) else None  
            if last\_round:  
                funding\_type \= last\_round.get('funding\_type', '')  
                if 'Seed' in funding\_type:  
                    stage \= "Seed"  
                elif 'Series A' in funding\_type:  
                    stage \= "Série A"  
                elif 'Series B' in funding\_type:  
                    stage \= "Série B"  
                elif 'Series C+' in funding\_type or 'Series' in funding\_type:  
                    stage \= "Série C+"  
                else:  
                    stage \= "Estágio Avançado"  
            else:  
                stage \= "Desconhecido"  
          
        \# Calcular métricas  
        growth\_indicators \= {  
            "estagio\_empresa": stage,  
            "numero\_funcionarios": employee\_count,  
            "seguidores\_linkedin": followers,  
            "rodadas\_financiamento": len(rounds) if isinstance(rounds, list) else 0,  
            "recebeu\_aquisicao": bool(company.get('acquired\_by')),  
            "ativa": not company.get('acquired\_by'),  
        }  
          
        return growth\_indicators  
      
    def get\_company\_financials(self, company: Dict) \-\> Dict:  
        """  
        Extrai informações de financiamento da empresa.  
          
        Args:  
            company: Dados da empresa  
          
        Returns:  
            Dados de financiamento estruturados  
        """  
          
        crunchbase \= company.get('crunchbase\_funding', {})  
        rounds \= crunchbase.get('rounds', \[\])  
          
        financial\_data \= {  
            "total\_raised": 0,  
            "currency": "USD",  
            "rounds": \[\],  
            "lead\_investors": set(),  
            "funding\_timeline": \[\]  
        }  
          
        if isinstance(rounds, list):  
            for round\_data in rounds:  
                if isinstance(round\_data, dict):  
                    \# Financiamento da rodada  
                    money \= round\_data.get('money\_raised', {})  
                    amount \= money.get('amount', 0\)  
                      
                    financial\_data\['total\_raised'\] \+= amount  
                    financial\_data\['currency'\] \= money.get('currency', 'USD')  
                      
                    \# Informações da rodada  
                    round\_info \= {  
                        "tipo": round\_data.get('funding\_type'),  
                        "data": round\_data.get('announced\_date'),  
                        "valor": amount,  
                        "num\_investidores": round\_data.get('investors\_count', 0),  
                        "url": round\_data.get('url')  
                    }  
                      
                    financial\_data\['rounds'\].append(round\_info)  
                    financial\_data\['funding\_timeline'\].append(  
                        f"{round\_data.get('announced\_date')} \- {round\_data.get('funding\_type')}: ${amount:,}"  
                    )  
                      
                    \# Lead investors  
                    lead\_investors \= round\_data.get('lead\_investors', \[\])  
                    if isinstance(lead\_investors, list):  
                        for investor in lead\_investors:  
                            if isinstance(investor, dict):  
                                financial\_data\['lead\_investors'\].add(investor.get('name'))  
          
        financial\_data\['lead\_investors'\] \= list(financial\_data\['lead\_investors'\])  
          
        return financial\_data  
      
    def batch\_get\_companies(  
        self,  
        identifiers: List\[str\],  
        delay\_min: float \= 2,  
        delay\_max: float \= 5  
    ) \-\> Dict:  
        """  
        Recupera múltiplas empresas com delays para respeitar rate limits.  
          
        Args:  
            identifiers: Lista de IDs de empresas  
            delay\_min: Delay mínimo  
            delay\_max: Delay máximo  
          
        Returns:  
            Dicionário com resultados  
        """  
          
        results \= {  
            "sucesso": \[\],  
            "falhas": \[\],  
            "total": len(identifiers)  
        }  
          
        for idx, identifier in enumerate(identifiers, 1):  
            try:  
                print(f"\[{idx}/{len(identifiers)}\] Recuperando: {identifier}")  
                  
                company \= self.get\_company\_profile(identifier)  
                results\['sucesso'\].append(company)  
                  
                \# Delay  
                delay \= random.uniform(delay\_min, delay\_max)  
                print(f"⏱️  Aguardando {delay:.1f}s...")  
                time.sleep(delay)  
              
            except requests.exceptions.HTTPError as e:  
                print(f"❌ Erro: {e.response.status\_code}")  
                results\['falhas'\].append({  
                    "identifier": identifier,  
                    "status\_code": e.response.status\_code  
                })  
          
        print(f"\\\\n✅ Sucesso: {len(results\['sucesso'\])}")  
        print(f"❌ Falhas: {len(results\['falhas'\])}")  
          
        return results  
      
    def compare\_companies(self, company\_ids: List\[str\]) \-\> Dict:  
        """  
        Compara múltiplas empresas lado a lado.  
          
        Args:  
            company\_ids: Lista de IDs de empresas  
          
        Returns:  
            Análise comparativa  
        """  
          
        companies \= \[\]  
        for company\_id in company\_ids:  
            try:  
                company \= self.get\_company\_profile(company\_id)  
                companies.append(company)  
                time.sleep(random.uniform(2, 4))  
            except Exception as e:  
                print(f"Erro ao recuperar {company\_id}: {e}")  
          
        if not companies:  
            return {}  
          
        \# Criar tabela comparativa  
        comparison \= {  
            "nomes": \[c.get('name') for c in companies\],  
            "setores": \[c.get('industry', \[\]) for c in companies\],  
            "funcionarios": \[c.get('employee\_count') for c in companies\],  
            "seguidores": \[c.get('followers\_count') for c in companies\],  
            "website": \[c.get('website') for c in companies\],  
            "paises": \[  
                c.get('locations', \[{}\])\[0\].get('country')   
                for c in companies  
            \]  
        }  
          
        return comparison

\# Exemplo de Uso  
if \_\_name\_\_ \== "\_\_main\_\_":  
      
    client \= LinkedInCompanyClient(  
        base\_url="https://api26.unipile.com:15609",  
        account\_id="seu\_account\_id",  
        api\_key="sua\_chave\_api"  
    )  
      
    \# Caso 1: Recuperar uma empresa  
    print("=== Recuperando Perfil de Empresa \===")  
    try:  
        google \= client.get\_company\_profile("google")  
        summary \= client.extract\_company\_summary(google)  
        print(json.dumps(summary, indent=2, ensure\_ascii=False))  
    except Exception as e:  
        print(f"Erro: {e}")  
      
    \# Caso 2: Analisar crescimento  
    print("\\\\n=== Análise de Crescimento \===")  
    try:  
        growth \= client.analyze\_company\_growth(google)  
        print(f"Estágio: {growth\['estagio\_empresa'\]}")  
        print(f"Funcionários: {growth\['numero\_funcionarios'\]}")  
        print(f"Seguidores: {growth\['seguidores\_linkedin'\]}")  
        print(f"Rodadas: {growth\['rodadas\_financiamento'\]}")  
    except Exception as e:  
        print(f"Erro: {e}")  
      
    \# Caso 3: Dados de financiamento  
    print("\\\\n=== Financiamento \===")  
    try:  
        financials \= client.get\_company\_financials(google)  
        print(f"Total Raised: ${financials\['total\_raised'\]:,.0f}")  
        print(f"Lead Investors: {', '.join(financials\['lead\_investors'\]\[:3\])}")  
        print(f"Timeline:")  
        for line in financials\['funding\_timeline'\]\[:5\]:  
            print(f"  \- {line}")  
    except Exception as e:  
        print(f"Erro: {e}")  
      
    \# Caso 4: Comparar empresas  
    print("\\\\n=== Comparação de Empresas \===")  
    try:  
        comparison \= client.compare\_companies(\["google", "microsoft", "apple"\])  
        print(json.dumps(comparison, indent=2, ensure\_ascii=False))  
    except Exception as e:  
        print(f"Erro: {e}")  
\`\`\`

\---

\#\# 🎯 Casos de Uso Práticos

\#\#\# 1\. Inteligência Competitiva  
\`\`\`python  
\# Analisar concorrentes  
client \= LinkedInCompanyClient(...)

competitors \= \["competitor1", "competitor2", "competitor3"\]  
for comp\_id in competitors:  
    try:  
        company \= client.get\_company\_profile(comp\_id)  
        summary \= client.extract\_company\_summary(company)  
        growth \= client.analyze\_company\_growth(company)  
          
        print(f"{summary\['nome'\]}")  
        print(f"  Funcionários: {growth\['numero\_funcionarios'\]}")  
        print(f"  Estágio: {growth\['estagio\_empresa'\]}")  
        print(f"  Seguidores: {growth\['seguidores\_linkedin'\]}")  
    except Exception as e:  
        print(f"Erro: {e}")  
\`\`\`

\#\#\# 2\. Pesquisa de Investimento  
\`\`\`python  
\# Analisar potencial de investimento  
client \= LinkedInCompanyClient(...)

startup \= client.get\_company\_profile("startup\_id")  
financials \= client.get\_company\_financials(startup)  
growth \= client.analyze\_company\_growth(startup)

print(f"Potencial de Investimento:")  
print(f"  \- Total Raised: ${financials\['total\_raised'\]:,.0f}")  
print(f"  \- Rodadas: {financials\['rounds'\]}")  
print(f"  \- Crescimento: {growth\['numero\_funcionarios'\]} employees")  
print(f"  \- Ativa: {growth\['ativa'\]}")  
\`\`\`

\#\#\# 3\. Prospecção B2B  
\`\`\`python  
\# Encontrar empresas para vender  
client \= LinkedInCompanyClient(...)

target\_companies \= \["company1", "company2", "company3"\]  
prospects \= \[\]

for company\_id in target\_companies:  
    try:  
        company \= client.get\_company\_profile(company\_id)  
          
        \# Verificar critérios  
        if (company.get('employee\_count', 0\) \> 500 and   
            "Technology" in company.get('industry', \[\])):  
              
            prospects.append({  
                "nome": company.get('name'),  
                "website": company.get('website'),  
                "contato": company.get('phone'),  
                "funcionarios": company.get('employee\_count')  
            })  
          
        time.sleep(random.uniform(2, 4))  
      
    except Exception as e:  
        print(f"Erro: {e}")

\# Salvar prospects  
with open("prospects.json", "w") as f:  
    json.dump(prospects, f, indent=2)  
\`\`\`

\#\#\# 4\. Monitoramento de Empresa  
\`\`\`python  
\# Monitorar status de empresa ao longo do tempo  
def monitor\_company\_changes(company\_id, days=30):  
    client \= LinkedInCompanyClient(...)  
      
    current \= client.get\_company\_profile(company\_id)  
    current\_data \= {  
        "data": datetime.now().isoformat(),  
        "funcionarios": current.get('employee\_count'),  
        "seguidores": current.get('followers\_count'),  
        "rodadas": len(current.get('crunchbase\_funding', {}).get('rounds', \[\]))  
    }  
      
    return current\_data

\# Comparar com histórico  
history \= load\_history("company\_history.json")  
latest \= monitor\_company\_changes("google")

if latest\['funcionarios'\] \> history\[-1\]\['funcionarios'\]:  
    print("✅ Empresa em crescimento\!")  
\`\`\`

\---

\#\# ⚙️ Boas Práticas

\#\#\# 1\. Tratamento Robusto de Erros  
\`\`\`python  
def get\_company\_safe(client, company\_id, max\_retries=3):  
    """Recuperar com retry automático."""  
    for attempt in range(max\_retries):  
        try:  
            return client.get\_company\_profile(company\_id)  
        except requests.exceptions.HTTPError as e:  
            if e.response.status\_code \== 404:  
                return None  \# Não retentar  
            elif e.response.status\_code \>= 500:  
                time.sleep(2 \*\* attempt)  \# Backoff exponencial  
            else:  
                raise  
      
    return None  
\`\`\`

\#\#\# 2\. Cache e Persistência  
\`\`\`python  
import json  
from pathlib import Path

class CachedCompanyClient(LinkedInCompanyClient):  
    def \_\_init\_\_(self, \*args, cache\_dir="./cache", \*\*kwargs):  
        super().\_\_init\_\_(\*args, \*\*kwargs)  
        self.cache\_dir \= Path(cache\_dir)  
        self.cache\_dir.mkdir(exist\_ok=True)  
      
    def get\_company\_profile(self, identifier: str) \-\> Dict:  
        cache\_file \= self.cache\_dir / f"{identifier}.json"  
          
        if cache\_file.exists():  
            with open(cache\_file) as f:  
                return json.load(f)  
          
        company \= super().get\_company\_profile(identifier)  
          
        with open(cache\_file, 'w') as f:  
            json.dump(company, f, indent=2)  
          
        return company  
\`\`\`

\#\#\# 3\. Exportação Estruturada  
\`\`\`python  
def export\_companies\_to\_csv(companies: List\[Dict\], filename: str):  
    """Exportar dados de empresas para CSV."""  
    import csv  
      
    with open(filename, 'w', newline='', encoding='utf-8') as f:  
        writer \= csv.DictWriter(f, fieldnames=\[  
            'name', 'employee\_count', 'followers', 'industry',   
            'website', 'country', 'funding\_total'  
        \])  
        writer.writeheader()  
          
        for company in companies:  
            writer.writerow({  
                'name': company.get('name'),  
                'employee\_count': company.get('employee\_count'),  
                'followers': company.get('followers\_count'),  
                'industry': ', '.join(company.get('industry', \[\])),  
                'website': company.get('website'),  
                'country': company.get('locations', \[{}\])\[0\].get('country'),  
                'funding\_total': sum(  
                    r.get('money\_raised', {}).get('amount', 0\)  
                    for r in company.get('crunchbase\_funding', {}).get('rounds', \[\])  
                    if isinstance(r, dict)  
                )  
            })  
\`\`\`

\---

\#\# 📊 Campos Principais Resumo

| Categoria | Campos | Descripción |  
|-----------|--------|-------------|  
| \*\*Identidade\*\* | id, name, public\_identifier, entity\_urn | Identificadores únicos |  
| \*\*Contato\*\* | website, phone, locations | Informações de contato |  
| \*\*Tamanho\*\* | employee\_count, employee\_count\_range | Métricas de tamanho |  
| \*\*Engajamento\*\* | followers\_count, is\_following | Dados sociais |  
| \*\*Classificação\*\* | industry, activities, organization\_type | Categorização |  
| \*\*Financiamento\*\* | crunchbase\_funding, acquired\_by | Dados de investimento |  
| \*\*Permissões\*\* | viewer\_permissions (30+ campos) | Controle de acesso |

\---

\#\# 🔗 Integração com Outros Endpoints

Combine este endpoint com outros para workflows completos:  
\`\`\`python  
\# 1\. Buscar empresas  
search\_client \= LinkedInSearchClient(...)  
companies \= search\_client.search\_companies\_classic(  
    keywords="SaaS",  
    location="Brazil"  
)

\# 2\. Recuperar perfis completos  
company\_client \= LinkedInCompanyClient(...)  
details \= \[\]

for result in companies\['items'\]:  
    detail \= company\_client.get\_company\_profile(  
        result\['public\_identifier'\]  
    )  
    details.append(detail)  
    time.sleep(random.uniform(2, 4))

\# 3\. Analisar e exportar  
summary\_data \= \[  
    company\_client.extract\_company\_summary(c)   
    for c in details  
\]

with open("company\_analysis.json", "w") as f:  
    json.dump(summary\_data, f, indent=2)  
\`\`\`

\---

\#\# 📝 Versão da Documentação

\- \*\*Versão\*\*: 1.0  
\- \*\*Data\*\*: Dezembro 2024  
\- \*\*Status\*\*: Documentação Completa e Validada  
\- \*\*Compatibilidade\*\*: Python 3.7+

\---

\*\*Desenvolvido para Vibecoding \- Documentação Profissional para Desenvolvimento Orientado por IA\*\*  
