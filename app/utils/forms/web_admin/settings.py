"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, TextAreaField, SelectField, HiddenField, SelectMultipleField, SubmitField, ValidationError, widgets)
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, Optional, Email, Regexp
from flask_wtf.file import FileField, FileAllowed

from ....models.payment_gateway import PaymentGateway, PaymentGatewayName

def get_day_choices(include_default: bool = True) -> list[tuple[str, str]]:
    """
    Return a list of (id, name) tuples for days of the week.
    
    If `include_default` is True, prepend ("", "— Select day —").
    """
    days = [
        ("0", "Sunday"),
        ("1", "Monday"),
        ("2", "Tuesday"),
        ("3", "Wednesday"),
        ("4", "Thursday"),
        ("5", "Friday"),
        ("6", "Saturday"),
    ]
    
    choices = [("", "— Select day —")] + days if include_default else days

    return choices


class GeneralSettingsForm(FlaskForm):
    site_title = StringField('Site Title', validators=[InputRequired()])
    tagline = StringField('Tagline', validators=[], description="In a few words, explain what this site is about. Example: “Just another E-Commerce site.”")
    admin_email = StringField('Administration Email Address', description="This address is used for admin purposes. If you change this, an email will be sent to your new address to confirm it. The new address will not become active until confirmed.")
    timezone = StringField('Timezone')
    week_starts_on = SelectField('Week Starts On', choices=[], coerce=int, validate_choice=False)
    
    # Currency Settings
    currency = StringField("Currency (e.g., NGN, USD, EUR)", validators=[])
    currency_position = SelectField("Currency Position", choices=[
        ("left", "Left ($100)"),
        ("right", "Right (100$)"),
        ("left_space", "Left with space ($ 100)"),
        ("right_space", "Right with space (100 $)")
    ], validators=[InputRequired()])
    thousand_separator = StringField("Thousand Separator")
    decimal_separator = StringField("Decimal Separator")
    number_of_decimals = SelectField("Number of Decimals", choices=[
        ("0", "0"), ("1", "1"), ("2", "2"), ("3", "3")
    ], validators=[InputRequired()])
    
    submit = SubmitField('Save Changes')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_starts_on.choices = get_day_choices(False)


class PaymentSettingsForm(FlaskForm):
    pass