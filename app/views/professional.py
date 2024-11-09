from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import ServiceRequest, db
from functools import wraps

professional_bp = Blueprint('professional', __name__)

def professional_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'professional' or not current_user.is_approved:
            flash('You must be an approved service professional to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@professional_bp.route('/dashboard')
@professional_required
def dashboard():
    # Get available requests (not assigned to any professional)
    available_requests = ServiceRequest.query.filter_by(
        professional_id=None,
        status='requested'
    ).all()
    
    # Get requests assigned to current professional
    assigned_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id
    ).order_by(ServiceRequest.date_of_request.desc()).all()
    
    print(f"assigned_requests {assigned_requests}")  # Debug print
    
    return render_template('professional/dashboard.html',
                         available_requests=available_requests,
                         assigned_requests=assigned_requests)

@professional_bp.route('/accept_request/<int:request_id>', methods=['POST'])
@professional_required
def accept_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.professional_id is not None:
        flash('This request has already been assigned.', 'warning')
        return redirect(url_for('professional.dashboard'))
    
    service_request.professional_id = current_user.id
    service_request.status = 'assigned'
    
    try:
        db.session.commit()
        flash('Service request accepted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error accepting request. Please try again.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('professional.dashboard'))

@professional_bp.route('/start_service/<int:request_id>', methods=['POST'])
@professional_required
def start_service(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.professional_id != current_user.id:
        flash('You can only start services assigned to you.', 'danger')
        return redirect(url_for('professional.dashboard'))
    
    service_request.status = 'in_progress'
    
    try:
        db.session.commit()
        flash('Service marked as in progress!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating status. Please try again.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('professional.dashboard'))

@professional_bp.route('/complete_service/<int:request_id>', methods=['POST'])
@professional_required
def complete_service(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.professional_id != current_user.id:
        flash('You can only complete services assigned to you.', 'danger')
        return redirect(url_for('professional.dashboard'))
    
    service_request.status = 'pending_customer_approval'
    
    try:
        db.session.commit()
        flash('Service marked as completed! Waiting for customer review.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating status. Please try again.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('professional.dashboard'))
