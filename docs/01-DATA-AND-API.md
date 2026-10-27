# 01. Modelagem de Dados e Contratos de API

## 1. Models (`servicos/models.py`)
- **Solicitacao**
  - `empresa`: CharField(max_length=150)
  - `servico_desejado`: TextField()
  - `status`: TextChoices (`ABERTA`, `CONTRATADA`, `ENCERRADA`), default=`ABERTA`
  - `criado_em`: DateTimeField(auto_now_add=True)
- **Proposta**
  - `solicitacao`: ForeignKey(Solicitacao, related_name=`propostas`, on_delete=CASCADE)
  - `valor`: DecimalField(max_digits=10, decimal_places=2)
  - `validade`: DateField()
  - `status`: TextChoices (`ENVIADA`, `ACEITA`, `EXPIRADA`), default=`ENVIADA`
- **Pagamento**
  - `proposta`: OneToOneField(Proposta, related_name=`pagamento`, on_delete=CASCADE)
  - `status`: TextChoices (`PENDENTE`, `CONFIRMADO`, `FALHOU`), default=`PENDENTE`
  - `atualizado_em`: DateTimeField(auto_now=True)

## 2. Endpoints e Payloads Exatos (DRF)
### `GET /api/solicitacoes/`
Retorna lista de solicitações com propostas e pagamento aninhados:
```json
[
  {
    "id": 1,
    "empresa": "Acme Corp",
    "servico_desejado": "Desenvolvimento de API",
    "status": "ABERTA",
    "criado_em": "2026-10-26T12:00:00Z",
    "propostas": [
      {
        "id": 10,
        "valor": "4500.00",
        "validade": "2026-11-05",
        "status": "ENVIADA",
        "pagamento": {
          "id": 100,
          "status": "PENDENTE"
        }
      }
    ]
  }
]

POST /api/solicitacoes/
Request: {"empresa": "string", "servico_desejado": "string"}

POST /api/propostas/
Request: {"solicitacao": 1, "valor": "4500.00", "validade": "2026-11-05"}

POST /api/propostas/{id}/aceitar/
Sem body. Altera Proposta para ACEITA, cria Pagamento PENDENTE, agenda task via transaction.on_commit e retorna {"pagamento_id": 100, "status": "PENDENTE"}.