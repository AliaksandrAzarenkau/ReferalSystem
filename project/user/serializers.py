from rest_framework import serializers

from user import services
from user.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    def get(self, user):
        users_activated_list = []
        profile = UserProfile.objects.get(phone_number=user)
        own_code = profile.own_invite_code
        activated_users = UserProfile.objects.filter(activated_invite_code=own_code)

        if len(activated_users) > 0:
            for _ in activated_users:
                users_activated_list.append(_.phone_number)

        response = {
            'phone_number': profile.phone_number,
            'own_invite_code': own_code,
            'activated_invite_code': profile.activated_invite_code,
            'activated_users': users_activated_list
        }

        return response

    def create(self, phone_number):
        new_user = UserProfile(
            phone_number=phone_number,
            own_invite_code=services.get_own_invite_code()
        )

        new_user.save()

        return new_user

    def update(self, request, invite_code=None):
        user = request.user
        user_profile = UserProfile.objects.get(phone_number=user)
        current_code = user_profile.activated_invite_code

        if not invite_code:
            invite_code = request.data.get('invite_code')

        if not UserProfile.objects.filter(own_invite_code=invite_code).exists():
            message = {'message': f'Wrong invite code'}
            return message

        if invite_code == user_profile.own_invite_code:
            message = {'message': f'Own invite code cannot be activated'}
            return message

        if current_code:
            message = {'message': f'Invite code {current_code} already activated'}
            return message

        user_profile.activated_invite_code = invite_code
        user_profile.save(update_fields=['activated_invite_code'])

        message = {'message': f'Invite code successfully activated'}

        return message

    class Meta:
        model = UserProfile
        fields = '__all__'
