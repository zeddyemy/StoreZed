"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from collections import Counter
from flask import request, jsonify, current_app
from sqlalchemy import desc, func, text
from flask_login import current_user

from ...extensions import db
from ...models import Tag
from config import Config
from .basics import int_or_none, generate_slug
from .loggers import log_exception, console_log

def get_tag_names() -> list[str]:
    tags = db.session.query(Tag.name).order_by(desc('id')).all()
    console_log('tags', tags)
    
    tag_names = [tag.name for tag in tags]
    
    return tag_names


def get_tag_choices() -> list[tuple[str, str]]:
    """
    Return list of (id, name) tuples for tags, ordered by descending id.
    """
    tags = db.session.query(Tag.id, Tag.name).order_by(desc(Tag.id)).all()
    
    # Prepend a default empty choice
    choices = [("", "— Select tag —")]
    
    choices.extend([(str(tag.id), tag.name) for tag in tags])
    
    return choices


def fetch_all_tags(page_num: int=None, paginate: bool = False) -> list[Tag] | object:
    ''' Gets all Tag rows from database
    
    This will return a pagination of all Tag rows from database.
    
    Alternatively, you can use get_sub_tags(id) to get the sub tags without pagination
    '''
    
    if not page_num:
        page_num = request.args.get("page", 1, type=int)
    
    all_tags = Tag.query.order_by(desc('id'))
    
    if paginate:
        pagination = all_tags \
            .order_by(Tag.id.desc()) \
            .paginate(page=page_num, per_page=10, error_out=False)
        
        return pagination
    else:
        all_tags = all_tags.all()
    
    return all_tags


def fetch_tag(identifier: int | str) -> Tag:
    tag = None
    try:
        # Check if product_id_key is an integer
        id = int(identifier)
        # Fetch the product by id
        tag = Tag.query.filter_by(id=id).first()
    except ValueError:
        # If not an integer, treat it as a string
        tag = Tag.query.filter_by(slug=identifier).first()

    return tag


def save_tag(form_data, slug=None) -> Tag:
    try:
        tag = fetch_tag(slug) if slug else None
        
        # get form data
        name = form_data.get('name', '')
        description = form_data.get('description', '')
        
        # Check if tag name already exists within the parent tag
        if not tag:
            existing_tag = Tag.query.filter_by(name=name, slug=slug).first()
            if existing_tag:
                raise ValueError('Tag with name ' + name + ' already exists')
        
        
        # Update the existing Tag or create a new one if it doesn't exist
        with current_app.app_context():
            if tag:
                slug = generate_slug(name, Tag, tag)
                tag.update(
                    name=name,
                    description=description,
                    slug=slug
                )
                
                tag:Tag = Tag.query.get(tag.id)
                
                return tag
            else:
                slug = generate_slug(name, Tag)
                new_tag = Tag(
                    name=name,
                    description=description,
                    slug=slug
                )
                db.session.add(new_tag)
                db.session.commit()
            
                new_tag = Tag.query.get(new_tag.id)
                return new_tag
    except Exception as e:
        db.session.rollback()
        log_exception('An error occurred while creating tag', e)
        raise e


def save_tags(tags, session=None) -> list:
    try:
        if session is None:
            session = db.session
        
        # Remove leading and trailing whitespace from each tag and exclude empty tags
        tags = [tag.strip() for tag in tags if tag.strip()]
        
        tag_objects = []
        if not tags:
            return tag_objects
        else:
            # query the existing tag or create a new one if it doesn't exist
            for tag_name in tags:
                tag = Tag.query.filter(func.lower(Tag.name) == func.lower(tag_name)).first()
                if not tag:
                    slug = generate_slug(tag_name, Tag)
                    tag = Tag(name=tag_name, slug=slug)
                    session.add(tag)
                    session.commit()
                tag_objects.append(tag)
        return tag_objects
    except Exception as e:
        log_exception('An error occurred creating tags', e)
        db.session.rollback()
        raise