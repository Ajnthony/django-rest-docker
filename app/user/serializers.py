"""
serializers for user api view
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    # serializer for the user object

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        # create and return a new user with encrypted password
        return get_user_model().objects.create_user(**validated_data)

    # instance: model instance that's going to be updated
    # validated_data: data that got passed in
    def update(self, instance, validated_data):
        # update and return the user

        # update password is optional
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    # serializer for the user auth token
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attributes):
        # validate and authenticate the user
        email = attributes.get('email')
        password = attributes.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate the user with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attributes['user'] = user
        return attributes
