from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import ServiceRequest, Service, Review, User
from app import db
from app.forms import ReviewForm, ServiceRequestForm, ServiceSearchForm
from functools import wraps
import matplotlib.pyplot as plt
import io
import base64

customer_bp = Blueprint('customer', __name__)

def customer_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'customer':
            flash('You must be a customer to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@customer_bp.route('/add_review/<int:request_id>', methods=['GET', 'POST'])
@customer_required
def add_review(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if this is the customer's request
    if service_request.customer_id != current_user.id:
        flash('You can only review your own service requests.', 'danger')
        return redirect(url_for('customer.dashboard'))
    
    # Check if request is pending customer approval
    if service_request.status != 'pending_customer_approval':
        flash('You can only review services that are pending your approval.', 'danger')
        return redirect(url_for('customer.dashboard'))
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(service_request_id=request_id).first()
    if existing_review:
        flash('You have already reviewed this service.', 'warning')
        return redirect(url_for('customer.dashboard'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            customer_id=current_user.id,
            professional_id=service_request.professional_id,
            service_request_id=request_id,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        try:
            # Add review
            db.session.add(review)
            # Update service request status to completed
            service_request.status = 'completed'
            db.session.commit()
            
            # Update professional's average rating
            review.update_professional_rating()
            
            flash('Review submitted successfully! Service marked as completed.', 'success')
            return redirect(url_for('customer.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting review. Please try again.', 'danger')
            print(f"Error: {str(e)}")
    
    return render_template('customer/add_review.html', 
                         form=form, 
                         service_request=service_request)

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    
    # Generate Service Request Status Chart
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
    plt.title('My Service Requests Status')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    status_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return render_template('customer/dashboard.html',
                         services=services,
                         service_requests=service_requests,
                         status_chart=status_chart)

@customer_bp.route('/request_service', methods=['GET', 'POST'])
@customer_required
def request_service():
    service_id = request.args.get('service_id', type=int)
    service = None
    if service_id:
        service = Service.query.get_or_404(service_id)
    
    form = ServiceRequestForm()
    # Populate service choices
    form.service_id.choices = [(s.id, s.name) for s in Service.query.all()]
    
    # If service_id is provided, set it as default
    if service_id:
        form.service_id.data = service_id
    
    if form.validate_on_submit():
        service_request = ServiceRequest(
            customer_id=current_user.id,
            service_id=form.service_id.data,
            date_of_request=form.date_of_request.data,
            remarks=form.remarks.data,
            status='requested'
        )
        try:
            db.session.add(service_request)
            db.session.commit()
            flash('Service request submitted successfully!', 'success')
            return redirect(url_for('customer.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting request. Please try again.', 'danger')
            print(f"Error: {str(e)}")
    
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

@customer_bp.route('/search_services', methods=['GET', 'POST'])
@customer_required
def search_services():
    form = ServiceSearchForm()
    services = []
    
    if form.validate_on_submit() or request.args.get('search_term'):
        search_term = form.search_term.data or request.args.get('search_term')
        search_type = form.search_type.data or request.args.get('search_type', 'name')
        
        if search_term:
            if search_type == 'name':
                services = Service.query.filter(Service.name.ilike(f'%{search_term}%')).all()
            elif search_type == 'location':
                services = Service.query.filter(Service.location.ilike(f'%{search_term}%')).all()
            elif search_type == 'pincode':
                services = Service.query.filter(Service.pincode == search_term).all()
            elif search_type == 'id':
                try:
                    service_id = int(search_term)
                    services = Service.query.filter_by(id=service_id).all()
                except ValueError:
                    flash('Invalid Service ID', 'danger')
        else:
            services = Service.query.all()
    else:
        services = Service.query.all()
    
    return render_template('customer/search_services.html', 
                         form=form, 
                         services=services)