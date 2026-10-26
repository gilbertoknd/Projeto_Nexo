import random
from datetime import timedelta
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.db import transaction
from .models import Solicitacao, Proposta, Pagamento

def consultar_gateway_externo():
    """Função isolada (facilita o mock no pytest!) que simula instabilidade."""
    if random.random() < 0.6:  # 60% de chance de falhar para testar o retry
        raise ConnectionError("Timeout no banco externo")
    return True

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def confirmar_pagamento(self, pagamento_id: int):
    pagamento = Pagamento.objects.select_related('proposta__solicitacao').get(id=pagamento_id)

    # Guard de idempotência: se já foi processado, não faz nada
    if pagamento.status == Pagamento.Status.CONFIRMADO:
        return "Já confirmado"

    try:
        consultar_gateway_externo()
    except Exception as exc:
        try:
            if self.request.retries >= self.max_retries:
                raise MaxRetriesExceededError("Número máximo de tentativas excedido")
            # Tenta reenfileirar a task
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            # Esgotou as 3 tentativas! Marca como FALHOU.
            pagamento.status = Pagamento.Status.FALHOU
            pagamento.save(update_fields=['status', 'atualizado_em'])
            return "Falhou após todas as tentativas"

    # Se passou sem exceção, confirma pagamento e contrata solicitação atomicamente
    with transaction.atomic():
        pagamento.status = Pagamento.Status.CONFIRMADO
        pagamento.save(update_fields=['status', 'atualizado_em'])

        solicitacao = pagamento.proposta.solicitacao
        solicitacao.status = Solicitacao.Status.CONTRATADA
        solicitacao.save(update_fields=['status'])

    return "Confirmado com sucesso"

@shared_task
def expirar_propostas_vencidas():
    hoje = timezone.localdate()
    atualizadas = Proposta.objects.filter(
        status=Proposta.Status.ENVIADA,
        validade__lt=hoje
    ).update(status=Proposta.Status.EXPIRADA)
    return atualizadas

@shared_task
def encerrar_solicitacoes_sem_proposta():
    limite = timezone.now() - timedelta(days=7)
    atualizadas = Solicitacao.objects.filter(
        status=Solicitacao.Status.ABERTA,
        criado_em__lte=limite,
        propostas__isnull=True
    ).update(status=Solicitacao.Status.ENCERRADA)
    return atualizadas