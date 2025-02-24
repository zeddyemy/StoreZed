import uuid
from flask import request
from sqlalchemy import inspect, or_
from sqlalchemy.orm import backref
from sqlalchemy.orm import Query

from app.extensions import db
from .media import Media
from ..utils.helpers.loggers import console_log
from ..utils.date_time import DateTimeUtils, datetime


# association table for the many-to-many relationship between products and categories
product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

# association table for the many-to-many relationship between products and tags
product_tag = db.Table('product_tag',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=uuid.uuid4)
    name = db.Column(db.String(50), nullable=False)
    description  = db.Column(db.String(300), nullable=True)
    selling_price = db.Column(db.Integer, nullable=True)
    actual_price = db.Column(db.Integer, nullable=True)
    sizes = db.Column(db.String(300), nullable=True)
    colors = db.Column(db.String(), nullable=True)
    slug = db.Column(db.String(), nullable=False, unique=True)
    pub_status = db.Column(db.String(), nullable=False, default='draft')
    date_created = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=True,)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    
    app_user = db.relationship('AppUser', backref=db.backref('products', lazy='dynamic'))
    tags = db.relationship('Tag', secondary=product_tag, backref=db.backref('products', lazy='dynamic'))
    categories = db.relationship('Category', secondary=product_category, backref=db.backref('products', lazy='dynamic'))
    
    
    def __repr__(self):
        return f'<Product ID: {self.id}, name: {self.name}, category Id: {self.category_id}>'
    
    @staticmethod
    def add_search_filters(query: Query, search_term: str) -> Query:
        """
        Adds search filters to a SQLAlchemy query.
        """
        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.slug.ilike(search_term),
                    )
                )
        return query
    
    @classmethod
    def create_product(cls, uuid, name, slug, user_id, commit=True, **kwargs):
        product = cls(uuid=uuid, name=name, slug=slug, user_id=user_id)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            
            if key == 'tags' and value:
                if isinstance(value, (list, tuple)):
                    product.tags.extend(value)
                else:
                    product.tags.append(value)
            elif key == 'categories' and value:
                if isinstance(value, (list, tuple)):
                    console_log('categories', value)
                    console_log('product.categories', product.categories)
                    product.categories.extend(value)
                    console_log('product.categories after', product.categories)
                else:
                    product.categories.append(value)
            else:
                setattr(product, key, value)
        
        product = db.session.merge(product)
        db.session.add(product)
        
        if commit:
            db.session.commit()
        
        return product
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.query(product_category).filter_by(product_id=self.id).delete()
        db.session.query(product_tag).filter_by(product_id=self.id).delete()
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    def get_media(self):
        if self.media_id:
            the_media = Media.query.get(self.media_id)
            if the_media:
                return the_media.get_path()
            else:
                return None
        else:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sellingPrice': self.selling_price,
            'actualPrice': self.actual_price,
            'sizes': self.sizes,
            'colors': self.colors,
            'slug': self.slug,
            'category_id': self.category_id
        }


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(), nullable=False, unique=True)
    
    @staticmethod
    def add_search_filters(query: Query, search_term: str) -> Query:
        """
        Adds search filters to a SQLAlchemy query.
        """
        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(
                    or_(
                        Tag.name.ilike(search_term),
                        Tag.slug.ilike(search_term),
                        Tag.description.ilike(search_term),
                    )
                )
        return query
    
    @classmethod
    def create_tag(cls, name, slug, commit=True, **kwargs):
        tag = cls(name=name, slug=slug, **kwargs)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(tag, key, value)
        
        if commit:
            db.session.merge(tag)
            db.session.add(tag)
            db.session.commit()
        
        return tag
    
    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.merge(self)
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
        }


class productVariations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    name = db.Column(db.String(100), nullable=False)
    selling_price = db.Column(db.Integer, nullable=True)
    img_url = db.Column(db.String(), nullable=True)
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'selling_price': self.selling_price,
            'img_url': self.img_url,
            'product_id': self.product_id
        }

