import uuid

class AsaasService:
    def __init__(self):

        self.api_url = "https://sandbox.asaas.com/api/v3/payments"
        self.api_key = "$asaas_secret_key_exemplo"

    def criar_cobranca_consulta(self, consulta):
        """
        Simula o envio da cobrança para o Asaas (Pix/Cartão).
        Retorna o ID da transação gerado pelo gateway.
        """
        # Exemplo de payload que seria enviado usando 'requests.post'
        payload = {
            "customer": "cus_0000012345", # Id do cliente simulado
            "billingType": "PIX",
            "value": 150.00, # Valor fictício da consulta
            "dueDate": consulta.data.strftime("%Y-%m-%d"),
            "externalReference": f"CONSULTA_{consulta.id}"
        }
        
        # Simulando uma resposta de sucesso HTTP 200 do Asaas
        # Cria um ID único com o prefixo real do Asaas ('pay_')
        id_transacao_asaas = f"pay_{uuid.uuid4().hex[:12].upper()}"
        
        print(f"[ASAAS LOG] Cobrança {id_transacao_asaas} gerada com sucesso para a Consulta {consulta.id}.")
        return id_transacao_asaas