"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
"""

from .auth import SignUpForm, LoginForm
from .web_admin.tags import TagForm
from .web_admin.users import AdminAddUserForm
from .web_admin.products import AddProductForm
from .web_admin.categories import CategoryForm
from .web_admin.settings import GeneralSettingsForm
from .web_admin.payment_methods import BacsPaymentForm, CodPaymentForm, CheckPaymentForm, GatewayPaymentForm