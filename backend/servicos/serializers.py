from rest_framework import serializers
from .models import Solicitacao, Proposta, Pagamento


class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = ['id', 'status', 'atualizado_em']
        read_only_fields = ['id', 'status', 'atualizado_em']


class PropostaSerializer(serializers.ModelSerializer):
    # OneToOneField reverso: traz o pagamento aninhado se existir (ou null)
    pagamento = PagamentoSerializer(read_only=True)

    class Meta:
        model = Proposta
        fields = ['id', 'solicitacao', 'valor', 'validade', 'status', 'pagamento']
        read_only_fields = ['id', 'status', 'pagamento']

    def validate(self, data):
        solicitacao = data.get('solicitacao')
        if solicitacao and solicitacao.status != Solicitacao.Status.ABERTA:
            raise serializers.ValidationError(
                "Não é possível enviar propostas para uma solicitação que não está ABERTA."
            )
        return data


class SolicitacaoSerializer(serializers.ModelSerializer):
    # Many-to-One reverso: lista todas as propostas desta solicitação
    propostas = PropostaSerializer(many=True, read_only=True)

    class Meta:
        model = Solicitacao
        fields = [
            'id',
            'empresa',
            'servico_desejado',
            'status',
            'criado_em',
            'propostas',
        ]
        read_only_fields = ['id', 'status', 'criado_em', 'propostas']