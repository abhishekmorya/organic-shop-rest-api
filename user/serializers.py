from core import models
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = get_user_model()

        fields = ['email', 'name', 'password']

        extra_kwargs = {
            'password': {
                'write_only': True, 
                'min_length': 5,
                'style': {'input_type': 'password'}
            },
        }
    
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""

        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Setting the password correctly and return it"""

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserTokenSerializer(serializers.Serializer):
    """Serializer for user token for authorization"""

    email = serializers.CharField()
    password = serializers.CharField(
        style = {'input_type': 'password'},
        trim_whitespace = False
    )

    def validate(self, attr):
        """
        Override the validate behaviour of super class to 
        authenticate the user before providing authentication token
        """
        email = attr.get('email')
        password = attr.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username = email,
            password = password,
        )

        if not user:
            raise serializers.ValidationError("Unable to authenticate with provided details")

        attr['user'] = user
        return attr


class UserAddressSerializer(serializers.ModelSerializer):
    """Serializer class for UserAddress object"""

    class Meta:
        model = models.UserAddress
        fields = (
            'id',
            'name',
            'line1',
            'line2',
            'city',
            'district',
            'state',
            'pincode',
            'addressType',
        )
        read_only_fields = ('id',)


class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer class for UserDetails object"""

    class Meta:
        model = models.UserDetails
        fields = ('selectedAddress',)
