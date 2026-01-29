#!/usr/bin/env python3
"""
Cron para envio automático de convites do LinkedIn.
Executa diariamente às 07:00 (horário de São Paulo) e processa todos os 
invite_schedules pendentes do dia.

Uso manual:
    python projeto_linkedin/cron_invites.py

Via Docker (ver docker-compose.cron.yml):
    O container executa automaticamente às 07h todos os dias.

Variáveis de ambiente necessárias:
    - SUPABASE_URL: URL do projeto Supabase
    - SUPABASE_SERVICE_KEY: Service Role Key do Supabase (para bypass de RLS)
    - INVITE_DAILY_LIMIT: Limite de convites por dia (default: 100)
    - INVITE_DELAY_MIN: Delay mínimo entre convites em segundos (default: 1.0)
    - INVITE_DELAY_MAX: Delay máximo entre convites em segundos (default: 3.0)
    - UNIPILE_BASE_URL: URL base da API Unipile (default: https://api26.unipile.com:15609)
"""

import os
import sys
import time
import random
import logging
from datetime import datetime, date, timedelta
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from supabase import create_client
from unipile_client import UnipileClient

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuração via variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
INVITE_DAILY_LIMIT = int(os.getenv("INVITE_DAILY_LIMIT", "40")) # Limite seguro inicial
INVITE_WEEKLY_LIMIT = int(os.getenv("INVITE_WEEKLY_LIMIT", "190")) # Limite semanal seguro
INVITE_DELAY_MIN = float(os.getenv("INVITE_DELAY_MIN", "300.0")) # 5 minutos
INVITE_DELAY_MAX = float(os.getenv("INVITE_DELAY_MAX", "900.0")) # 15 minutos
UNIPILE_BASE_URL = os.getenv("UNIPILE_BASE_URL", "https://api26.unipile.com:15609")


def validate_config():
    """Valida se todas as variáveis de ambiente necessárias estão configuradas."""
    if not SUPABASE_URL:
        logger.error("SUPABASE_URL não configurada!")
        return False
    if not SUPABASE_SERVICE_KEY:
        logger.error("SUPABASE_SERVICE_KEY não configurada!")
        return False
    return True


def get_pending_schedules(supabase, today: str, limit: int):
    """
    Busca todos os agendamentos pendentes para o dia atual.
    Usa JOIN com unipile_accounts para obter as credenciais.
    """
    try:
        # Busca schedules com status 'scheduled' para hoje
        # Inclui dados da conta Unipile via FK
        result = supabase.table("invite_schedules") \
            .select("*, unipile_accounts(id, account_id, api_key, label)") \
            .eq("scheduled_date", today) \
            .eq("status", "scheduled") \
            .limit(limit) \
            .execute()
        
        return result.data or []
    except Exception as e:
        logger.error(f"Erro ao buscar agendamentos: {e}")
        return []


def check_weekly_limit(supabase):
    """
    Verifica se o limite semanal de convites foi atingido.
    Retorna True se o limite foi atingido, False caso contrário.
    """
    try:
        # Data de 7 dias atrás
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        # Conta convites enviados nos últimos 7 dias
        count_result = supabase.table("invite_schedules") \
            .select("id", count="exact") \
            .gte("sent_at", seven_days_ago) \
            .eq("status", "sent") \
            .execute()
        
        total_sent = count_result.count
        
        logger.info(f"Verificando limite semanal... enviadas nos últimos 7 dias: {total_sent}/{INVITE_WEEKLY_LIMIT}")
        
        if total_sent >= INVITE_WEEKLY_LIMIT:
            logger.warning(f"⚠️ LIMITE SEMANAL ATINGIDO ({total_sent}/{INVITE_WEEKLY_LIMIT}). Convites pausados temporariamente.")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar limite semanal: {e}")
        return False # Em caso de erro, permite continuar para não travar por bugs de consulta


def send_invitation(unipile: UnipileClient, account_id: str, provider_id: str, message: str = None):
    """
    Envia um convite de conexão via Unipile API.
    Retorna (success, result, is_already_connected)
    """
    try:
        result = unipile.send_invitation(
            account_id=account_id,
            identifier=provider_id,
            message=message
        )
        
        if result is None:
             raise Exception("Falha na API Unipile (Rate Limit ou Timeout)")
             
        return True, result, False
    except Exception as e:
        error_details = str(e)
        
        # Tenta extrair detalhes da resposta se houver
        if hasattr(e, 'response') and e.response is not None:
             try:
                 err_json = e.response.json()
                 
                 # Lógica para tratamento de "Já conectado"
                 err_type = err_json.get('type', '')
                 err_msg = err_json.get('message', '').lower()
                 err_detail = err_json.get('detail', '').lower()
                 
                 # Lista de erros que consideramos como "Sucesso/Resolvido"
                 if (
                     "already_connected" in err_type or 
                     "already connected" in err_detail or
                     "pending" in err_msg or
                     "already pending" in err_msg
                 ):
                     logger.info(f"  ℹ️ Lead {provider_id} já conectado ou pendente. Marcando como enviado.")
                     return True, {"id": "ALREADY_CONNECTED"}, True
                 
                 # Se não for caso de sucesso, salva o JSON completo para debug
                 error_details = f"Status: {e.response.status_code} | Body: {err_json}"
                 
             except ValueError:
                 # Se não for JSON, pega o texto puro
                 error_details = f"Status: {e.response.status_code} | Body: {e.response.text}"
             except Exception:
                 pass
                 
        return False, error_details, False


def update_schedule_status(supabase, schedule_id: str, status: str, **kwargs):
    """
    Atualiza o status de um agendamento.
    """
    try:
        update_data = {"status": status}
        
        if status == "sent":
            update_data["sent_at"] = datetime.utcnow().isoformat()
        
        if "invitation_id" in kwargs:
            update_data["invitation_id"] = kwargs["invitation_id"]
        
        if "error_message" in kwargs:
            update_data["error_message"] = kwargs["error_message"]
        
        supabase.table("invite_schedules") \
            .update(update_data) \
            .eq("id", schedule_id) \
            .execute()
        
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        return False


def process_schedules():
    """
    Processa todos os agendamentos pendentes do dia.
    """
    if not validate_config():
        return False
    
    # Conecta ao Supabase com Service Key (bypass RLS)
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # Data de hoje
    today = date.today().isoformat()
    logger.info(f"Iniciando processamento de convites para {today}")
    
    # Valida limite semanal ANTES de buscar novos
    if check_weekly_limit(supabase):
        logger.info("❌ Abortando processamento de hoje devido ao limite semanal.")
        return True
    
    # Busca agendamentos pendentes
    schedules = get_pending_schedules(supabase, today, INVITE_DAILY_LIMIT)
    
    if not schedules:
        logger.info("Nenhum convite agendado para hoje.")
        return True
    
    logger.info(f"Encontrados {len(schedules)} convites para processar")
    logger.info(f"Delay programado: {INVITE_DELAY_MIN/60:.1f} a {INVITE_DELAY_MAX/60:.1f} minutos entre envios")
    
    # Processa cada agendamento
    sent_count = 0
    error_count = 0
    consecutive_errors = 0
    
    # Cache de clientes Unipile por account_id
    unipile_clients = {}
    
    for schedule in schedules:
        try:
            # Obtém dados da conta Unipile
            account_data = schedule.get("unipile_accounts")
            if not account_data:
                logger.warning(f"Schedule {schedule['id']}: conta Unipile não encontrada")
                update_schedule_status(
                    supabase, 
                    schedule["id"], 
                    "error",
                    error_message="Conta Unipile não encontrada"
                )
                error_count += 1
                consecutive_errors += 1
                continue
            
            account_id = account_data["account_id"]
            api_key = account_data["api_key"]
            
            # Cria ou reutiliza cliente Unipile
            if account_id not in unipile_clients:
                unipile_clients[account_id] = UnipileClient(UNIPILE_BASE_URL, api_key)
            
            unipile = unipile_clients[account_id]
            provider_id = schedule["provider_id"]
            message = schedule.get("message")
            
            logger.info(f"Processando {provider_id}...")
            
            # Envia convite
            success, result, already_connected = send_invitation(unipile, account_id, provider_id, message)
            
            if success:
                consecutive_errors = 0 # Reseta contador de erros
                invitation_id = result.get("id") if isinstance(result, dict) else None
                
                # Se for already connected, podemos usar um status diferente ou apenas 'sent' com log
                error_message = "Lead já era conexão ou pendente." if already_connected else None
                
                update_schedule_status(
                    supabase,
                    schedule["id"],
                    "sent",
                    invitation_id=invitation_id,
                    error_message=error_message
                )
                sent_count += 1
                logger.info(f"  ✅ Enviado{' (Já conectado)' if already_connected else ''}: {provider_id}")
            else:
                error_msg_str = str(result)
                update_schedule_status(
                    supabase,
                    schedule["id"],
                    "error",
                    error_message=error_msg_str
                )
                error_count += 1
                consecutive_errors += 1
                logger.error(f"  ❌ Erro: {provider_id} - {error_msg_str}")
                
                # ==== Lógica de Segurança ====
                should_break = False
                
                if "Status: 500" in error_msg_str:
                    logger.critical("⛔ Erro 500 detectado (Automação/LinkedIn Instável). Parando por segurança.")
                    should_break = True
                elif "Status: 429" in error_msg_str or "rate limit" in error_msg_str.lower():
                    logger.critical("⛔ Rate Limit detectado. Parando por segurança.")
                    should_break = True
                elif consecutive_errors >= 3:
                    logger.critical(f"⛔ {consecutive_errors} erros consecutivos. Parando por segurança.")
                    should_break = True
                    
                if should_break:
                    break
            
            # Delay aleatório entre convites
            delay = random.uniform(INVITE_DELAY_MIN, INVITE_DELAY_MAX)
            logger.info(f"  ⏳ Aguardando {delay:.1f}s...")
            time.sleep(delay)
            
        except Exception as e:
            logger.error(f"Erro ao processar schedule {schedule.get('id')}: {e}")
            update_schedule_status(
                supabase,
                schedule["id"],
                "error",
                error_message=str(e)
            )
            error_count += 1
            consecutive_errors += 1
            
            if consecutive_errors >= 3:
                logger.critical("⛔ Erros inesperados consecutivos. Abortando.")
                break
    
    # Resumo
    logger.info("=" * 50)
    logger.info(f"Processamento concluído!")
    logger.info(f"  Total processados: {len(schedules)}")
    logger.info(f"  Enviados com sucesso: {sent_count}")
    logger.info(f"  Erros: {error_count}")
    logger.info("=" * 50)
    
    return error_count == 0


def main():
    """
    Função principal do cron.
    """
    logger.info("=" * 50)
    logger.info("CRON DE CONVITES - LinkedIn Prospect SDR Tool")
    logger.info(f"Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Limite diário: {INVITE_DAILY_LIMIT}")
    logger.info(f"Delay: {INVITE_DELAY_MIN}s - {INVITE_DELAY_MAX}s")
    logger.info("=" * 50)
    
    success = process_schedules()
    
    if success:
        logger.info("Cron finalizado com sucesso!")
        sys.exit(0)
    else:
        logger.error("Cron finalizado com erros!")
        sys.exit(1)


if __name__ == "__main__":
    main()
