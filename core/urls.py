from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from consultas.views import ProfissionalViewSet, ConsultaViewSet, asaas_webhook
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Importa as views prontas de JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'consultas', ConsultaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), # Gera o arquivo de esquema oculto
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # Tela visual do Swagger
    path('api-auth/', include('rest_framework.urls')),
    path('api/webhooks/asaas/', asaas_webhook, name='webhook-asaas'),
]