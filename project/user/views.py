from django.shortcuts import render, redirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.services import auth_request_handler, auth_code_gen, key_holder, parse_phone_number
from user.serializers import UserSerializer


class LoginAPIView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['phone_number'],
        ),
        responses={200: 'Success'}
    )
    def post(self, request):
        """
        Запрос кода подтверждения по номеру телефона
        """

        phone_number = request.data.get('phone_number')
        if phone_number is None or len(phone_number) == 0:
            return Response({'message': 'phone number cannot be empty'}, status=status.HTTP_200_OK)

        response = auth_code_gen(request)

        # Т.к. имитация общения с сервисом, чтобы не хранить код подтверждения в БД
        phone_number = parse_phone_number(request.data.get('phone_number'))
        request.session['phone_number'] = phone_number

        return Response({'authentication_code': response}, status=status.HTTP_200_OK)


class AuthenticationAPIView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'authentication_code': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['authentication_code'],
        ),
        responses={200: 'Success'}
    )
    def post(self, request):
        """
        Запрос на аутентификацию по коду подтверждения
        """
        phone_number = request.session['phone_number']
        result = auth_request_handler(request, phone_number)

        return Response(result)


class UserProfileAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer = UserSerializer

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                "own_invite_code": openapi.Schema(type=openapi.TYPE_STRING),
                "activated_invite_code": openapi.Schema(type=openapi.TYPE_STRING),
                "activated_users": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        )},
    )
    def get(self, request):
        """
        Запрос профиля пользователя
        """
        result = self.serializer.get(request, request.user)

        return Response({'user_profile': result}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'invite_code': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['invite_code'],
        ),
        responses={200: 'Success'}
    )
    def post(self, request):
        """
        Запрос на активацию инвайт-кода
        """
        user = request.user
        result = self.serializer.update(user, request)

        return Response(result, status=status.HTTP_200_OK)


"""Эндпоинты для части с шаблонами"""


@permission_classes([AllowAny])
def get_signup_page(request):
    """
    Запрос кода подтверждения по номеру телефона
    """
    if request.method == 'GET':
        return render(request, template_name='signup.html')
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if not phone_number:
            result = {'message': f'You must provide phone number'}

            return render(request, template_name='signup.html', context=result)

        phone_number = parse_phone_number(phone_number)
        request.session['phone_number'] = phone_number

        auth_code_gen(request, phone_number)

        return redirect('auth')


@permission_classes([AllowAny])
def authentication(request):
    """
    Запрос на аутентификацию по коду подтверждения
    """
    if request.method == 'GET':
        phone_number = request.session['phone_number']
        auth_code = key_holder[phone_number]

        context = {'auth_code': auth_code}

        return render(request, template_name='auth.html', context=context)

    if request.method == 'POST':
        auth_code = request.POST.get('auth_code')
        phone_number = request.session['phone_number']
        original_code = key_holder[phone_number]

        if auth_code != original_code:
            result = {'message': 'Wrong code', 'auth_code': original_code}

            return render(request, template_name='auth.html', context=result)

        auth_request_handler(request, phone_number, auth_code)

        return redirect('profile')


@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        """
        Запрос профиля пользователя
        """
        context = UserSerializer.get(request, request.user)

        return render(request, template_name='profile.html', context=context)

    if request.method == 'POST':
        """
        Запрос на активацию инвайт-кода
        """
        invite_code = request.POST.get('invite_code')
        if not invite_code:
            result = {'message': f'You must provide an invite code'}

            return render(request, template_name='profile.html', context=result)

        message = UserSerializer.update(request, request, invite_code).get('message')
        result = {'message': message}

        return render(request, template_name='profile.html', context=result)
