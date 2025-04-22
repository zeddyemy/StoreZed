"""
This module defines the User model for the database.

It includes fields for the user's email, password, and other necessary information,
as well as methods for password hashing and verification.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""
from sqlalchemy import or_
from sqlalchemy.orm import Query, backref
from sqlalchemy import Index, CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .media import Media
from config import Config
from ..extensions import db
from ..utils.date_time import DateTimeUtils



class TempUser(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    
    def __repr__(self):
        return f'<ID: {self.id}, email: {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'date_joined': self.date_joined,
        }

# Define the User data model.
class AppUser(db.Model, UserMixin):
    __tablename__ = "app_user"
    
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    password_hash = db.Column(db.String(255), nullable=True)
    date_joined = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)

    # Relationships
    profile = db.relationship('Profile', back_populates="app_user", uselist=False, cascade="all, delete-orphan")
    address = db.relationship('Address', back_populates="app_user", uselist=False, cascade="all, delete-orphan")
    wallet = db.relationship('Wallet', back_populates="app_user", uselist=False, cascade="all, delete-orphan")
    customer_orders = db.relationship('CustomerOrder', back_populates='app_user', lazy='dynamic')
    payments = db.relationship('Payment', back_populates='app_user', lazy='dynamic')
    subscriptions = db.relationship('Subscription', back_populates='app_user', lazy='dynamic')
    
    roles = db.relationship('UserRole', back_populates='user', foreign_keys='UserRole.app_user_id', cascade="all, delete-orphan") # roles assigned to the user.
    assigned_roles = db.relationship('UserRole', back_populates='assigner', foreign_keys='UserRole.assigner_id', cascade="all, delete-orphan") # roles that the user has assigned to others
    
    
    #user_settings = db.relationship('UserSettings', back_populates='app_user', uselist=False, cascade='all, delete-orphan')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password) -> bool:
        """
        #This returns True if the password is same as hashed password in the database.
        """
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_2fa_enabled(self):
        return self.user_settings.is_2fa_enabled
    
    @property
    def wallet_balance(self):
        return self.wallet.balance
    
    @property
    def role_names(self) -> list[str]:
        """Returns a list of role names for the user."""
        if not db.inspect(self).persistent:
            # Reattach to session if necessary
            self = db.session.merge(self)
        return [str(user_role.role.name.value) for user_role in self.roles]
    
    @property
    def full_name(self):
        return f"{self.profile.firstname} {self.profile.lastname}"
    
    
    def __repr__(self):
        return f'<ID: {self.id}, username: {self.username}, email: {self.email}>'
    
    @staticmethod
    def add_search_filters(query: Query, search_term: str) -> Query:
        """
        Adds search filters to a SQLAlchemy query.
        """
        if search_term:
            search_term = f"%{search_term}%"
            
            # Join the Profile table using outerjoin to include users without a profile
            query = query.outerjoin(AppUser.profile)
            
            query = query.filter(
                    or_(
                        AppUser.username.ilike(search_term),
                        AppUser.email.ilike(search_term),
                        Profile.firstname.ilike(search_term),
                        Profile.lastname.ilike(search_term)
                    )
                )
        return query
    
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    def to_dict(self) -> dict:
        
        address_info = {}
        if self.address:
            address_info.update({
                'country': self.address.country,
                'state': self.address.state
            })
        
        profile_data = {}
        if self.profile:
            profile_data.update({
                'firstname': self.profile.firstname,
                'lastname': self.profile.lastname,
                'gender': self.profile.gender,
                'phone': self.profile.phone,
                'profile_picture': self.profile.profile_pic,
                'referral_link': self.profile.referral_link,
            })
        
        user_wallet = self.wallet
        wallet_info = {
            'balance': user_wallet.balance if user_wallet else None,
            'currency_name': user_wallet.currency_name if user_wallet else None,
            'currency_code': user_wallet.currency_code if user_wallet else None,
            'currency_symbol': user_wallet.currency_symbol if user_wallet else None,
        }
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_joined': self.date_joined,
            'wallet': wallet_info,
            'roles': self.role_names,
            **address_info,  # Merge address information
            **profile_data # Merge profile information
        }


class Profile(db.Model):
    __tablename__ = "profile"
    
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(200), nullable=True)
    lastname = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    profile_picture_id = db.Column(db.Integer(), db.ForeignKey('media.id'), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False,)
    app_user = db.relationship('AppUser', back_populates="profile")
    
    __table_args__ = (
        Index('ix_profile_firstname_trgm', 'firstname', postgresql_using='gin', postgresql_ops={'firstname': 'gin_trgm_ops'}),
        Index('ix_profile_lastname_trgm', 'lastname', postgresql_using='gin', postgresql_ops={'lastname': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return f'<profile ID: {self.id}, name: {self.firstname}>'
    
    @property
    def referral_link(self):
        return f'{Config.APP_DOMAIN_NAME}/signup/{self.app_user.username}'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    @property
    def profile_pic(self):
        if self.profile_picture_id:
            theImage = Media.query.get(self.profile_picture_id)
            if theImage:
                return theImage.get_path()
            else:
                return ''
        else:
            return ''
        
    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'gender': self.gender,
            'phone': self.phone,
            'profile_picture': self.profile_pic,
            'referral_link': f'{self.referral_link}',
        }


class Address(db.Model):
    __tablename__ = "address"
    
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False,)
    app_user = db.relationship('AppUser', back_populates="address")
    
    def __repr__(self):
        return f'<address ID: {self.id}, country: {self.country}, user ID: {self.user_id}>'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'state': self.state,
            'user_id': self.user_id
        }

