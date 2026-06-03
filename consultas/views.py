from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Profissional, Consulta
from .serializers import ProfissionalSerializer, ConsultaSerializer
from .services import AsaasService

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_with_author = ProfissionalSerializer
    
    def get_serializer_class(self):
        return ProfissionalSerializer

    @action(detail=True, methods=['get'])
    def consultas(self, request, pk=None):
        profissional = self.get_object()
        consultas = profissional.consultas.all()
        serializer = ConsultaSerializer(consultas, many=True)
        return Response(serializer.data)

class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer

    def perform_create(self, serializer):
        # 1. Salva a consulta no banco de dados local
        consulta = serializer.save()
        
        # 2. Dispara a criação da cobrança de forma transparente no Asaas
        asaas_service = AsaasService()
        id_faturamento = asaas_service.criar_cobranca_consulta(consulta)
        
        # 3. Atualiza a consulta com o ID retornado pelo gateway de pagamento
        consulta.asaas_id = id_faturamento
        consulta.save()


# === WEBHOOK DA INTEGRAÇÃO COM O ASAAS ===

@api_view(['POST'])
@permission_classes([AllowAny]) # CRÍTICO: Permite que o servidor do Asaas acesse sem o cabeçalho JWT da API
def asaas_webhook(request):
    """
    Recebe as notificações de eventos de pagamento enviados pelo Asaas.
    """
    evento = request.data.get("event")
    payment_data = request.data.get("payment", {})
    id_pagamento_asaas = payment_data.get("id")

    print(f"[ASAAS WEBHOOK] Evento '{evento}' recebido para o pagamento {id_pagamento_asaas}")

    # Evento enviado pelo Asaas quando o Pix ou Cartão é compensado
    if evento == "PAYMENT_RECEIVED":
        try:
            consulta = Consulta.objects.get(asaas_id=id_pagamento_asaas)
            consulta.status_pagamento = 'PAGO'
            consulta.save()
            return Response({"status": "Sucesso. Consulta atualizada para PAGO."}, status=status.HTTP_200_OK)
        except Consulta.DoesNotExist:
            return Response({"error": "Identificador de pagamento inválido ou não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Retorna sucesso para outros eventos não tratados (ex: PAYMENT_CREATED) para o Asaas saber que recebemos o sinal
    return Response({"status": "Evento processado."}, status=status.HTTP_200_OK)