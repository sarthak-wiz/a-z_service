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
    # Query assigned requests directly from ServiceRequest model
    assigned_requests = ServiceRequest.query.filter_by(
        professional_id=current_user.id,
        status='assigned'
    ).all()
    
    # Get available requests (not assigned to any professional)
    available_requests = ServiceRequest.query.filter_by(
        professional_id=None,
        status='requested'
    ).all()
    
    return render_template('professional/dashboard.html',
                         assigned_requests=assigned_requests,
                         available_requests=available_requests)

@professional_bp.route('/accept_request/<int:request_id>', methods=['POST'])
@professional_required
def accept_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.professional_id:
        flash('This request has already been assigned.', 'warning')
    else:
        service_request.professional_id = current_user.id
        service_request.status = 'accepted'
        db.session.commit()
        flash('Request accepted successfully.', 'success')
    return redirect(url_for('professional.dashboard'))

@professional_bp.route('/complete_request/<int:request_id>', methods=['POST'])
@professional_required
def complete_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.professional_id != current_user.id:
        flash('You are not authorized to complete this request.', 'danger')
    else:
        service_request.status = 'completed'
        db.session.commit()
        flash('Service marked as completed.', 'success')
    return redirect(url_for('professional.dashboard'))
