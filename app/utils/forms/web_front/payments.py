"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, IntegerField, TextAreaField, SelectField, HiddenField, SelectMultipleField, SubmitField, ValidationError, widgets)
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, Optional, Email, Regexp
from flask_wtf.file import FileField, FileAllowed

from ....models.payment_gateway import PaymentGateway, PaymentGatewayName
from ....enums.payments import PaymentMethods, PaymentGatewayName
from ...helpers.settings import get_payment_method_settings
from ...helpers.loggers import console_log
from ...payments.utils import get_payment_providers

class TopUpForm(FlaskForm):
    amount = IntegerField("Amount", validators=[InputRequired()])
    submit = SubmitField("Pay")