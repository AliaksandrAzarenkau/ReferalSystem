import random
import string
import time

from django.contrib.auth import login

from config import AUTH_CODE_LENGTH, INVITE_CODE_LENGTH
from user.models import UserProfile
from user.serializers import UserSerializer
from user.authentication import AuthBackend

key_holder = dict()


def parse_phone_number(data: str) -> int:
    result = ''

    for _ in data:
        if _.isdigit():
            result += _

    return int(result)


def get_own_invite_code() -> str:
    all_symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits

    while True:
        result = ''.join(random.choice(all_symbols) for _ in range(INVITE_CODE_LENGTH))
        if not UserProfile.objects.filter(own_invite_code=result).exists():
            break
    return result


def auth_request_handler(request, phone_number: str, auth_code=None) -> None:
    if auth_code == None:
        auth_code = request.data.get("authentication_code")
    if key_holder[phone_number] != auth_code:
        return {'message': 'Wrong authentication code'}

    phone_number = parse_phone_number(str(phone_number))

    if not UserProfile.objects.filter(phone_number=phone_number).exists():
        UserSerializer(phone_number)
        if UserSerializer.is_valid:
            UserSerializer.create(request, phone_number=phone_number)

    user = UserProfile.objects.get(phone_number=phone_number)
    AuthBackend.authenticate(user)
    login(request, user=user)

    return {'message': 'Accepted'}


def auth_code_gen(request, phone=None) -> str:
    result = ''.join(random.choice(string.digits) for _ in range(AUTH_CODE_LENGTH))

    if phone is None:
        phone = request.data.get('phone_number')
        phone = parse_phone_number(phone)

    key_holder[phone] = result

    time.sleep(1)

    return result
