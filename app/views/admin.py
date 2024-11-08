from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import Service, User, db
from app.forms import ServiceForm

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'admin':
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    services = Service.query.all()
    users = User.query.filter_by(role='professional').all()
    return render_template('admin/dashboard.html', services=services, users=users)

@admin_bp.route('/services/add', methods=['GET', 'POST'])
@admin_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_service.html', form=form)

@admin_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.base_price = form.base_price.data
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_service.html', form=form, service=service)

@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/professionals/<int:user_id>/approve', methods=['POST'])
@admin_required
def approve_professional(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'professional':
        flash('This user is not a service professional.', 'danger')
        return redirect(url_for('admin.dashboard'))
    user.is_approved = True
    db.session.commit()
    flash(f'Service professional {user.username} has been approved.', 'success')
    return redirect(url_for('admin.dashboard'))
