from django.db import models

class Solicitacao(models.Model):
    class Status(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        CONTRATADA = 'CONTRATADA', 'Contratada'
        ENCERRADA = 'ENCERRADA', 'Encerrada'

    empresa = models.CharField(max_length=150)
    servico_desejado = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTA
    )
    criado_em = models.DateTimeField(auto_now_add=True) # Essencial para o job de 7 dias!

class Proposta(models.Model):
    class Status(models.TextChoices):
        ENVIADA = 'ENVIADA', 'Enviada'
        ACEITA = 'ACEITA', 'Aceita'
        EXPIRADA = 'EXPIRADA', 'Expirada'

    solicitacao = models.ForeignKey(
        Solicitacao,
        on_delete=models.CASCADE,
        related_name='propostas'
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    validade = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENVIADA
    )

class Pagamento(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        FALHOU = 'FALHOU', 'Falhou'

    proposta = models.OneToOneField(
        Proposta,
        on_delete=models.CASCADE,
        related_name='pagamento'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )
    atualizado_em = models.DateTimeField(auto_now=True)