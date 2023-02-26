from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()
class CustomAuth(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            if 'username' in kwargs and kwargs['username'] is not None and email is None:
                email = kwargs['username']
            user = UserModel.objects.get(Q(username__iexact=email) | Q(email__iexact=email))
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
       
        