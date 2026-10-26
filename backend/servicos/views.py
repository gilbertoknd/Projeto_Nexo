from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Solicitacao, Proposta, Pagamento
from .serializers import SolicitacaoSerializer, PropostaSerializer
from .tasks import confirmar_pagamento


class SolicitacaoViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Permite criar (POST) e listar (GET) solicitações já trazendo propostas e pagamentos.
    """
    queryset = (
        Solicitacao.objects
        .prefetch_related('propostas__pagamento')
        .order_by('-criado_em')
    )
    serializer_class = SolicitacaoSerializer


class PropostaViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Permite enviar proposta (POST /api/propostas/) e aceitar proposta (POST /api/propostas/{id}/aceitar/).
    """
    queryset = Proposta.objects.select_related('solicitacao', 'pagamento').all()
    serializer_class = PropostaSerializer

    @action(detail=True, methods=['post'])
    def aceitar(self, request, pk=None):
        with transaction.atomic():
            # Bloqueia a linha da proposta e da solicitação até o fim da transação
            try:
                proposta = (
                    Proposta.objects
                    .select_for_update()
                    .select_related('solicitacao')
                    .get(pk=pk)
                )
            except Proposta.DoesNotExist:
                return Response(
                    {"detail": "Proposta não encontrada."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if proposta.solicitacao.status != Solicitacao.Status.ABERTA:
                return Response(
                    {"detail": "Esta solicitação já foi contratada ou encerrada."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if proposta.status != Proposta.Status.ENVIADA:
                return Response(
                    {"detail": f"Proposta não pode ser aceita (status atual: {proposta.status})."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 1. Atualiza o status da proposta para ACEITA
            proposta.status = Proposta.Status.ACEITA
            proposta.save(update_fields=['status'])

            # 2. Cria (ou recupera, por segurança) o registro de Pagamento PENDENTE
            pagamento, _ = Pagamento.objects.get_or_create(
                proposta=proposta,
                defaults={'status': Pagamento.Status.PENDENTE}
            )

            # 3. Só envia a mensagem para o RabbitMQ após o COMMIT no PostgreSQL
            transaction.on_commit(lambda: confirmar_pagamento.delay(pagamento.id))

        return Response(
            {
                "pagamento_id": pagamento.id,
                "proposta_id": proposta.id,
                "status": pagamento.status,
            },
            status=status.HTTP_200_OK
        )