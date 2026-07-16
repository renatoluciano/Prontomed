from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Especialidade, Medico, TipoExame, Agendamento

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class EspecialidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidade
        fields = '__all__'

class MedicoSerializer(serializers.ModelSerializer):
    # Traz os detalhes do usuário dono deste perfil médico de forma aninhada
    usuario = UserSerializer(read_only=True)
    especialidade_nome = serializers.CharField(source='especialidade.nome', read_only=True)

    class Meta:
        model = Medico
        fields = ['id', 'usuario', 'crm', 'especialidade', 'especialidade_nome', 'telefone']

class TipoExameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoExame
        fields = '__all__'

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'

    # Garante que as validações personalizadas do 'clean()' do Model também rodem na API
    def validate(self, attrs):
        # Cria uma instância temporária do model sem salvar no banco apenas para rodar as validações
        instance = Agendamento(**attrs)
        try:
            instance.clean()
        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError(e.message if hasattr(e, 'message') else str(e))
        return attrs
