from django.contrib.auth import authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from anpr_app.models import User, VehicleOwner


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'gender', 'contact',)
        extra_kwargs = {'password': {'write_only': True}}   
    
    def validate_email(self, data):
        user_query = User.objects.filter(email__iexact=data).exists()
        if user_query:
            raise serializers.ValidationError(f'{data} already exist!')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs, *args, **kwargs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(username=email, password=password)
        qs = User.objects.filter(email__iexact=email).exists()
        if qs is None:
            raise serializers.ValidationError(f'Sorry {email} does not exist.')
        if not user:
            raise serializers.ValidationError('Incorrect email or password.')
        return super(SigninSerializer, self).validate(attrs, *args, **kwargs)


class ProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'contact',)

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.gender = validated_data['gender']
        instance.contact = validated_data['contact']
        instance.save()
        return super(ProfileUpdateSerializer, self).update(instance, validated_data)

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password fields didn't match.")
        return super(ChangePasswordSerializer, self).validate(attrs)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return super(ChangePasswordSerializer, self).validate(value)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance  