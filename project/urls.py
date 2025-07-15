"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ventasapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('index/', views.index,name="index"),
    path('', views.tienda, name="tienda"),## AQUI ESTOY MOSTRANDO LOS NEGOCIOS sin login
    path('tienda/', views.tienda, name="tienda"),## AQUI ESTOY MOSTRANDO LOS NEGOCIOS sin login
    path('crear_negocio/', views.create_or_update_business, name='crear_negocio'),  # Create
  

    # Stripe: éxito de suscripción
    path('suscripcion/exitosa/', views.subscription_success, name='subscription_success'),

    # Stripe: webhook (no lleva login)
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),

    # (Opcional) página de cancelación
    path('negocio/<int:business_id>/cancelado/', views.subscription_cancelled, name='subscription_cancelled'),

    path('start-subscription-for-business/<int:business_id>/', views.start_subscription_for_business, name='start_subscription_for_business'),

    # urls.py
    path('negocio/<int:business_id>/redirigir-a-suscripcion/', views.redirect_to_stripe_checkout, name='redirect_to_stripe_checkout'),#ESTO ES PARA LO DE LA SUSCRIPCION DE CADA NEGOCIO

    path('stripe/crear-y-redirigir/', views.stripe_crear_y_redirigir, name='stripe_crear_y_redirigir'),

   path('stripe/return/', views.stripe_onboarding_completado, name='stripe_onboarding_completado'),




    path('crear_negocio/<int:business_id>/', views.create_or_update_business, name='editar_negocio'),  # Edit
    path('register/<str:role>/', views.register_user, name='register_user'),
    path('registrar/<str:role>/', views.registtrar_conductor, name='registro_conductor'),
    path('not-authorized/', views.not_authorized, name='not_authorized'),
    path('login/', views.login_user, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),   
    path('logout/', views.logout_user, name='logout'),
    path('business/delete/<int:business_id>/', views.eliminar_negocio, name='delete_business'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('negocio/<int:business_id>/', views.business_detail, name='business_detail'),
    path('negocio/<int:business_id>/agregar-producto/', views.agregar_item_menu_negocio, name='agregar_producto'),
    path('producto/<int:producto_id>/agregar-extra/', views.agregar_extra, name='agregar_extra'),

    path('producto/<int:producto_id>/editar/', views.editar_producto_menu, name='editar_producto_menu'),
    path('negocio/<int:business_id>/productos/', views.ver_menu_negocio, name='menu'),
    path('producto/<int:producto_id>/',views.eliminar_producto_menu, name="eliminar_producto_menu"),

      path('carrito/eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/add/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),  # Ver carrito
    path('carrito/checkout/', views.checkout, name='checkout'),  # Stripe checkout    
    path('direccion-envio/', views.direccion_envio, name='direccion_envio'),
    path('carrito/success/', views.success, name='success'),
    path('business/<int:business_id>/pedidos/', views.ver_pedidos_por_negocio, name='ver_pedidos_por_negocio'),
    
    path('pedidos/<int:pedido_id>/marcar-envio/', views.marcar_envio_pedido, name='marcar_envio_pedido'),
    path('actualizar_carrito_ajax/', views.actualizar_carrito_ajax, name='actualizar_carrito_ajax'),


    
   

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
