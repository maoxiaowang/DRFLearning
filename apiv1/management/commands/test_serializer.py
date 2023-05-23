from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        from apiv1.serializers import UserSerializer
        serializer = UserSerializer(data={
            'username': 'user1', 'password1': '123456', 'password2': '123456',
            'profile': {
                'age': 11
            }
        })
        is_valid = serializer.is_valid()
        print(is_valid)
        print(serializer.errors)
        print(serializer.validated_data)
