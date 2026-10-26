import pytest
from datetime import timedelta
from django.utils import timezone
from unittest.mock import patch
from celery.exceptions import Retry
from servicos.models import Solicitacao, Proposta, Pagamento
from servicos.tasks import (
    confirmar_pagamento,
    expirar_propostas_vencidas,
    encerrar_solicitacoes_sem_proposta,
)


@pytest.mark.django_db
def test_confirmar_pagamento_sucesso():
    solicitacao = Solicitacao.objects.create(empresa="Tech Corp", servico_desejado="Dev Web")
    proposta = Proposta.objects.create(
        solicitacao=solicitacao, valor=5000, validade=timezone.localdate() + timedelta(days=5), status=Proposta.Status.ACEITA
    )
    pagamento = Pagamento.objects.create(proposta=proposta, status=Pagamento.Status.PENDENTE)

    with patch("servicos.tasks.consultar_gateway_externo", return_value=True):
        confirmar_pagamento(pagamento.id)

    pagamento.refresh_from_db()
    solicitacao.refresh_from_db()
    assert pagamento.status == Pagamento.Status.CONFIRMADO
    assert solicitacao.status == Solicitacao.Status.CONTRATADA


@pytest.mark.django_db
def test_confirmar_pagamento_falha_apos_retries():
    solicitacao = Solicitacao.objects.create(empresa="Tech Corp", servico_desejado="Dev Web")
    proposta = Proposta.objects.create(
        solicitacao=solicitacao, valor=5000, validade=timezone.localdate() + timedelta(days=5), status=Proposta.Status.ACEITA
    )
    pagamento = Pagamento.objects.create(proposta=proposta, status=Pagamento.Status.PENDENTE)

    # Simula que já estamos na última tentativa (retries=3 de max_retries=3)
    with patch("servicos.tasks.consultar_gateway_externo", side_effect=ConnectionError("Banco fora do ar")):
        confirmar_pagamento.push_request(retries=3)
        try:
            confirmar_pagamento(pagamento.id)
        finally:
            confirmar_pagamento.pop_request()

    pagamento.refresh_from_db()
    solicitacao.refresh_from_db()
    assert pagamento.status == Pagamento.Status.FALHOU
    assert solicitacao.status == Solicitacao.Status.ABERTA


@pytest.mark.django_db
def test_expirar_propostas_vencidas():
    solicitacao = Solicitacao.objects.create(empresa="Empresa A", servico_desejado="Consultoria")
    ontem = timezone.localdate() - timedelta(days=1)
    amanha = timezone.localdate() + timedelta(days=1)

    p_vencida = Proposta.objects.create(solicitacao=solicitacao, valor=1000, validade=ontem)
    p_valida = Proposta.objects.create(solicitacao=solicitacao, valor=2000, validade=amanha)

    expirar_propostas_vencidas()

    p_vencida.refresh_from_db()
    p_valida.refresh_from_db()
    assert p_vencida.status == Proposta.Status.EXPIRADA
    assert p_valida.status == Proposta.Status.ENVIADA


@pytest.mark.django_db
def test_encerrar_solicitacoes_sem_proposta_7_dias():
    s_antiga = Solicitacao.objects.create(empresa="Antiga", servico_desejado="Design")
    # Força a data de criação para 8 dias atrás no banco
    Solicitacao.objects.filter(id=s_antiga.id).update(criado_em=timezone.now() - timedelta(days=8))

    s_recente = Solicitacao.objects.create(empresa="Recente", servico_desejado="SEO")

    encerrar_solicitacoes_sem_proposta()

    s_antiga.refresh_from_db()
    s_recente.refresh_from_db()
    assert s_antiga.status == Solicitacao.Status.ENCERRADA
    assert s_recente.status == Solicitacao.Status.ABERTA
