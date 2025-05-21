import uuid as uuid
from slugify import slugify
from flask import render_template, request, flash, redirect, abort, url_for, make_response
from flask_login import login_required, current_user

from .. import web_admin_bp
from ....extensions import db
from ....models import Tag
from ....utils.forms.web_admin.tags import TagForm
from ....utils.helpers.basics import redirect_url, get_or_404
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.helpers.product_tags import fetch_all_tags, fetch_tag, save_tag
from ....utils.decorators import session_roles_required, web_admin_login_required



@web_admin_bp.route("/tags", methods=['GET'], strict_slashes=False)
@web_admin_login_required()
def tags():
    page_num = request.args.get("page", 1, type=int)
    search_term = request.args.get("search", "").strip()
    page_name = "tags"
    
    current_user_roles = current_user.role_names
    current_user_id = current_user.id
    
    pagination = fetch_all_tags(page_num=page_num, paginate=True, search_term=search_term)
    
    console_log('pagination', pagination.items)
    
    # Extract paginated tags and pagination info
    all_tags = pagination.items
    total_pages = pagination.pages
    
    return render_template('web_admin/pages/tags/tags.html', all_tags=all_tags, pagination=pagination, total_pages=total_pages, search_term=search_term, page_name=page_name)


@web_admin_bp.route("/tags/new", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def add_new_tag():
    form: TagForm = TagForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                form_data = request.form # get form data
                new_tag = save_tag(form_data)
                
                
                flash('Your new tag ' + new_tag.name + ' was created successfully!', 'success')
                return redirect(url_for('web_admin.tags'))
            except ValueError as e:
                log_exception('Error updating tag', e)
                flash(e, 'error')
            except Exception as e:
                log_exception('Error creating new tag', e)
                flash('An error occurred. Your tag ' + form_data['name'] + ' could not be Created.', 'error')
            
        else:
            console_log("Form Error", form.errors)
            flash("New tag could not be created", 'error')

    
    return render_template('web_admin/pages/tags/new_tag.html', form=form, tag=None)


@web_admin_bp.route("/tags/edit/<slug>", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def edit_tag(slug):
    
    tag = fetch_tag(slug)
    if not tag:
        flash('No such tag Exist', 'error')
        return redirect(url_for('web_admin.tags'))
    
    form: TagForm = TagForm(obj=tag)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                form_data = request.form # get form data
                updated_tag = save_tag(form_data, slug)
                
                
                flash('Your tag ' + updated_tag.name + ' was updated successfully!', 'success')
                return redirect(url_for('web_admin.tags'))
            except ValueError as e:
                log_exception('Error updating tag', e)
                flash(e, 'error')
            except Exception as e:
                log_exception('Error updating tag', e)
                flash('An error occurred. Your tag ' + form_data['name'] + ' could not be updated.', 'error')
        else:
            console_log("Form Error", form.errors)
            flash("Tag could not be updated", 'error')
        
        tag = fetch_tag(slug)

    
    return render_template('web_admin/pages/tags/edit_tag.html', form=form, tag=tag)


@web_admin_bp.route("/tags/delete/<slug>", methods=['POST', 'GET'], strict_slashes=False)
@web_admin_login_required()
def delete_tag(slug):
    """Delete a tag."""
    try:
        tag = fetch_tag(slug)
        if not tag:
            flash('Tag does not exist', 'error')
            return redirect(url_for('web_admin.tags'))
        

        # Delete the tag itself
        db.session.delete(tag)
        db.session.commit()

        flash(f'Tag "{tag.name}" was successfully deleted!', 'success')
        return redirect(url_for('web_admin.tags'))  # Redirect to the tags list page
    except Exception as e:
        db.session.rollback()
        log_exception('Error deleting tag', e)
        flash('An error occurred while deleting the tag. Please try again later.', 'error')
        return redirect(url_for('web_admin.tags'))
