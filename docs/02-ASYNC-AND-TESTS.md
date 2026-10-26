# 02. Processamento Assíncrono (Celery) e Testes (Pytest)

## 1. Tasks em `servicos/tasks.py`
1. **`consultar_gateway_externo()`**: Função auxiliar isolada que simula falha aleatória levantando `ConnectionError` (facilita mock nos testes).
2. **`confirmar_pagamento(self, pagamento_id)`**:
   - Decorador: `@shared_task(bind=True, max_retries=3, default_retry_delay=5)`
   - Chama `consultar_gateway_externo()`.
   - Se falhar: chama `raise self.retry(exc=exc)`.
   - Captura `MaxRetriesExceededError`: muda `pagamento.status = 'FALHOU'` e salva.
   - Se tiver sucesso: dentro de `transaction.atomic()`, muda `pagamento.status = 'CONFIRMADO'` e `solicitacao.status = 'CONTRATADA'`.
3. **`expirar_propostas_vencidas()`**:
   - Atualiza propostas com `status='ENVIADA'` e `validade__lt=timezone.localdate()` para `EXPIRADA`.
4. **`encerrar_solicitacoes_sem_proposta()`**:
   - Atualiza solicitações com `status='ABERTA'`, `criado_em__lte=timezone.now() - timedelta(days=7)` e `propostas__isnull=True` para `ENCERRADA`.

## 2. Agendamento em `config/celery.py` (Celery Beat)
- `expirar_propostas_vencidas`: `crontab(hour=0, minute=0)`
- `encerrar_solicitacoes_sem_proposta`: `crontab(hour=1, minute=0)`

## 3. Requisitos de Teste (`servicos/tests/test_tasks.py`)
- Usar `pytest` e `@pytest.mark.django_db`.
- Mockar `servicos.tasks.consultar_gateway_externo` com `unittest.mock.patch`.
- Testar os 4 cenários: confirmação de pagamento, esgotamento de retries virando `FALHOU`, expiração de propostas vencidas e encerramento de solicitações após 7 dias sem propostas.