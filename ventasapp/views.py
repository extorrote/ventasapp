from django.shortcuts import render

from .models import Business,Producto,UserProfile,CATEGORY_TYPES, CITIES,DAYS_OF_WEEK,Extra

from .forms import BusinessForm, UserRegistrationForm,BusinessOwnerProfileForm,EditUserForm,EditBusinessOwnerProfileForm,CustomPasswordChangeForm,ProductoForm,ConductorProfileForm,ExtraForm


from django.shortcuts import render, redirect, get_object_or_404##ESTE ME SIRVE PAARA LA EDICION DE ITEMS
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail #ENVIAR EMAIL
from django.conf import settings #ESTO ES PARA IMPORTAR LOS SETTINGS DEL BACKEND PARA EL ENVIO DEL EMAIL 
from django.contrib import messages #MENSAJES DE SUCESS O ERROR
from django.http import HttpResponseForbidden ## ESTE ES EL QUE SIRVE PARA MOSTRAR ERROR 404, O POR EJEMPLO LOS ERORES DE ACCESO O NO AUTORIZED,
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives#ESTE ME PERMITE ENVIAR EMAILS CON TEXTO PLANO Y CON HTML,lo estamos utilizando para las notificaciones de los registros.
from django.contrib.auth import authenticate, login,logout
from .models import CATEGORY_TYPES ##ESTE ES PARA SELECCIONAR LAS CATEGORIAS DE NEGOCIO CUANDO INGRESAMOS UNA PROPIEDAD, LO ESTAMOS USANDO EN EL BUCLE DE LOS BOTONES
from django.db.models import Q



def index(request):
    return render(request,'index.html')


def register_user(request, role):
    if role not in ['business_owner', 'concierge']:
        return redirect('home')

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = BusinessOwnerProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = role
            if role == 'business_owner':
                role_text = "Propietario de Negocio"
            else:
                role_text = role.capitalize()
            profile.save()

            # Iniciar sesión automáticamente
            login(request, user)

            # Guardar ID en sesión para onboarding de Stripe
            request.session['pending_stripe_user_id'] = user.id

            # Enviar correo al administrador
            subject = "Registro de Nuevo Usuario"
            from_email = "noreply@yourdomain.com"
            to = ['wwwstephen95live@gmail.com']
            text_content = f"Un nuevo {role_text} se ha registrado con el nombre de usuario: {user.username}. Requiere aprobación para acceder al sistema."
            html_content = f"""
            <p>Un nuevo <strong style="color:#48e;">{role_text}</strong> se ha registrado con el nombre de usuario: 
            <span style="color:red; font-weight:bold;">{user.username}</span> 
            Requiere aprobación para acceder al sistema.</p>
            """
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # Redirigir a la vista que crea cuenta Stripe y lanza onboarding
            return redirect('stripe_crear_y_redirigir')

    else:
        user_form = UserRegistrationForm()
        profile_form = BusinessOwnerProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role
    })


# views.py
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from .models import UserProfile





stripe.api_key = settings.STRIPE_SECRET_KEY  # Asegúrate de tener esto en settings.py

@login_required
def stripe_crear_y_redirigir(request):
    user_id = request.session.get('pending_stripe_user_id')
    if not user_id:
        return HttpResponse("No se encontró el usuario para conectar a Stripe.", status=400)

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)

    try:
        if not profile.stripe_account_id:
            # ✅ Crear cuenta Express con ambas capacidades
            account = stripe.Account.create(
                type="express",
                country="MX",  # Ajusta si operas en otro país
                email=profile.email,
                capabilities={
                    "transfers": {"requested": True},
                    "card_payments": {"requested": True},
                },
            )
            profile.stripe_account_id = account.id
            profile.save()

        # ✅ Crear link de onboarding
        account_link = stripe.AccountLink.create(
            account=profile.stripe_account_id,
            refresh_url=request.build_absolute_uri(reverse('stripe_crear_y_redirigir')),
            return_url=request.build_absolute_uri(reverse('stripe_onboarding_completado')),
            type='account_onboarding',
        )

        # Limpiar session después de usarla
        if 'pending_stripe_user_id' in request.session:
            del request.session['pending_stripe_user_id']

        return redirect(account_link.url)

    except stripe.error.InvalidRequestError as e:
        return HttpResponse(f"Error al conectar con Stripe: {e.user_message}", status=400)

    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)




# views.py
@login_required
def stripe_onboarding_completado(request):
    return redirect('dashboard')

    

def registtrar_conductor(request, role):
    

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ConductorProfileForm(request.POST, request.FILES) 

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = role
            
            profile.save()

            # Email content
            subject = "Registro de Nuevo Usuario"
            from_email = "noreply@yourdomain.com"
            to = ['wwwstephen95live@gmail.com']
            text_content = f"Un nuevo {role} se ha registrado con el nombre de usuario: {user.username}. Requiere aprobación para acceder al sistema."
            html_content = f"""
            <p>Un nuevo <strong style="color:#48e;">{role}</strong> se ha registrado con el nombre de usuario: 
            <span style="color:red; font-weight:bold;">{user.username}</span> 
            Requiere aprobación para acceder al sistema.</p>
            """

            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return render(request, 'registration_pending.html')

    else:
        user_form = UserRegistrationForm()
        profile_form = ConductorProfileForm()
        

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'role': role
    })

    
from .models import ConductorUser

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Primero intenta encontrar un perfil en UserProfile
            try:
                profile = user.userprofile
                if profile.is_approved:
                    login(request, user)
                    return redirect('dashboard')  # Redirige a dashboard único
                else:
                    messages.warning(request, "Tu cuenta aún no ha sido aprobada.")
            except UserProfile.DoesNotExist:
                # Si no existe en UserProfile, intenta en ConductorUser
                try:
                    conductor = ConductorUser.objects.get(user=user)
                    if conductor.is_approved:
                        login(request, user)
                        return redirect('dashboard')  # Cambiado a dashboard único también para conductor
                    else:
                        messages.warning(request, "Tu cuenta de conductor aún no ha sido aprobada.")
                except ConductorUser.DoesNotExist:
                    messages.error(request, "No se encontró un perfil asociado a este usuario. Contacta al soporte.")
        else:
            messages.error(request, "Nombre de usuario o contraseña inválidos.")
    
    return render(request, 'index.html')






# ESTOS SON LOS LABELS PARA LOS BOTONES PORQUE LOS ESTAMOS METIENDO EN IN BUcle
CATEGORY_DISPLAY_NAMES = {
    
    'gastronomia_bebidas': 'Gastronomía / Bebidas',
    'tiendas_de_conveniencia': 'Tiendas de Conveniencia',
    'farmacias': 'Farmacias',
    'flores_y_regalos': 'Flores y Regalos',
    
    
}
from .models import ConductorUser,UserProfile
@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        try:
            profile = request.user.conductoruser
        except ConductorUser.DoesNotExist:
            return redirect('not_authorized')

    category_filter = request.GET.get('categoria')  # e.g. "tours_actividades"

    if profile.role == 'business_owner':
        businesses = Business.objects.filter(owner=request.user)
        return render(request, 'dashboard_business_owner.html', {
            'profile': profile,
            'businesses': businesses, 
            'selected_category': category_filter,
            'categories': CATEGORY_TYPES,
            'category_labels': CATEGORY_DISPLAY_NAMES,
        })

    elif profile.role == 'conductor':
        # ✅ Filtrar negocios por ciudad del conductor
        businesses = Business.objects.filter(city=profile.city)

        if category_filter:
            category_types = dict(CATEGORY_TYPES).get(category_filter, [])
            category_codes = [code for code, label in category_types]
            if category_codes:
                businesses = businesses.filter(
                    Q(tipos_de_negocio__iregex=r'\b(' + '|'.join(category_codes) + r')\b')
                )

        return render(request, 'dashboard2.html', {
            'profile': profile,
            'businesses': businesses,
            'selected_category': category_filter,
            'categories': CATEGORY_TYPES,
            'category_labels': CATEGORY_DISPLAY_NAMES,
        })

    else:
        return redirect('not_authorized')
    

from django.shortcuts import render
from django.db.models import Q
from .models import Business, CATEGORY_TYPES

def tienda(request):
    category_filter = request.GET.get('categoria')  # Ejemplo: "gastronomia_bebidas"

    # Obtener todos los negocios que no tienen usuario asignado
    businesses = Business.objects.all()

    # Si hay filtro por categoría, aplicarlo
    if category_filter:
        category_types = CATEGORY_TYPES.get(category_filter, [])
        category_codes = [code for code, _ in category_types]

        if category_codes:
            businesses = businesses.filter(
                Q(tipos_de_negocio__iregex=r'\b(' + '|'.join(category_codes) + r')\b')
            )

    return render(request, 'dashboard2.html', {
        'profile': None,
        'businesses': businesses,
        'selected_category': category_filter,
        'categories': CATEGORY_TYPES,
        'category_labels': CATEGORY_DISPLAY_NAMES,
    })




import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Business, BusinessSubscription
from .forms import BusinessForm


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import BusinessSubscription

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'invoice.payment_failed':
        subscription_id = event['data']['object']['subscription']
        try:
            sub = BusinessSubscription.objects.get(stripe_subscription_id=subscription_id)
            sub.is_active = False
            sub.save()
            if sub.business:
                sub.business.is_active = False
                sub.business.save()
        except BusinessSubscription.DoesNotExist:
            pass

    elif event['type'] == 'invoice.payment_succeeded':
        subscription_id = event['data']['object']['subscription']
        try:
            sub = BusinessSubscription.objects.get(stripe_subscription_id=subscription_id)
            sub.is_active = True
            sub.save()
            if sub.business:
                sub.business.is_active = True
                sub.business.save()
        except BusinessSubscription.DoesNotExist:
            pass

    return HttpResponse(status=200)





stripe.api_key = settings.STRIPE_SECRET_KEY
@login_required
def redirect_to_stripe_checkout(request, business_id):
    return render(request, 'redirect_to_stripe.html', {
        'business_id': business_id,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })

@login_required
def create_or_update_business(request, business_id=None):
    if business_id:
        business = get_object_or_404(Business, id=business_id)
        if business.owner != request.user:
            return HttpResponseForbidden("No estás autorizado para editar este negocio.")
    else:
        business = None

    user_giro = request.user.userprofile.giro_de_negocio

    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            business = form.save(commit=False)

            if not business_id:
                business.owner = request.user
                business.owner_or_manager_email = request.user.email
                business.city = request.user.userprofile.city
                business.tipos_de_negocio = user_giro

            business.save()

            # Redirige para iniciar la suscripción asociada a este negocio
           
            return redirect('redirect_to_stripe_checkout', business_id=business.id)

    else:
        initial = {}
        if not business_id:
            initial['tipos_de_negocio'] = user_giro
        form = BusinessForm(instance=business, initial=initial)
        form.fields['tipos_de_negocio'].disabled = True

    return render(request, 'business_form.html', {'form': form})


@login_required
def start_subscription_for_business(request, business_id):
    business = get_object_or_404(Business, id=business_id, owner=request.user)

    num_businesses = Business.objects.filter(owner=request.user).count()

    if num_businesses == 1:
        price_id = settings.STRIPE_PRICE_FIRST_BUSINESS  # Precio primer negocio ₱519
        trial_days = 0
    else:
        price_id = settings.STRIPE_PRICE_ADDITIONAL_BUSINESS  # Precio adicionales ₱419
        trial_days = None

    user = request.user
    if not hasattr(user, "userprofile") or not user.userprofile.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email)
        user.userprofile.stripe_customer_id = customer.id
        user.userprofile.save()
    else:
        customer = stripe.Customer.retrieve(user.userprofile.stripe_customer_id)

    subscription_data = {}
    if trial_days:
        subscription_data['trial_period_days'] = trial_days

    base_url = request.build_absolute_uri('/suscripcion/exitosa/')
    success_url = f"{base_url}?session_id={{CHECKOUT_SESSION_ID}}"

    session = stripe.checkout.Session.create(
        customer=customer.id,
        payment_method_types=['card'],
        mode='subscription',
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        subscription_data=subscription_data,
        metadata={
            'user_id': user.id,
            'business_id': business.id,
        },
        success_url=success_url,
        cancel_url=request.build_absolute_uri(f'/negocio/{business.id}/cancelado/'),
    )

    return JsonResponse({'sessionId': session.id})




@login_required
def subscription_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponseBadRequest("Sesión no válida")

    session = stripe.checkout.Session.retrieve(session_id)
    subscription_id = session.subscription
    customer_id = session.customer

    business_id = session.metadata.get('business_id')
    business = None
    if business_id:
        try:
            business = Business.objects.get(id=business_id, owner=request.user)
        except Business.DoesNotExist:
            business = None

    if not BusinessSubscription.objects.filter(stripe_subscription_id=subscription_id).exists():
        BusinessSubscription.objects.create(
            user=request.user,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=customer_id,
            business=business,
            is_active=True,
        )

    messages.success(request, "Suscripción activada y negocio publicado.")
    return redirect('dashboard')


def subscription_cancelled(request, business_id):
    messages.info(request, "No completaste el pago de suscripción. Puedes intentarlo más tarde.")
    return redirect('dashboard')




### ESTA ES LA VISTA PARA MOSTRAR LOS DETALLES DEL NEGOCIO
@login_required
def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id)

    # Intenta obtener el perfil del usuario (UserProfile o ConductorUser)
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        try:
            profile = request.user.conductoruser
        except ConductorUser.DoesNotExist:
            return redirect('not_authorized')

    # Permissions check
    if profile.role == 'business_owner' and business.owner != request.user:
        return redirect('not_authorized')
    elif profile.role == 'conductor' and business.city != profile.city:
        return redirect('not_authorized')

    # Si el perfil tiene `giro_de_negocio`, lo usamos, si no, lo dejamos como None
    tipo_de_negocio = getattr(profile, 'giro_de_negocio', None)

    # Get products
    productos = Producto.objects.filter(business=business)

    return render(request, 'detail_business.html', {
        'business': business,
        'productos': productos,
        'profile': profile,
        'tipo_de_negocio': tipo_de_negocio,
    })
    
    

def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    productos = Producto.objects.filter(business=business)

    return render(request, 'detail_business.html', {
        'business': business,
        'productos': productos,
        'profile': None,
        'tipo_de_negocio': None,
    })
    

##ESTA ES LA VISTA PARA ELIMINAR UN NEGOCIO    
@login_required
def eliminar_negocio(request, business_id):
    business = get_object_or_404(Business, id=business_id)

    # Only allow deletion if the logged-in user is the owner/manager
    if request.user.email != business.owner_or_manager_email:
        return redirect('not_authorized')

    if request.method == 'POST':
        business.delete()
        return redirect('dashboard')

    return render(request, 'confirm_delete.html', {'business': business})    




def send_email(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            company_name=form.cleaned_data['company_name']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            message = form.cleaned_data['message']

            # Process the form data, e.g., send an email
            send_mail(
                f'Contact Form Submission from {name}',
                f'Nombre de la Compañia: {company_name}\nMi Nombre: {name}\nPhone: {phone}\nEmail: {email}\n Descripcion de la empresa: {message}',
                'proyectodigitalmexico@gmail.com',  # From email
                ['proyectodigitalmexico@gmail.com'],  # To email
                fail_silently=False,
            )


            messages.success(request, 'Email Sent!  we will Get Back to You Soon')
            return redirect('index')
    else:
        form = ContactForm()

    return render(request, 'index.html', {'form': form})



##ESTO ES CUANDO EL USUARIO SE LOGUEO CON OTRA CUENTA Y YA EN LA OTRA PESTAÑA ACTUALIZA LO VA REDIRIGIR AQUI 
@login_required
def not_authorized(request):
    return render(request, 'navegador_expirado.html')




#ESTA ES LA VISTA PARA MOSTRAR EL PERFIL DEL USUARIO
@login_required
def view_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        try:
            profile = request.user.conductoruser
        except ConductorUser.DoesNotExist:
            return redirect('not_authorized')

    if profile.role == 'business_owner':
        template = 'view_profile_business_owner.html'
    elif profile.role == 'conductor':
        template = 'view_profile_concierge.html'
    else:
        return redirect('not_authorized')

    return render(request, template, {
        'user': request.user,
        'profile': profile
    })


from .forms import EditarConductorProfile 
from django.contrib.auth import update_session_auth_hash 

#VISTA PARA EDITAR PERFIL DE USUARIO
@login_required
def edit_profile(request):
    user = request.user

    # Intenta obtener cualquiera de los dos perfiles
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        try:
            profile = user.conductoruser
        except ConductorUser.DoesNotExist:
            return redirect('not_authorized')

    original_role = profile.role  # Bloquea el cambio de rol

    user_form = EditUserForm(request.POST or None, instance=user)

    # Elige el formulario correcto según el rol
    if original_role == 'business_owner':
        profile_form = EditBusinessOwnerProfileForm(
            request.POST or None, request.FILES or None, instance=profile
        )
    elif original_role == 'conductor':
        profile_form = EditarConductorProfile(  # ✅ CAMBIO AQUÍ
            request.POST or None, request.FILES or None, instance=profile
        )
    else:
        return redirect('not_authorized')

    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get("password")
            if password:
                user.set_password(password)
                update_session_auth_hash(request, user)
            user.save()

            updated_profile = profile_form.save(commit=False)
            updated_profile.role = original_role
            updated_profile.save()

            return redirect('view_profile')

    return render(request, 'editar_perfil_usuario.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })




def logout_user(request):
    logout(request)
    return redirect('index') 

##CAMBIAR LA CONTRASEÑA DE USUARIO
from django.contrib.auth.forms import PasswordChangeForm
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, 'Tu contraseña se ha cambiado correctamente!')
            return redirect('index')
        else:
            messages.error(request, 'Porfavor corrige los siguientes errores.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html',{'form': form})






#ESTA ES LA VISTA PARA AGREGAR UN PRODUCTO ESTANDAR A UN NEGOCIO
@login_required
def agregar_item_menu_negocio(request, business_id):
    business = get_object_or_404(Business, id=business_id, owner=request.user)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, business_instance=business)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.business = business
            producto.tipo_subcategoria = business.tipos_de_negocio  # Asigna el tipo
            producto.save()
            return redirect('dashboard')  
    else:
        form = ProductoForm(business_instance=business)

    return render(request, 'agregar_producto.html', {'form': form, 'business': business})



@login_required
def agregar_extra(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, business__owner=request.user)
    
    if request.method == 'POST':
        form = ExtraForm(request.POST)
        if form.is_valid():
            extra = form.save(commit=False)
            extra.producto = producto
            extra.save()
            return redirect('menu', business_id=producto.business.id)  # CORREGIDO
    else:
        form = ExtraForm()

    return render(request, 'agregar_extras.html', {
        'form': form,
        'producto': producto
    })



#ESTA ES LA VISTA DONDE ESTOY MOSTRANDO LOS PRODUCTOS ESTANDAR , AQUI NO SE ESTAN MOSTRANDO LOS PRODUCTOS DE HOTELERIA
from django.db.models import Prefetch

@login_required 
def ver_menu_negocio(request, business_id):
    business = get_object_or_404(Business, id=business_id)

    productos = Producto.objects.filter(business=business).prefetch_related('extras').order_by('name')

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        try:
            profile = request.user.conductoruser
        except ConductorUser.DoesNotExist:
            return redirect('not_authorized')

    return render(request, 'menu.html', {
        'business': business,
        'productos': productos,
        'profile': profile
    })


def ver_menu_negocio(request, business_id):
    business = get_object_or_404(Business, id=business_id)

    productos = Producto.objects.filter(business=business).prefetch_related('extras').order_by('name')

    

    return render(request, 'menu.html', {
        'business': business,
        'productos': productos,
        'profile': None
    })
    
    
#EDITAR PRODUCTO ESTANDAR 
@login_required
def editar_producto_menu(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    profile = request.user.userprofile

    # Access control
    if profile.role == 'business_owner' and producto.business.owner != request.user:
        return redirect('not_authorized')
    elif profile.role == 'concierge' and producto.business.city != profile.city:
        return redirect('not_authorized')

    business = producto.business

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'agregar_producto.html', {
        'form': form,
        'business': business,
        'editing': True,
        'producto': producto
    })

#ELIMINAR PRODUCTO ESTANDAR     
@login_required
def eliminar_producto_menu(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Only allow deletion if the logged-in user is the owner/manager
    if request.user.userprofile.role == 'busines_owner':
        return redirect('not_authorized')
        

    if request.method == 'POST':
        producto.delete()
        return redirect('dashboard')

    return render(request, {'business': producto})





from django.shortcuts import render, redirect
from .models import Producto, Extra, CartItem, ExtraEnCarrito, Cart
from .forms import DireccionDeEnvioForm

def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)
    request.session['cart_id'] = cart.id  # Por si quieres seguir usándolo
    return cart



def add_to_cart(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cart = get_or_create_cart(request)

    if cart.items.exists():
        negocio_existente = cart.items.first().producto.business
        if producto.business != negocio_existente:
            return JsonResponse({
                "status": "error",
                "message": "Tu carrito ya contiene productos de otro negocio. Finaliza esa compra antes de agregar productos de un nuevo negocio."
            })

    # Agrega el producto al carrito
    item = CartItem.objects.create(cart=cart, producto=producto, cantidad=1)

    extras_ids = request.POST.getlist('extras')
    for extra_id in extras_ids:
        extra = Extra.objects.get(id=extra_id)
        ExtraEnCarrito.objects.create(cart_item=item, extra=extra, cantidad=1)

    return JsonResponse({
        "status": "success",
        "message": f"Agregado {producto.name} al carrito."
    })

###ver carrito
def ver_carrito(request):
    cart = get_or_create_cart(request)

    # Procesa solo si viene del botón "guardar" o "proceder"
    if request.method == "POST":
        action = request.POST.get('action')

        if action in ['guardar', 'proceder']:
            for item in cart.items.all():
                # 🔄 Actualiza la cantidad del producto
                cantidad_str = request.POST.get(f'cantidad_{item.id}')
                if cantidad_str and cantidad_str.isdigit():
                    cantidad = int(cantidad_str)
                    if cantidad > 0:
                        item.cantidad = cantidad

                # 📝 Actualiza la nota del producto
                nota = request.POST.get(f'nota_{item.id}', '').strip()
                item.nota = nota  # 👈 Guarda la nota escrita por el usuario

                item.save()

                # 🔁 Elimina los extras anteriores del carrito
                item.extras_en_carrito.all().delete()

                # ➕ Agrega extras nuevos desde el POST
                for key in request.POST:
                    if key.startswith(f'extra_{item.id}_'):
                        extra_id = key.split('_')[-1]
                        cantidad_str = request.POST[key]
                        if cantidad_str and cantidad_str.isdigit():
                            cantidad = int(cantidad_str)
                            if cantidad > 0:
                                try:
                                    extra = Extra.objects.get(id=extra_id)
                                    ExtraEnCarrito.objects.create(
                                        cart_item=item,
                                        extra=extra,
                                        cantidad=cantidad
                                    )
                                except Extra.DoesNotExist:
                                    continue  # Ignora si el extra no existe

            if action == 'proceder':
                return redirect('direccion_envio')

    # 🧮 Cálculo de subtotales por producto y total general
    cart_items_info = []
    total_general = 0

    for item in cart.items.all():
        subtotal_producto = item.producto.price * item.cantidad

        extras_info = []
        subtotal_extras = 0
        for extra_item in item.extras_en_carrito.all():
            subtotal_extra = extra_item.extra.precio * extra_item.cantidad
            extras_info.append({
                'nombre': extra_item.extra.nombre,
                'cantidad': extra_item.cantidad,
                'precio': extra_item.extra.precio,
                'subtotal': subtotal_extra
            })
            subtotal_extras += subtotal_extra

        subtotal_total = subtotal_producto + subtotal_extras
        total_general += subtotal_total

        cart_items_info.append({
            'item': item,
            'nota': item.nota,
            'subtotal_producto': subtotal_producto,
            'extras_info': extras_info,
            'subtotal_extras': subtotal_extras,
            'subtotal_total': subtotal_total
        })

    # ✅ Detectar si el carrito está vacío
    carrito_vacio = not cart.items.exists()

    return render(request, 'carrito.html', {
        'cart': cart,
        'cart_items_info': cart_items_info,
        'total_general': total_general,
        'carrito_vacio': carrito_vacio,  # 👈 Se pasa al template
    })




from django.views.decorators.http import require_POST

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])  # Permite GET además de POST
def eliminar_item_carrito(request, item_id):
    print(f"Intentando eliminar item_id: {item_id}")  # Debug

    cart = get_or_create_cart(request)
    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
        item.delete()
        print(f"Item {item_id} eliminado correctamente")
    except CartItem.DoesNotExist:
        print(f"Item {item_id} no existe o no pertenece al carrito")

    return redirect('ver_carrito')







from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# ESTA VISTA LA CREE PARA QUE SE PUEDAN ACTUALIZAR CON AJAX AUTOMATICAAMENTE LAS CANTIDADES Y EXTRAS DEL CARRITO
@csrf_exempt
def actualizar_carrito_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        cantidad = data.get('cantidad')
        extras = data.get('extras', {})
        nota = data.get('nota', '')  # <-- obtener la nota

        try:
            item = CartItem.objects.get(id=item_id)
            if cantidad and int(cantidad) > 0:
                item.cantidad = int(cantidad)

            item.nota = nota  # <-- guardar nota
            item.save()

            item.extras_en_carrito.all().delete()
            for extra_id_str, cantidad_str in extras.items():
                if cantidad_str and cantidad_str.isdigit() and int(cantidad_str) > 0:
                    extra = Extra.objects.get(id=int(extra_id_str))
                    ExtraEnCarrito.objects.create(cart_item=item, extra=extra, cantidad=int(cantidad_str))

            # Calcular total
            cart = item.cart
            total_general = 0
            for cart_item in cart.items.all():
                subtotal_producto = cart_item.producto.price * cart_item.cantidad
                subtotal_extras = sum(
                    e.extra.precio * e.cantidad for e in cart_item.extras_en_carrito.all()
                )
                total_general += subtotal_producto + subtotal_extras

            return JsonResponse({
                'status': 'success',
                'total_general': total_general
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)








import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY 

# en ventasapp/views.py

import stripe
from django.conf import settings
from django.shortcuts import redirect
from .models import Cart, DireccionDeEnvio,Venta

from .forms import DireccionDeEnvioForm
from decimal import Decimal #ESTO SE ESTA USANDO EN LA LOGICA DE QUE SI EL USUARIO ELIGE RETIRO EN SUCURSAL O ENVIO A DOMICILIO
def direccion_envio(request): 
    if request.method == "POST":
        form = DireccionDeEnvioForm(request.POST)
        if form.is_valid():
            opcion_entrega = form.cleaned_data.get('opcion_entrega')
            direccion_envio = form.save(commit=False)

            # Obtener el carrito
            cart = get_or_create_cart(request)

            if opcion_entrega == 'sucursal':
                # Retiro en sucursal = sin dirección ni costo
                direccion_envio.direccion = ''
                direccion_envio.ciudad = ''
                direccion_envio.estado = ''
                direccion_envio.codigo_postal = ''
                direccion_envio.costo_envio = 0
            else:
                # Domicilio: considerar si hay envío gratis
                productos = [item.producto for item in cart.items.all()]
                if productos:
                    todos_envio_gratis = all(p.tiene_envio_gratis for p in productos)
                    if todos_envio_gratis:
                        # Todos con envío gratis -> costo_envio 0
                        direccion_envio.costo_envio = 0
                    else:
                        # Costo envío es el mayor precio_de_envio de productos sin envío gratis
                        productos_con_envio = [p for p in productos if not p.tiene_envio_gratis]
                        mayor_precio_envio = max([p.precio_de_envio or 0 for p in productos_con_envio])
                        direccion_envio.costo_envio = Decimal(mayor_precio_envio)
                else:
                    direccion_envio.costo_envio = 0  # por si acaso

            # Si el usuario decidió propina después, fuerza a 0
            if form.cleaned_data.get('decidir_propina_despues'):
                direccion_envio.propina_voluntaria = 0

            direccion_envio.save()
            request.session['direccion_envio_id'] = direccion_envio.id
            return redirect('checkout')
    else:
        form = DireccionDeEnvioForm()

    return render(request, 'direccion_envio.html', {'form': form})





stripe.api_key = settings.STRIPE_SECRET_KEY



from decimal import Decimal  # Asegúrate de tener esta importación al inicio del archivo

def iniciar_pago(request):
    cart = get_or_create_cart(request)
    direccion = DireccionDeEnvio.objects.get(id=request.session['direccion_envio_id'])

    negocio = cart.items.first().producto.business  # Asumiendo 1 solo negocio
    line_items = []

    for item in cart.items.all():
        line_items.append({
            'price_data': {
                'currency': 'mxn',
                'unit_amount': int(Decimal(item.producto.price) * 100),
                'product_data': {'name': item.producto.name},
            },
            'quantity': item.cantidad,
        })

        for extra_item in item.extras_en_carrito.all():
            precio_extra = Decimal(extra_item.extra.precio or 0)
            line_items.append({
                'price_data': {
                    'currency': 'mxn',
                    'unit_amount': int(precio_extra * 100),
                    'product_data': {
                        'name': f"{extra_item.extra.nombre} (Extra de {item.producto.name})"
                    },
                },
                'quantity': extra_item.cantidad,
            })

    # Costo envío (igual que tu lógica)
    if direccion.opcion_entrega == 'domicilio':
        productos = [item.producto for item in cart.items.all()]
        if productos:
            todos_envio_gratis = all(p.tiene_envio_gratis for p in productos)
            if not todos_envio_gratis:
                productos_con_envio = [p for p in productos if not p.tiene_envio_gratis]
                mayor_precio_envio = max([Decimal(p.precio_de_envio or 0) for p in productos_con_envio])
                if mayor_precio_envio > 0:
                    line_items.append({
                        'price_data': {
                            'currency': 'mxn',
                            'unit_amount': int(mayor_precio_envio * 100),
                            'product_data': {'name': 'Envío a domicilio'},
                        },
                        'quantity': 1,
                    })

    # Propina voluntaria
    if direccion.propina_voluntaria and direccion.propina_voluntaria > 0:
        line_items.append({
            'price_data': {
                'currency': 'mxn',
                'unit_amount': int(Decimal(direccion.propina_voluntaria) * 100),
                'product_data': {'name': 'Propina voluntaria'},
            },
            'quantity': 1,
        })

    stripe_params = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': request.build_absolute_uri('/carrito/success/'),
        'cancel_url': request.build_absolute_uri('/carrito/cancel/'),
    }

    if negocio.stripe_account_id and negocio.stripe_account_id != settings.STRIPE_ACCOUNT_ID:
        stripe_params['payment_intent_data'] = {
            # No application_fee_amount si no quieres comisión
            'transfer_data': {
                'destination': negocio.stripe_account_id,
            },
        }
        checkout_session = stripe.checkout.Session.create(
            **stripe_params,
            stripe_account=negocio.stripe_account_id
        )
    else:
        checkout_session = stripe.checkout.Session.create(**stripe_params)

    return redirect(checkout_session.url)






######## AQUI ES DONDE SALE TODA LA LISTAA EN STRIPE
def checkout(request):
    cart = get_or_create_cart(request)
    direccion_envio_id = request.session.get('direccion_envio_id')
    direccion_envio = None
    if direccion_envio_id:
        try:
            direccion_envio = DireccionDeEnvio.objects.get(id=direccion_envio_id)
        except DireccionDeEnvio.DoesNotExist:
            pass

    line_items = []
    negocio = None

    for item in cart.items.all():
        negocio = item.producto.business

        # Producto principal
        line_items.append({
            'price_data': {
                'currency': 'mxn',
                'product_data': {'name': item.producto.name},
                'unit_amount': int(item.producto.price * 100),
            },
            'quantity': item.cantidad,
        })

        # Extras con cantidad desde ExtraEnCarrito
        for extra_item in item.extras_en_carrito.all():
            precio_extra = extra_item.extra.precio or 0
            line_items.append({
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': f"{extra_item.extra.nombre} (Extra de {item.producto.name})"
                    },
                    'unit_amount': int(precio_extra * 100),
                },
                'quantity': extra_item.cantidad,
            })

    # Agregar costo de envío si es domicilio y corresponde
    if direccion_envio and direccion_envio.opcion_entrega == 'domicilio':
        productos = [item.producto for item in cart.items.all()]
        if productos:
            todos_envio_gratis = all(p.tiene_envio_gratis for p in productos)
            if not todos_envio_gratis:
                productos_con_envio = [p for p in productos if not p.tiene_envio_gratis]
                mayor_precio_envio = max([p.precio_de_envio or 0 for p in productos_con_envio])
                if mayor_precio_envio > 0:
                    line_items.append({
                        'price_data': {
                            'currency': 'mxn',
                            'product_data': {'name': 'Envío a domicilio'},
                            'unit_amount': int(mayor_precio_envio * 100),
                        },
                        'quantity': 1,
                    })

    # Agregar propina voluntaria si aplica
    if direccion_envio and direccion_envio.propina_voluntaria and direccion_envio.propina_voluntaria > 0:
        line_items.append({
            'price_data': {
                'currency': 'mxn',
                'product_data': {'name': 'Propina'},
                'unit_amount': int(direccion_envio.propina_voluntaria * 100),
            },
            'quantity': 1,
        })

    stripe_params = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': request.build_absolute_uri('/carrito/success/'),
        'cancel_url': request.build_absolute_uri('/carrito/cancel/'),
    }

    # Stripe Connect
    if negocio and negocio.stripe_account_id and negocio.stripe_account_id != settings.STRIPE_ACCOUNT_ID:
        stripe_params['payment_intent_data'] = {
            'application_fee_amount': 500,
            'transfer_data': {
                'destination': negocio.stripe_account_id,
            },
        }

    # Agregar metadata de envío si está disponible
    if direccion_envio:
        stripe_params['metadata'] = {
            'metodo_entrega': direccion_envio.opcion_entrega,
            'nombre_completo': direccion_envio.nombre_completo,
            'telefono': direccion_envio.telefono,
            'direccion': direccion_envio.direccion,
            'ciudad': direccion_envio.ciudad,
            'estado': direccion_envio.estado,
            'codigo_postal': direccion_envio.codigo_postal,
        }

    checkout_session = stripe.checkout.Session.create(**stripe_params)
    return redirect(checkout_session.url)



from .models import Pedido, ExtraEnVenta, DireccionDeEnvio, Venta
from django.shortcuts import render

def success(request):
    cart = get_or_create_cart(request)
    direccion_id = request.session.get('direccion_envio_id')
    direccion_envio = DireccionDeEnvio.objects.filter(id=direccion_id).first()
    user = request.user if request.user.is_authenticated else None

    pedido = None
    if cart and cart.items.exists():
        pedido = Pedido.objects.create(
            cliente=user,
            direccion_envio=direccion_envio,
            pagado=True,
            session_key=cart.session_key if hasattr(cart, 'session_key') else None
        )

        for item in cart.items.all():
            venta = Venta.objects.create(
                pedido=pedido,
                business=item.producto.business,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.price,
                subtotal=item.subtotal(),
                direccion_envio=direccion_envio,
                cliente=user,
                pagado=True,
                nota=item.nota
            )

            for extra_carrito in item.extras_en_carrito.all():
                ExtraEnVenta.objects.create(
                    venta=venta,
                    extra=extra_carrito.extra,
                    cantidad=extra_carrito.cantidad,
                )

        cart.delete()
        request.session.pop('cart_id', None)
        request.session.pop('direccion_envio_id', None)

    # --- AQUI VIENE LA PARTE IGUAL A ver_pedidos_por_negocio ---
    pedido_data = {}
    if pedido:
        ventas_del_pedido = Venta.objects.filter(pedido=pedido).select_related(
            'producto', 'cliente', 'pedido', 'direccion_envio', 'business'
        ).prefetch_related('extras_en_venta__extra')

        d = pedido.direccion_envio
        direccion_data = None
        whatsapp = ""

        if d:
            direccion_data = {
                'fecha_creacion': d.fecha_creacion,
                'nombre_completo': d.nombre_completo,
                'telefono': d.telefono,
                'opcion_entrega': d.opcion_entrega,  # crudo para lógica
                'opcion_entrega_display': d.get_opcion_entrega_display(),  # para mostrar
                'direccion': d.direccion,
                'ciudad': d.ciudad,
                'estado': d.estado,
                'codigo_postal': d.codigo_postal,
                'propina_voluntaria': d.propina_voluntaria,
                'decidir_propina_despues': d.decidir_propina_despues,
                'notas': d.notas,
            }
            whatsapp = d.telefono

        ventas_info = []
        total_pedido = Decimal('0.00')
        productos_del_pedido = []

        for venta in ventas_del_pedido:
            extras_info = []
            for extra_rel in venta.extras_en_venta.all():
                extra = extra_rel.extra
                cantidad = extra_rel.cantidad
                subtotal_extra = extra.precio * cantidad
                extras_info.append({
                    'nombre': extra.nombre,
                    'precio': extra.precio,
                    'cantidad': cantidad,
                    'subtotal': subtotal_extra,
                })

            venta_subtotal = venta.subtotal
            total_pedido += venta_subtotal
            producto = venta.producto
            productos_del_pedido.append(producto)

            ventas_info.append({
                'producto': producto.name,
                'imagen': producto.image1.url if producto.image1 else None,
                'cantidad': venta.cantidad,
                'precio_unitario': venta.precio_unitario,
                'subtotal': venta_subtotal,
                'extras': extras_info or None,
                'negocio': venta.business.commercial_name,
                'nota': venta.nota,
            })

        # Costo de envío
        costo_envio = Decimal('0.00')
        if d and d.opcion_entrega == 'domicilio':
            if productos_del_pedido:
                todos_envio_gratis = all(p.tiene_envio_gratis for p in productos_del_pedido)
                if not todos_envio_gratis:
                    productos_con_envio = [p for p in productos_del_pedido if not p.tiene_envio_gratis]
                    costo_envio = max([p.precio_de_envio or 0 for p in productos_con_envio])
            total_pedido += costo_envio

        # Propina
        if d:
            total_pedido += d.propina_voluntaria or 0

        pedido_data = {
            'pedido': pedido,
            'direccion': direccion_data,
            'ventas': ventas_info,
            'total_pagado': total_pedido,
            'costo_envio': costo_envio,
            'whatsapp': whatsapp,
        }

    return render(request, 'success.html', {
        'pedido': pedido_data
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from decimal import Decimal

from .models import Business, Venta
from collections import defaultdict


@login_required
def ver_pedidos_por_negocio(request, business_id):
    business = get_object_or_404(Business, id=business_id, owner=request.user)

    ventas = Venta.objects.filter(business=business).exclude(pedido=None).select_related(
        'producto', 'cliente', 'pedido', 'direccion_envio'
    ).prefetch_related('extras_en_venta__extra')

    pedidos_dict = defaultdict(list)
    for venta in ventas:
        pedidos_dict[venta.pedido].append(venta)

    # Separar en pedidos pendientes y enviados
    pedidos_pendientes = []
    pedidos_enviados = []

    for pedido, ventas_del_pedido in pedidos_dict.items():
        d = pedido.direccion_envio
        direccion_data = None
        whatsapp = ""

        if d:
            direccion_data = {
                'fecha_creacion':d.fecha_creacion,
                'nombre_completo': d.nombre_completo,
                'telefono': d.telefono,
                'opcion_entrega': d.get_opcion_entrega_display(),
                'direccion': d.direccion,
                'ciudad': d.ciudad,
                'estado': d.estado,
                'codigo_postal': d.codigo_postal,
                'propina_voluntaria': d.propina_voluntaria,
                'notas': d.notas,
            }
            whatsapp = d.telefono

        ventas_info = []
        total_pedido = Decimal('0.00')
        productos_del_pedido = []

        for venta in ventas_del_pedido:
            extras_info = []
            for extra_rel in venta.extras_en_venta.all():
                extra = extra_rel.extra
                cantidad = extra_rel.cantidad
                subtotal_extra = extra.precio * cantidad
                extras_info.append({
                    'nombre': extra.nombre,
                    'precio': extra.precio,
                    'cantidad': cantidad,
                    'subtotal': subtotal_extra,
                })

            venta_subtotal = venta.subtotal
            total_pedido += venta_subtotal
            producto = venta.producto
            productos_del_pedido.append(producto)

            ventas_info.append({
                'producto': producto.name,
                'cantidad': venta.cantidad,
                'precio_unitario': venta.precio_unitario,
                'subtotal': venta_subtotal,
                'extras': extras_info or None,
                'negocio': venta.business.commercial_name,
                'nota': venta.nota,
            })

        # Calcular costo de envío cobrado al usuario
        costo_envio = Decimal('0.00')
        if d and d.opcion_entrega == 'domicilio':
            if productos_del_pedido:
                todos_envio_gratis = all(p.tiene_envio_gratis for p in productos_del_pedido)
                if not todos_envio_gratis:
                    productos_con_envio = [p for p in productos_del_pedido if not p.tiene_envio_gratis]
                    costo_envio = max([p.precio_de_envio or 0 for p in productos_con_envio])
            total_pedido += costo_envio

        # Propina
        if d:
            total_pedido += d.propina_voluntaria or 0

        pedido_data = {
            'pedido': pedido,
            'direccion': direccion_data,
            'ventas': ventas_info,
            'total_pagado': total_pedido,
            'costo_envio': costo_envio,
            'whatsapp': whatsapp,
        }

        if pedido.enviado:
            pedidos_enviados.append(pedido_data)
        else:
            pedidos_pendientes.append(pedido_data)

    return render(request, 'ver_pedidos.html', {
        'business': business,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_enviados': pedidos_enviados,
    })





@require_POST
@login_required
def marcar_envio_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar que el usuario es dueño del negocio al que pertenece al menos una venta del pedido
    if not pedido.ventas.filter(business__owner=request.user).exists():
        return HttpResponseForbidden("No tienes permiso para modificar este pedido.")

    pedido.enviado = 'enviado' in request.POST
    pedido.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))







