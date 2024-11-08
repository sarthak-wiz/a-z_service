from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.models import ServiceRequest, Service, db
from app.forms import ServiceRequestForm
from datetime import datetime

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer/dashboard.html', 
                         services=services,
                         service_requests=service_requests)

@customer_bp.route('/request_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def request_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceRequestForm()
    
    if form.validate_on_submit():
        new_request = ServiceRequest(
            service_id=service.id,
            customer_id=current_user.id,
            date_of_request=form.date_of_request.data,
            remarks=form.remarks.data,
            status='requested'
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Service request submitted successfully!', 'success')
        return redirect(url_for('customer.dashboard'))
    
    return render_template('customer/request_service.html', 
                         form=form, 
                         service=service)

@customer_bp.route('/cancel_request/<int:request_id>', methods=['POST'])
@login_required
def cancel_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    if service_request.customer_id != current_user.id:
        flash('You are not authorized to cancel this request.', 'danger')
        return redirect(url_for('customer.dashboard'))
    
    if service_request.status != 'requested':
        flash('This request cannot be cancelled anymore.', 'warning')
        return redirect(url_for('customer.dashboard'))
    
    db.session.delete(service_request)
    db.session.commit()
    flash('Service request cancelled successfully.', 'success')
    return redirect(url_for('customer.dashboard'))
