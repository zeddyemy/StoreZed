"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (StringField, EmailField, PasswordField, SelectField, HiddenField, ValidationError)
from wtforms.validators import DataRequired, EqualTo, Length, Email, Regexp

from ....models import AppUser
from ...helpers.roles import get_role_names


class AdminAddUserForm(FlaskForm):
    """form for the admin to add new user of the dashboard"""
    username = StringField(
        'Username', validators=[DataRequired()]
    )
    email = EmailField(
        'Email address', validators=[DataRequired(), Email()]
    )
    firstname = StringField(
        'First Name', validators=[
            DataRequired(),
            Length(3, 50, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Please Make sure you typed your name correctly",
            )
        ]
    )
    lastname = StringField(
        'Last Name', validators=[
            DataRequired(),
            Length(3, 50, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Please Make sure you typed your name correctly",
            )
        ]
    )
    
    password = PasswordField(
        'Password', validators=[DataRequired()]
    )
    
    role = SelectField(
        'role',
        choices=get_role_names,
        validate_choice=False
    )
    existingEmail = HiddenField()
    existingUsername = HiddenField()
    
    def validate_email(self, email):
        if AppUser.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered!")

    def validate_username(self, username):
        if AppUser.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken!")


