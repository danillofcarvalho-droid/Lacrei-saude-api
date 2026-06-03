from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta
from .models import Profissional, Consulta

class LacreiSaudeAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Cria um profissional padrão no banco de dados para usarmos nos testes de consultas
        self.profissional_padrao = Profissional.objects.create(
            nome_social="Dr. Alex Silva",
            profissao="Psicólogo",
            endereco="Rua das Flores, 123",
            contato="11999999999"
        )
        
        # URLs dos endpoints usando o 'reverse' do Django (busca pelo 'name' da rota)
        self.url_profissionais = reverse('profissional-list')
        self.url_consultas = reverse('consulta-list')

    # === TESTES DE SUCESSO (HAPPY PATH) ===

    def test_criar_profissional_com_sucesso(self):
        """Garante que um profissional é criado com sucesso quando autenticado"""
        self.client.force_authenticate(user=self.user) # Autentica o cliente
        dados = {
            "nome_social": "Dra. Morgana",
            "profissao": "Cardiologista",
            "endereco": "Av. Central, 456",
            "contato": "61988888888"
        }
        response = self.client.post(self.url_profissionais, dados, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profissional.objects.count(), 2) # O padrão + o novo

    def test_criar_consulta_com_sucesso(self):
        """Garante que uma consulta é agendada com sucesso no futuro"""
        self.client.force_authenticate(user=self.user)
        data_futura = timezone.now() + timedelta(days=2)
        dados = {
            "data": data_futura,
            "profissional": self.profissional_padrao.id
        }
        response = self.client.post(self.url_consultas, dados, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_buscar_consultas_por_id_do_profissional(self):
        self.client.force_authenticate(user=self.user)
        
        # Cria uma consulta para o profissional padrão
        Consulta.objects.create(data=timezone.now() + timedelta(days=1), profissional=self.profissional_padrao)
        
        # Monta a URL: /api/profissionais/{id}/consultas/
        url_customizada = reverse('profissional-consultas', kwargs={'pk': self.profissional_padrao.id})
        
        response = self.client.get(url_customizada)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Deve retornar exatamente 1 consulta

    # === TESTES DE ERRO E VALIDAÇÃO (EDGE CASES) ===

    def test_requisicao_sem_autenticacao_deve_falhar(self):
        """(Teste de Segurança - barrar requisições anônimas)"""
        response = self.client.get(self.url_profissionais)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_criar_profissional_com_dados_ausentes_deve_falhar(self):
        """Garante que a API rejeita dados incompletos"""
        self.client.force_authenticate(user=self.user)
        dados_incompletos = {
            "nome_social": "Dr. Sem Profissão"
            # Faltando profissão, endereço e contato
        }
        response = self.client.post(self.url_profissionais, dados_incompletos, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_consulta_no_passado_deve_falhar(self):
        """Garante que a regra de negócio do Serializer barra datas passadas"""
        self.client.force_authenticate(user=self.user)
        data_passada = timezone.now() - timedelta(days=1) # Ontem
        dados = {
            "data": data_passada,
            "profissional": self.profissional_padrao.id
        }
        response = self.client.post(self.url_consultas, dados, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("A data e hora da consulta não podem ser no passado.", response.data['data'])