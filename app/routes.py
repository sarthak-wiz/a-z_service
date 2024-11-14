from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Service, ServiceRequest
from .forms import LoginForm, RegistrationForm, ServiceForm
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import random
import string

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

def generate_professional_id():
    """Generate a unique professional ID in format PRO12345"""
    while True:
        # Generate a random 5-digit number
        number = ''.join(random.choices(string.digits, k=5))
        professional_id = f'PRO{number}'
        
        # Check if this ID already exists
        existing_user = User.query.filter_by(professional_id=professional_id).first()
        if not existing_user:
            return professional_id

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    professional_id = None
    
    # Generate professional ID if role is professional
    if request.method == 'GET' and request.args.get('role') == 'professional':
        professional_id = generate_professional_id()
    
    if form.validate_on_submit():
        try:
            user_data = {
                'username': form.username.data,
                'password': form.password.data, 
                'role': form.role.data,
                'is_approved': form.role.data != 'professional'
            }
            
            if form.role.data == 'professional':
                user_data.update({
                    'professional_id': request.form.get('professional_id'),
                    'location': form.location.data,
                    'pincode': form.pincode.data
                })
            
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
            
            message = 'Registration successful!'
            if form.role.data == 'professional':
                message += ' Please wait for admin approval.'
            flash(message, 'success')
            
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html', 
                         form=form, 
                         professional_id=professional_id)



@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))



