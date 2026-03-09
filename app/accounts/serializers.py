import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

User = get_user_model()


def validate_password(password):
    password_regex = re.compile(r'^(?=.*[a-z])(?=.*[0-9]).{8,}$')
    if not password_regex.match(password):
        raise serializers.ValidationError(_('Password must be alphanumeric and 8 caracters'))
    
def validate_username(username):
    username_regex = re.compile(r'^\w+$')
    if not username_regex.match(username):
        raise serializers.ValidationError(_('The username only allows letters, numbers, and underscores.'))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'email', 'password']
        
    username = serializers.CharField(max_length=150, min_length=4, validators=[UniqueValidator(queryset=User.objects.all(), message=_('This username already exists.'))])
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message=_('This email address is being used by another user.'))])
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        if password is not None:
            instance.set_password(password)
            instance.save()

        return instance
