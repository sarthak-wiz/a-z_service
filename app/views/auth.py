from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User
from app.forms import RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user_data = {
            'username': form.username.data,
            'password': hashed_password,
            'role': form.role.data,
            'is_approved': form.role.data != 'professional'  
        }
        
        
        if form.role.data == 'professional':
            user_data.update({
                'professional_id': form.professional_id.data.upper(),
                'location': form.location.data,
                'pincode': form.pincode.data
            })
        
        user = User(**user_data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!' + 
                  (' Please wait for admin approval.' if form.role.data == 'professional' else ''), 
                  'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('That username is already taken. Please choose another.', 'danger')
    
    return render_template('register.html', form=form) 