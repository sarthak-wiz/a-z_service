from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, ServiceRequest, Service, db
from functools import wraps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

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

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get counts for dashboard
    total_professionals = User.query.filter_by(role='professional').count()
    pending_approvals = User.query.filter_by(role='professional', is_approved=False).count()
    blocked_professionals = User.query.filter_by(role='professional', is_blocked=True).count()
    total_customers = User.query.filter_by(role='customer').count()
    
    # Get recent professionals (last 5)
    recent_professionals = User.query.filter_by(role='professional')\
        .order_by(User.id.desc())\
        .limit(5)\
        .all()
    
    # Generate Professional Status Chart
    plt.figure(figsize=(8, 8))
    plt.pie([
        total_professionals - pending_approvals - blocked_professionals,
        pending_approvals,
        blocked_professionals
    ], 
        labels=['Approved', 'Pending', 'Blocked'],
        colors=['#28a745', '#ffc107', '#dc3545'],
        autopct='%1.1f%%'
    )
    plt.title('Professional Status Distribution')
    
    # Save to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    professional_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Generate Service Request Status Chart
    service_requests = ServiceRequest.query.all()
    status_counts = {
        'requested': 0,
        'assigned': 0,
        'in_progress': 0,
        'completed': 0,
        'cancelled': 0
    }
    for request in service_requests:
        status_counts[request.status] = status_counts.get(request.status, 0) + 1
    
    plt.figure(figsize=(8, 8))
    plt.pie(status_counts.values(),
        labels=status_counts.keys(),
        colors=['#007bff', '#17a2b8', '#ffc107', '#28a745', '#dc3545'],
        autopct='%1.1f%%'
    )
    plt.title('Service Request Status Distribution')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    requests_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return render_template('admin/dashboard.html',
                         total_professionals=total_professionals,
                         pending_approvals=pending_approvals,
                         blocked_professionals=blocked_professionals,
                         total_customers=total_customers,
                         professional_chart=professional_chart,
                         requests_chart=requests_chart,
                         recent_professionals=recent_professionals)

@admin_bp.route('/approve_professional/<int:user_id>', methods=['POST'])
@admin_required
def approve_professional(user_id):
    professional = User.query.get_or_404(user_id)
    if professional.role != 'professional':
        flash('Invalid user role.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    professional.is_approved = True
    try:
        db.session.commit()
        flash('Professional approved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error approving professional. Please try again.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/block_professional/<int:user_id>', methods=['POST'])
@admin_required
def block_professional(user_id):
    professional = User.query.get_or_404(user_id)
    if professional.role != 'professional':
        flash('Invalid user role.', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    professional.is_blocked = not professional.is_blocked  # Toggle blocked status
    try:
        db.session.commit()
        status = 'blocked' if professional.is_blocked else 'unblocked'
        flash(f'Professional {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating professional status. Please try again.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/search_professionals', methods=['GET', 'POST'])
@admin_required
def search_professionals():
    from app.forms import ProfessionalSearchForm
    form = ProfessionalSearchForm()
    
    if form.validate_on_submit():
        search_term = form.search_term.data
        search_type = form.search_type.data
        
        # Base query
        query = User.query.filter_by(role='professional')
        
        # Apply search filter if search term is provided
        if search_term:
            if search_type == 'username':
                query = query.filter(User.username.ilike(f'%{search_term}%'))
            elif search_type == 'professional_id':
                query = query.filter(User.professional_id.ilike(f'%{search_term}%'))
            elif search_type == 'location':
                query = query.filter(User.location.ilike(f'%{search_term}%'))
            elif search_type == 'pincode':
                query = query.filter(User.pincode == search_term)
        
        professionals = query.all()
    else:
        professionals = User.query.filter_by(role='professional').all()
    
    return render_template('admin/search_professionals.html', 
                         form=form, 
                         professionals=professionals)

@admin_bp.route('/manage_services')
@admin_required
def manage_services():
    services = Service.query.all()
    return render_template('admin/manage_services.html', services=services)

@admin_bp.route('/add_service', methods=['GET', 'POST'])
@admin_required
def add_service():
    from app.forms import ServiceForm
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            time_required=form.time_required.data
        )
        try:
            db.session.add(service)
            db.session.commit()
            flash('Service added successfully!', 'success')
            return redirect(url_for('admin.manage_services'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding service. Please try again.', 'danger')
            print(f"Error: {str(e)}")
    
    return render_template('admin/add_service.html', form=form)

@admin_bp.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    from app.forms import ServiceForm
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.base_price = form.base_price.data
        service.time_required = form.time_required.data
        
        try:
            db.session.commit()
            flash('Service updated successfully!', 'success')
            return redirect(url_for('admin.manage_services'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating service. Please try again.', 'danger')
            print(f"Error: {str(e)}")
    
    return render_template('admin/edit_service.html', form=form, service=service)

@admin_bp.route('/delete_service/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    try:
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting service. Please try again.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('admin.manage_services'))