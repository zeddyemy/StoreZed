from sqlalchemy import inspect
from sqlalchemy.orm import backref
from sqlalchemy.orm import Query
from flask import url_for

from ..extensions import db
from ..utils.date_time import DateTimeUtils
from .media import Media

class NavigationBarItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), nullable=False, unique=True)  # e.g., "home", "products"
    url = db.Column(db.String(500), nullable=True)
    order = db.Column(db.Integer, nullable=True, default=0)
    is_active = db.Column(db.Boolean, default=True)  # Toggle visibility
    icon_class = db.Column(db.String(100), nullable=True, default='bx-pie-chart')  # For icon libraries
    icon_path = db.Column(db.String(500), nullable=True)  # For custom images
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)
    
    # relationships
    parent_id = db.Column(db.Integer, db.ForeignKey('navigation_bar_item.id'), nullable=True) # Self-referential foreign key
    children = db.relationship('NavigationBarItem', backref=backref('parent', remote_side=[id]), lazy=True)
    
    
    def __repr__(self):
        return f'<Nav ID: {self.id}, name: {self.name}, is_active: {self.is_active}>'
    
    @classmethod
    def create(cls, name, url, order=0, is_active=True, parent_id=None, commit=True):
        from slugify import slugify
        nav_item = cls(name=name, slug=slugify(name), url=url, order=order, is_active=is_active)
        db.session.add(nav_item)
        if commit:
            db.session.commit()
        return nav_item
    
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
    
    def to_dict(self, include_children=False):
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "url": self.url,
            "order": self.order,
            "is_active": self.is_active,
            "icon_class": self.icon_class,
            "icon_path": self.icon_path,
            "parent_id": self.parent_id,
        }
        
        if include_children:
            data['children'] = [child.to_dict() for child in self.children]
        return data




def create_nav_items(clear: bool = False) -> None:
    from slugify import slugify
    default_items = [
            {
                "name": 'Dashboard',
                "url": url_for('web_front.index'),
                "order": 0,
                "is_active": True,
            },
            {
                "name": 'Add Balance',
                "url": url_for('web_front.top_up'),
                "order": 1,
                "is_active": True
            },
            {
                "name": 'Orders',
                "url": url_for('web_front.orders'),
                "order": 2,
                "is_active": True
            },
            {
                "name": 'Sign Out',
                "url": url_for('web_front.logout'),
                "order": 99,
                "is_active": True
            }
        ]
    
    if inspect(db.engine).has_table('navigation_bar_item'):
        if clear:
            NavigationBarItem.query.delete()
            db.session.commit()
        
        new_items = []
        for nav_item in default_items:
            if not NavigationBarItem.query.filter_by(name=nav_item['name']).first():
                new_nav_item = NavigationBarItem(name=nav_item['name'], slug=slugify(nav_item['name']), url=nav_item['url'], order=nav_item['order'], is_active=nav_item['is_active'])
                new_items.append(new_nav_item)
        
        if new_items:
            db.session.bulk_save_objects(new_items)
            db.session.commit()
    