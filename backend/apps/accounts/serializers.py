from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Permite login com username ou email no mesmo campo do formulário.

    O frontend envia sempre o valor no campo ``username``. O Simple JWT padrão
    autentica apenas pelo username do modelo, por isso emails como
    ``admin@abiptom.gw`` eram rejeitados mesmo quando pertenciam ao admin.
    """

    def validate(self, attrs):
        login_value = attrs.get(self.username_field)
        if login_value and '@' in login_value:
            user = (
                User.objects.filter(email__iexact=login_value.strip())
                .only('username')
                .first()
            )
            if user:
                attrs[self.username_field] = user.get_username()
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name', read_only=True, default=None)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_arn_admin = serializers.BooleanField(read_only=True)
    is_arn_staff = serializers.BooleanField(read_only=True)
    is_operator_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'operator', 'operator_name',
            'phone', 'position', 'is_active', 'date_joined',
            'is_arn_admin', 'is_arn_staff', 'is_operator_user',
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
    is_arn_admin = serializers.BooleanField(read_only=True)
    is_arn_staff = serializers.BooleanField(read_only=True)
    is_operator_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'operator', 'operator_name',
            'operator_code', 'operator_type', 'phone', 'position',
            'is_arn_admin', 'is_arn_staff', 'is_operator_user',
        ]
        read_only_fields = [
            'id', 'username', 'role', 'operator',
        ]
