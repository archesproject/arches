from django.contrib.auth.models import User
from django.contrib.auth.models import Group


def add_users():
    profiles = (
        {
            "name": "ben",
            "email": "ben@test.com",
            "password": "Test12345!",
            "groups": ["Graph Editor", "Resource Editor"],
        },
        {
            "name": "sam",
            "email": "sam@test.com",
            "password": "Test12345!",
            "groups": ["Graph Editor", "Resource Editor", "Resource Reviewer"],
        },
        {
            "name": "jim",
            "email": "jim@test.com",
            "password": "Test12345!",
            "groups": ["Graph Editor", "Resource Editor"],
        },
    )

    for profile in profiles:
        try:
            user = User.objects.create_user(
                username=profile["name"],
                email=profile["email"],
                password=profile["password"],
            )
            user.save()

            for group_name in profile["groups"]:
                group = Group.objects.get(name=group_name)
                group.user_set.add(user)

        except Exception as e:
            print(e)
