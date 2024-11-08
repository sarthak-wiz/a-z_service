from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, DateField, SelectField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('customer', 'Customer'), 
        ('professional', 'Service Professional')
    ])
    submit = SubmitField('Register')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    base_price = FloatField('Base Price', validators=[DataRequired()])
    submit = SubmitField('Add Service')

class ApproveForm(FlaskForm):
    """Form for approving service professionals"""
    submit = SubmitField('Approve Professional')

class ServiceRequestForm(FlaskForm):
    """Form for customers to request services"""
    date_of_request = DateField('Preferred Date', validators=[DataRequired()])
    remarks = TextAreaField('Additional Notes')
    submit = SubmitField('Submit Request')
