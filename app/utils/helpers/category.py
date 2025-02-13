"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

import os, sys
from threading import Thread
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage
from flask import Flask, request, jsonify, current_app
from cachetools import cached, TTLCache

from ...extensions import db
from ...models import Category
from config import Config
from .basics import int_or_none, generate_slug
from .loggers import console_log, log_exception
from .media import save_media_files_to_temp, save_media

# Create a cache with a Time-To-Live (TTL) of 5 minutes (300 seconds)
cache = TTLCache(maxsize=100, ttl=300)

def get_category_names() -> list[str]:
    categories = db.session.query(Category.name).order_by(desc('id')).all()
    console_log('categories', categories)
    
    category_names = [cat.name for cat in categories]
    
    return category_names

def get_category_choices() -> list[tuple[str, str]]:
    """
    Return list of (id, name) tuples for categories, ordered by descending id.
    """
    categories = db.session.query(Category.id, Category.name).order_by(desc(Category.id)).all()
    
    # Prepend a default empty choice
    choices = [("", "— Select category —")]
    
    choices.extend([(str(cat.id), cat.name) for cat in categories])
    
    return choices

def fetch_all_categories(cat_id: int=None, page_num: int=None, paginate: bool = False) -> list[Category] | object:
    ''' Gets all Category rows from database
    
    This will return a pagination of all Category rows from database.
    :param cat_id: The ID of a Category. if cat_id is passed, it will return the sub categories of the category
    
    Alternatively, you can use get_sub_categories(id) to get the sub categories without pagination
    '''
    
    if not page_num:
        page_num = request.args.get("page", 1, type=int)
    
    if not cat_id:
        all_categories = Category.query.order_by(desc('id'))
    elif cat_id:
        all_categories = Category.query.filter(Category.parent_id == cat_id).order_by(desc('id'))
    
    if paginate:
        RESULTS_PER_PAGE = int('10')
        pagination = all_categories \
            .order_by(Category.id.desc()) \
            .paginate(page=page_num, per_page=RESULTS_PER_PAGE, error_out=False)
        
        return pagination
    else:
        all_categories = all_categories.all()
    
    return all_categories

@cached(cache)
def get_cached_categories() -> list[dict[str, str]]:
    return [cat.to_dict() for cat in fetch_all_categories()]

def fetch_category(identifier: int | str) -> Category:
    category = None
    try:
        # Check if product_id_key is an integer
        id = int(identifier)
        # Fetch the product by id
        category = Category.query.filter_by(id=id).first()
    except ValueError:
        # If not an integer, treat it as a string
        category = Category.query.filter_by(slug=identifier).first()

    return category


def save_category(form_data, slug=None) -> Category:
    try:
        category = None
        if slug:
            category = fetch_category(slug)
        
        # get form data
        name = form_data.get('name', '')
        description = form_data.get('description', '')
        parent_cat = int_or_none(form_data.get('parent_cat', None))
        
        cat_img = request.files.get('cat_img', '')
        
        # If no image was uploaded, set cat_img to None
        if not cat_img or cat_img.filename == '':
            cat_img = None
        
        if cat_img:
            media_id = save_category_media(cat_img)
        if not cat_img and category:
            media_id = category.media_id if category.media_id else None
        else:
            media_id = None
        
        
        # Check if category name already exists within the parent category
        existing_category = Category.query.filter_by(name=name, parent_id=parent_cat).first()
        if existing_category:
            raise ValueError('Category name already exists within the selected parent category.')
        
        
        # Update the existing Category or create a new one if it doesn't exist
        with current_app.app_context():
            if category:
                slug = generate_slug(name, Category, category)
                category.update(
                    name=name,
                    description=description,
                    media_id=media_id,
                    parent_id=parent_cat,
                    slug=slug
                )
                
                db.session.commit()
                category = Category.query.get(category.id)
                return category
            else:
                slug = generate_slug(name, Category)
                new_category = Category(
                    name=name,
                    description=description,
                    media_id=media_id,
                    parent_id=parent_cat,
                    slug=slug
                )
                db.session.add(new_category)
                db.session.commit()
            
                new_category = Category.query.get(new_category.id)
                return new_category
    except Exception as e:
        db.session.rollback()
        log_exception('An error occurred while creating category', e)
        raise e


def async_save_category_media(app: Flask, media_file_paths, category: Category = None) -> int:
    with app.app_context():
        try:
            
            console_log("async media_file_paths", media_file_paths)
            if media_file_paths:
                for file_path in media_file_paths:
                    filename = os.path.basename(file_path)
                    console_log("filename", filename)
                    with open(file_path, 'rb') as media_file:
                        category_media = save_media(media_file, filename) # This saves image file, saves the path in db and return the Media instance
                        category_media_id = category_media.id
                        console_log("r category_media_id", category_media_id)
            elif not media_file_paths and category:
                if category.media_id:
                    category_media = category.media
                    category_media_id = category_media.id
                else:
                    category_media = None
                    category_media_id = None
            else:
                category_media = None
                category_media_id = None
            
            if not category_media:
                raise ValueError("No Category media to save")
            
            return category_media_id
        except Exception as e:
            log_exception()
            raise e

def save_category_media(media_file: FileStorage, category: Category = None):
    media_file_paths = save_media_files_to_temp(media_file)
    console_log("media_file_paths", media_file_paths)
    
    return async_save_category_media(current_app._get_current_object(), media_file_paths, category)

