"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, TextAreaField, SelectField, HiddenField, SelectMultipleField, ValidationError, widgets)
from wtforms.validators import InputRequired, DataRequired, EqualTo, Length, Optional, Email, Regexp
from flask_wtf.file import FileField, FileAllowed

from ...helpers.category import get_category_choices
from ....models.category import Category


class CategoryForm(FlaskForm):
    """
    form to add new category
    """
    name = StringField('name', validators=[InputRequired(), Length(min=1, max=30)])
    description = TextAreaField('description')
    parent_cat = SelectField('parent_cat', choices=[], validate_choice=False)
    cat_img = FileField('Category Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_cat.choices = get_category_choices()
