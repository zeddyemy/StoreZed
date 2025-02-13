"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from sqlalchemy.orm import backref

from ..extensions import db
from .media import Media
from .product import Product, product_category
from ..utils.date_time import DateTimeUtils, datetime

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description  = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(), nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    children = db.relationship('Category', backref=backref('parent', remote_side=[id]), lazy=True)
    

        
    def __repr__(self):
        return f'<Cat ID: {self.id}, name: {self.name}, parent: {self.parent_id}>'
    
    
    @classmethod
    def create_category(cls, name, slug, description='', media_id=None, commit=True, **kwargs):
        category = cls(name=name, description=description, slug=slug, media_id=media_id, **kwargs)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(category, key, value)
        
        if commit:
            db.session.add(category)
            db.session.commit()
        
        return category
    
    def get_thumbnail(self):
        media: Media = Media.query.get(self.media_id)
        return media.get_path() if media else None
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

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
            'description': self.description,
            'slug': self.slug,
            }

