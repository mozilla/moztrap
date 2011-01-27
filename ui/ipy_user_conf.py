"""
Makes IPython import all of your projects models when shell is started.

1. Save as ipy_user_conf.py in project root
2. ./manage.py shell
3. profit

"""

import IPython.ipapi
ip = IPython.ipapi.get()


def main():
    print "\nImported:\n\n"
    
    imports = [
        "from tcmui.core.api import admin, Credentials",
        "from tcmui.core.models import Company, CompanyList",
        "from tcmui.users.models import User, UserList, Role, RoleList, Permission, PermissionList",
        "from tcmui.products.models import Product, ProductList",
        ]
        
    for imp in imports:
        ip.ex(imp)
        print imp

    print "\n"

main()
