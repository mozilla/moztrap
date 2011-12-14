def refresh(obj):
    return obj.__class__._base_manager.get(pk=obj.pk)



user_number = 1

def create_user(**kwargs):
    global user_number

    password = kwargs.pop("password", None)
    if "username" not in kwargs:
        kwargs["username"] = "test%s" % user_number
        user_number += 1

    from django.contrib.auth.models import User

    user = User(**kwargs)
    if password:
        user.set_password(password)
    user.save()
    return user



def create_product(**kwargs):
    from cc.core.models import Product

    defaults = {
        "name": "Test Product",
        "description": "",
        }

    defaults.update(kwargs)

    return Product.objects.create(**defaults)
