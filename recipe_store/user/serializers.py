from django.contrib.auth import get_user_model, authenticate
# while outputting msgs to the screen for langage conversion
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    # password is set using the set_password(), accept instance and validated_data
    def update(self, instance, validated_data):
        """Update a user, setting the passwordcorrectly and return it"""
        # very similar to get but after getting/retrieving value removes key from dictionary
        # and needs a default value like None instead of password
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        # if user provideda new passowrd
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    # validates that the inputs are correct Field type and authenticates values

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            # _ used: convert into any other language if need be in future
            msg = _('Unable to authenticate with provided credentials')
            # sends a http 400 response
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
