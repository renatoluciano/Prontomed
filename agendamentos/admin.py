from django.contrib import admin
from .models import Especialidade, Medico, TipoExame, Agendamento

@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('get_nome_completo', 'crm', 'especialidade', 'telefone')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'crm')
    list_filter = ('especialidade',)

    # Método auxiliar para exibir o nome completo do médico no painel
    def get_nome_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nome_completo.short_description = 'Nome do Médico'

@admin.register(TipoExame)
class TipoExameAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'paciente', 'medico', 'tipo_exame', 'data', 'horario')
    list_filter = ('tipo', 'data', 'medico')
    search_fields = ('paciente__username', 'medico__usuario__first_name', 'data')
    
    # Organiza os campos visualmente na tela de cadastro/edição do admin
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('paciente', 'tipo', 'data', 'horario')
        }),
        ('Detalhes Opcionais (Conforme o Tipo)', {
            'fields': ('medico', 'tipo_exame', 'consulta_original'),
            'description': 'Preencha apenas os campos necessários para o tipo de agendamento selecionado.'
        }),
    )

    # Força a execução das validações personalizadas do 'clean()' dentro do painel admin
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)
