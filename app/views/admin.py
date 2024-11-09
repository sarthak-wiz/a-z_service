from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Service
from app import db
from app.forms import ProfessionalSearchForm, ServiceForm
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need to be logged in as an admin to view this page.', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/search_professionals', methods=['GET'])
@admin_required
def search_professionals():
    form = ProfessionalSearchForm()
    query = User.query.filter_by(role='professional')
    
    search_term = request.args.get('search_term', '')
    search_type = request.args.get('search_type', 'username')
    
    if search_term:
        if search_type == 'username':
            query = query.filter(User.username.ilike(f'%{search_term}%'))
        elif search_type == 'professional_id':
            query = query.filter(User.professional_id.ilike(f'%{search_term}%'))
        elif search_type == 'location':
            query = query.filter(User.location.ilike(f'%{search_term}%'))
        elif search_type == 'pincode':
            query = query.filter(User.pincode.ilike(f'%{search_term}%'))
    
    professionals = query.all()
    return render_template('admin/search_professionals.html',
                         professionals=professionals,
                         form=form)

@admin_bp.route('/admin/approve_professional/<int:user_id>', methods=['POST'])
@admin_required
def approve_professional(user_id):
    professional = User.query.get_or_404(user_id)
    if professional.role != 'professional':
        flash('User is not a professional.', 'danger')
        return redirect(url_for('admin.search_professionals'))
    
    professional.is_approved = True
    db.session.commit()
    flash(f'Professional {professional.username} has been approved.', 'success')
    return redirect(url_for('admin.search_professionals'))

@admin_bp.route('/admin/block_professional/<int:user_id>', methods=['POST'])
@admin_required
def block_professional(user_id):
    professional = User.query.get_or_404(user_id)
    if professional.role != 'professional':
        flash('User is not a professional.', 'danger')
        return redirect(url_for('admin.search_professionals'))
    
    professional.is_blocked = not professional.is_blocked  # Toggle blocked status
    status = 'blocked' if professional.is_blocked else 'unblocked'
    db.session.commit()
    flash(f'Professional {professional.username} has been {status}.', 'success')
    return redirect(url_for('admin.search_professionals'))

@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    # Get counts for dashboard
    total_professionals = User.query.filter_by(role='professional').count()
    pending_approvals = User.query.filter_by(role='professional', is_approved=False).count()
    blocked_professionals = User.query.filter_by(role='professional', is_blocked=True).count()
    total_customers = User.query.filter_by(role='customer').count()
    
    # Get recent professionals
    recent_professionals = User.query.filter_by(role='professional')\
                              .order_by(User.id.desc())\
                              .limit(5)\
                              .all()
    
    return render_template('admin/dashboard.html',
                         total_professionals=total_professionals,
                         pending_approvals=pending_approvals,
                         blocked_professionals=blocked_professionals,
                         total_customers=total_customers,
                         recent_professionals=recent_professionals)

@admin_bp.route('/admin/manage_services')
@admin_required
def manage_services():
    services = Service.query.all()
    form = ServiceForm()
    return render_template('admin/manage_services.html', 
                         services=services, 
                         form=form)

@admin_bp.route('/admin/add_service', methods=['POST'])
@admin_required
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            time_required=form.time_required.data
        )
        db.session.add(service)
        try:
            db.session.commit()
            flash('Service added successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error adding service. Please try again.', 'danger')
    return redirect(url_for('admin.manage_services'))

@admin_bp.route('/admin/edit_service/<int:service_id>', methods=['POST'])
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm()
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.base_price = form.base_price.data
        service.time_required = form.time_required.data
        try:
            db.session.commit()
            flash('Service updated successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error updating service. Please try again.', 'danger')
    return redirect(url_for('admin.manage_services'))

@admin_bp.route('/admin/delete_service/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    try:
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting service. Please try again.', 'danger')
    return redirect(url_for('admin.manage_services'))
