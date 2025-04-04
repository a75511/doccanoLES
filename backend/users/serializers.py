from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_polymorphic.serializers import PolymorphicSerializer


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    sex = serializers.CharField(source='userdata.sex', read_only=True)
    age = serializers.IntegerField(source='userdata.age', read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(source='userdata.created_by', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'is_staff', 'is_superuser', 'sex', 'age', 'created_by')

class UserPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        User: UserSerializer,
        **{cls.Meta.model: cls for cls in UserSerializer.__subclasses__()},
    }