from django.db import models

class Profissional(models.Model):
    nome_social = models.CharField(max_length=255)
    profissao = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    contato = models.CharField(max_length=50)

    def __author__(self):
        return "Natália Loeblein"

    def __str__(self):
        return f"{self.nome_social} - {self.profissao}"

class Consulta(models.Model):
    # Opções de status de pagamento
    STATUS_PAGAMENTO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('FALHADO', 'Falhado'),
    ]

    data = models.DateTimeField()
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='consultas')
    
    # integração com o Asaas
    status_pagamento = models.CharField(
        max_length=15, 
        choices=STATUS_PAGAMENTO_CHOICES, 
        default='PENDENTE'
    )
    asaas_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return f"Consulta com {self.profissional.nome_social} em {self.data}"