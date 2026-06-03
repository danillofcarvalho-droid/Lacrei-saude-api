from rest_framework import serializers
from .models import Profissional, Consulta
from django.utils import timezone

class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = '__all__'


class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = '__all__'

    # Regra de Negócio / Validação de Segurança
    def validate_data(self, value):
        """
        Garante que ninguém consiga agendar uma consulta com uma data que já passou.
        O Django procura automaticamente por métodos que começam com 'validate_<nome_do_campo>'.
        """
        if value < timezone.now():
            raise serializers.ValidationError("A data e hora da consulta não podem ser no passado.")
        return value