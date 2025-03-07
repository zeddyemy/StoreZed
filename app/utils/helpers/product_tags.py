"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from typing import Optional
from collections import Counter
from flask import request, jsonify, current_app
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Query
from flask_sqlalchemy.pagination import Pagination
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

def get_tag_suggestions(term: str) -> list[str]:
    term = str(term).strip()
    
    suggestions: list[str] = []
    
    tag_suggestions: list[Tag] = Tag.query.filter(Tag.name.ilike(f'%{term}%')).all()
    suggestions.extend([tag.name for tag in tag_suggestions])
    
    
    return suggestions

def fetch_all_tags(
        page_num: Optional[int] = None,
        paginate: Optional[bool] = False,
        search_term: Optional[str] = None,
    ) -> list[Tag] | Pagination:
    '''
    Get tags from the database with optional filtering and pagination.

    Returns either a pagination object or list of Tag instances.

    Args:
        page_num: Page number for pagination (default from request if None)
        paginate: Return pagination object when True
        search_term: Filter term for tag search

    Returns:
        Pagination object or list of Tag instances
    '''
    
    # Get parameters from request if not provided
    if page_num is None:
        page_num = request.args.get("page", 1, type=int)
    
    if search_term is None:
        search_term = request.args.get("search", "").strip()
    
    # Base query
    query = Tag.query

    # Apply search filters
    query = Tag.add_search_filters(query, search_term)
    
    # Apply consistent ordering
    query = query.order_by(Tag.id.desc())
    
    if paginate:
        pagination = query.paginate(page=page_num, per_page=10, error_out=False)
        
        return pagination
    
    return query.all()


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