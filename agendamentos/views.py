from rest_framework.decorators import action  
from rest_framework.response import Response  
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

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ADICIONE ESTE MÉTODO ABAIXO DENTRO DA CLASSE MEDICOVIEWSET
    @action(detail=True, methods=['get'], url_path='horarios-disponiveis')
    def horarios_disponiveis(self, request, pk=None):
        """
        Devolve uma lista de horários livres para o médico na data especificada.
        Exemplo de uso: /api/medicos/1/horarios-disponiveis/?data=2026-08-20
        """
        medico = self.get_object()
        data_param = request.query_params.get('data')

        if not data_param:
            return Response({"error": "O parâmetro 'data' no formato AAAA-MM-DD é obrigatório."}, status=400)

        try:
            # Valida se a data enviada está no formato correto
            data_selecionada = datetime.strptime(data_param, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=400)

        # 1. Pega todos os horários possíveis cadastrados no nosso Model
        todos_horarios = [opcao[0] for opcao in Agendamento.HORARIOS_CHOICES]

        # 2. Busca no banco quais horários já estão ocupados para esse médico nessa data
        horarios_ocupados = Agendamento.objects.filter(
            medico=medico,
            data=data_selecionada
        ).values_list('horario', flat=True)

        # 3. Filtra a lista mantendo apenas o que não está ocupado
        horarios_livres = [h for h in todos_horarios if h not in horarios_ocupados]

        return Response({
            "medico": medico.usuario.get_full_name() or medico.usuario.username,
            "data": data_param,
            "horarios_disponiveis": horarios_livres
        })