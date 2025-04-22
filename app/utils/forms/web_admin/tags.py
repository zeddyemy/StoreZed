"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, TextAreaField, SelectField, HiddenField, SelectMultipleField, ValidationError, widgets)
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, Optional, Email, Regexp
from flask_wtf.file import FileField, FileAllowed

from ....models.product import Tag


class TagForm(FlaskForm):
    """
    form to add new tag
    """
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=30)])
    description = TextAreaField('description')
    
