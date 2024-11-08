from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Service, ServiceRequest
from .forms import LoginForm, RegistrationForm, ServiceForm

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
            if user.role == 'professional' and not user.is_approved:
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('main.login'))
            
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Role-specific redirects
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'professional':
                return redirect(url_for('professional.dashboard'))
            else:
                return redirect(url_for('customer.dashboard'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=form.password.data,
            role=form.role.data,
            is_approved=form.role.data == 'customer'  # Auto-approve customers, professionals need admin approval
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        if form.role.data == 'professional':
            flash('Your account will be reviewed by an admin before you can access professional features.', 'info')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
