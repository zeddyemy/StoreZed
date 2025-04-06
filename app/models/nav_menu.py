from sqlalchemy import inspect
from sqlalchemy.orm import backref
from sqlalchemy.orm import Query
from flask import url_for

from ..extensions import db
from ..utils.date_time import DateTimeUtils
from .media import Media

class NavigationMenu(db.Model):
    __tablename__ = 'navigation_menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    
    # A menu can have multiple items (ordered by a provided order)
    items = db.relationship(
        'NavMenuItem', 
        backref='menu', 
        lazy=True, 
        cascade="all, delete-orphan", 
        order_by="NavMenuItem.order"
    )

    def __repr__(self):
        return f"<NavigationMenu {self.name}>"
    
    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    def to_dict(self, include_items=False, items_children=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }
        
        if include_items:
            data['items'] = [
                item.to_dict(include_children=items_children)
                for item in self.items
            ]
        
        return data

class NavMenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('navigation_menu.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(100), nullable=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)  # e.g., "home", "products"
    url = db.Column(db.String(500), nullable=True)
    item_type = db.Column(db.String(50), nullable=False, default="custom")  # e.g., 'category', 'custom', 'page'
    ref_id = db.Column(db.Integer, nullable=True)
    order = db.Column(db.Integer, nullable=True, default=0)
    is_active = db.Column(db.Boolean, default=True)  # Toggle visibility
    icon_class = db.Column(db.String(100), nullable=True, default='bx-pie-chart')  # For icon libraries
    icon_path = db.Column(db.String(500), nullable=True)  # For custom images
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)
    
    # relationships
    parent_id = db.Column(db.Integer, db.ForeignKey('nav_menu_item.id'), nullable=True) # Self-referential foreign key
    children = db.relationship('NavMenuItem', backref=backref('parent', remote_side=[id]), lazy=True)
    
    
    def __repr__(self):
        return f'<NavMenuItem ID: {self.id}, name: {self.name} (Type: {self.item_type}), is_active: {self.is_active}>'
    
    @classmethod
    def create(cls, name, label, url, order=0, is_active=True, parent_id=None, commit=True, **kwargs):
        from ..utils.helpers.basics import generate_slug
        slug = generate_slug(name, NavMenuItem)
        
        label = label if label else name
        
        nav_item = cls(name=name, label=label, slug=slug, url=url, order=order, is_active=is_active, parent_id=parent_id)
        
        for key, value in kwargs.items():
            setattr(nav_item, key, value)
        
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
            "label": self.label,
            "slug": self.slug,
            "url": self.url,
            "order": self.order,
            "item_type": self.item_type,
            "ref_id": self.ref_id,
            "is_active": self.is_active,
            "icon_class": self.icon_class,
            "icon_path": self.icon_path,
            "parent_id": self.parent_id,
        }
        
        if include_children:
            data['children'] = [
                child.to_dict(include_children)
                for child in sorted(self.children, key=lambda x: x.order)
                if child.is_active
            ]
        return data



"""
def create_menu_items(clear: bool = False) -> None:
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
    
    if inspect(db.engine).has_table('menu_item'):
        if clear:
            NavMenuItem.query.delete()
            db.session.commit()
        
        new_items = []
        for menu_item in default_items:
            if not NavMenuItem.query.filter_by(name=menu_item['name']).first():
                new_nav_item = NavMenuItem(name=menu_item['name'], slug=slugify(menu_item['name']), url=menu_item['url'], order=menu_item['order'], is_active=menu_item['is_active'])
                new_items.append(new_nav_item)
        
        if new_items:
            db.session.bulk_save_objects(new_items)
            db.session.commit()
"""