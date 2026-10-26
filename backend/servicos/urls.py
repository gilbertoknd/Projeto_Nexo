from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitacaoViewSet, PropostaViewSet

router = DefaultRouter()
router.register(r'solicitacoes', SolicitacaoViewSet, basename='solicitacao')
router.register(r'propostas', PropostaViewSet, basename='proposta')

urlpatterns = [
    path('', include(router.urls)),
]
