"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from sqlalchemy import inspect, or_
from sqlalchemy.orm import backref
from sqlalchemy.orm import Query

from ..extensions import db
from .media import Media
from .product import Product, product_category
from ..utils.date_time import DateTimeUtils, datetime

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description  = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(80), nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    children = db.relationship("Category", backref=backref("parent", remote_side=[id]), lazy=True)
    
        
    def __repr__(self):
        return f"<Cat ID: {self.id}, name: {self.name}, parent: {self.parent_id}>"
    
    @staticmethod
    def add_search_filters(query: Query, search_term: str) -> Query:
        """
        Adds search filters to a SQLAlchemy query.
        """
        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(
                    or_(
                        Category.name.ilike(search_term),
                        Category.slug.ilike(search_term),
                    )
                )
        return query
    
    @classmethod
    def create_category(cls, name, slug, description="", media_id=None, commit=True, **kwargs):
        category = cls(name=name, description=description, slug=slug, media_id=media_id, **kwargs)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(category, key, value)
        
        db.session.add(category)
        
        if commit:
            db.session.commit()
        
        return category
    
    def get_thumbnail(self):
        media: Media = Media.query.get(self.media_id)
        return media.get_path() if media else None
    
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
    
    def to_dict(self, include_children=False) -> dict[str, any]:
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "slug": self.slug,
            "parent_id": self.parent_id
            }
        if include_children:
            data["children"] = [child.to_dict() for child in self.children]
        return data

