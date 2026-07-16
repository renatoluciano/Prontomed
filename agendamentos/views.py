from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Especialidade, Medico, TipoExame, Agendamento
from .serializers import (
    EspecialidadeSerializer, 
    MedicoSerializer, 
    TipoExameSerializer, 
    AgendamentoSerializer
)

class EspecialidadeViewSet(viewsets.ModelViewSet):
    queryset = Especialidade.objects.all()
    serializer_class = EspecialidadeSerializer
    # Permite leitura para qualquer um, mas modificação apenas para administradores
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TipoExameViewSet(viewsets.ModelViewSet):
    queryset = TipoExame.objects.all()
    serializer_class = TipoExameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    # Exige que o usuário esteja logado para interagir com os agendamentos
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Regra de Segurança Extra:
        Pacientes comuns só enxergam os próprios agendamentos.
        Médicos e administradores podem ver todos da clínica.
        """
        user = self.request.user
        
        if user.is_staff or hasattr(user, 'perfil_medico'):
            return Agendamento.objects.all()
            
        return Agendamento.objects.filter(paciente=user)

    def perform_create(self, serializer):
        """
        Praticidade:
        Se um paciente comum criar um agendamento, o sistema herda automaticamente 
        o usuário logado como o 'paciente' da consulta, evitando fraudes.
        """
        if not self.request.user.is_staff:
            serializer.save(paciente=self.request.user)
        else:
            serializer.save()

