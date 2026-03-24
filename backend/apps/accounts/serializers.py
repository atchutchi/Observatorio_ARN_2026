from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True, default=None)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'operator', 'operator_name',
            'phone', 'position', 'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'role', 'operator', 'phone', 'position',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True, default=None)
    operator_code = serializers.CharField(source='operator.code', read_only=True, default=None)
    operator_type = serializers.CharField(
        source='operator.operator_type.code', read_only=True, default=None
    )
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'operator', 'operator_name',
            'operator_code', 'operator_type', 'phone', 'position',
        ]
        read_only_fields = [
            'id', 'username', 'role', 'operator',
        ]
