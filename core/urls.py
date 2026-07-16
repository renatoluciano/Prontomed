from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclui todas as rotas da nossa API sob o prefixo /api/
    path('api/', include('agendamentos.urls')),
]
