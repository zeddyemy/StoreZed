from sqlalchemy import inspect
from sqlalchemy.orm import backref
from datetime import datetime
from flask import url_for

from ..extensions import db
from .media import Media

class NavigationBarItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, nullable=True, default=0)
    visible = db.Column(db.Boolean, default=True)
    icon_class = db.Column(db.String(100), nullable=True, default='bx-pie-chart')  # For icon libraries
    icon_path = db.Column(db.String(500), nullable=True)  # For custom images
    parent_id = db.Column(db.Integer, db.ForeignKey('navigation_bar_item.id'))
    submenus = db.relationship('NavigationBarItem')
    
    
    def __repr__(self):
        return f'<Nav ID: {self.id}, name: {self.name}, visible: {self.visible}>'
    
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
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "link": self.link,
            "order": self.order,
            "visible": self.visible,
            "icon_class": self.icon_class,
            "icon_path": self.icon_path,
            "parent_id": self.parent_id,
        }




def create_nav_items(clear: bool = False) -> None:
    default_items = [
            {
                "name": 'Dashboard',
                "link": url_for('web_front.index'),
                "order": 0,
                "visible": True,
            },
            {
                "name": 'Add Balance',
                "link": url_for('web_front.top_up'),
                "order": 1,
                "visible": True
            },
            {
                "name": 'Orders',
                "link": url_for('web_front.orders'),
                "order": 2,
                "visible": True
            },
            {
                "name": 'Sign Out',
                "link": url_for('web_front.logout'),
                "order": 99,
                "visible": True
            }
        ]
    
    if inspect(db.engine).has_table('navigation_bar_item'):
        if clear:
            NavigationBarItem.query.delete()
            db.session.commit()
        
        new_items = []
        for nav_item in default_items:
            if not NavigationBarItem.query.filter_by(name=nav_item['name']).first():
                new_nav_item = NavigationBarItem(name=nav_item['name'], link=nav_item['link'], order=nav_item['order'], visible=nav_item['visible'])
                new_items.append(new_nav_item)
        
        if new_items:
            db.session.bulk_save_objects(new_items)
            db.session.commit()
    