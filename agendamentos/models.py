from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Medico(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_medico')
    crm = models.CharField(max_length=20, unique=True)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.PROTECT, related_name='medicos')
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.get_full_name() or self.usuario.username} ({self.crm})"

class TipoExame(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    instrucoes_preparo = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Agendamento(models.Model):
    TIPO_CHOICES = [
        ('CONSULTA', 'Consulta Inicial'),
        ('EXAME', 'Exame Prescrito'),
        ('RETORNO', 'Retorno Médico'),
    ]

    HORARIOS_CHOICES = [
        ('08:00', '08:00'), ('08:30', '08:30'),
        ('09:00', '09:00'), ('09:30', '09:30'),
        ('10:00', '10:00'), ('10:30', '10:30'),
        ('11:00', '11:00'), ('11:30', '11:30'),
        ('14:00', '14:00'), ('14:30', '14:30'),
        ('15:00', '15:00'), ('15:30', '15:30'),
        ('16:00', '16:00'), ('16:30', '16:30'),
    ]

    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meus_agendamentos')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    data = models.DateField()
    horario = models.CharField(max_length=5, choices=HORARIOS_CHOICES)
    
    # Campos condicionais baseados no tipo de agendamento
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='agenda', blank=True, null=True)
    tipo_exame = models.ForeignKey(TipoExame, on_delete=models.CASCADE, blank=True, null=True)
    
    # Auto-relacionamento: Vincula o Retorno de volta à Consulta Inicial
    consulta_original = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='retornos')
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evita choque: mesmo médico, no mesmo dia e horário
        unique_together = ('medico', 'data', 'horario')

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.paciente.username} em {self.data} às {self.horario}"

    def clean(self):
        # 1. Bloqueia agendamentos retroativos
        if self.data < timezone.now().date():
            raise ValidationError("Não é possível agendar datas no passado.")

        # 2. Validações para Exames
        if self.tipo == 'EXAME':
            if not self.tipo_exame:
                raise ValidationError("É obrigatório selecionar o Tipo de Exame.")
            self.medico = None # Exames não ocupam agenda de médicos específicos nesta regra

        # 3. Validações para Consultas e Retornos
        if self.tipo in ['CONSULTA', 'RETORNO']:
            if not self.medico:
                raise ValidationError("É obrigatório selecionar um Médico.")
            self.tipo_exame = None

        # 4. Regra de Negócio de Ouro: Validação do Retorno (Prazo de 30 dias)
        if self.tipo == 'RETORNO':
            if not self.consulta_original:
                raise ValidationError("Para marcar um retorno, é obrigatório vincular a Consulta Inicial original.")
            
            if self.consulta_original.tipo != 'CONSULTA':
                raise ValidationError("O agendamento de origem precisa ser do tipo 'Consulta Inicial'.")
                
            if self.consulta_original.paciente != self.paciente:
                raise ValidationError("A consulta original selecionada pertence a outro paciente.")

            # Verifica se estourou o prazo limite de 30 dias corridos
            prazo_limite = self.consulta_original.data + timedelta(days=30)
            if self.data > prazo_limite:
                raise ValidationError(f"Prazo de retorno expirado. O limite era até {prazo_limite.strftime('%d/%m/%Y')}.")
