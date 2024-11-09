from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, DateField, SelectField, DateTimeField, IntegerField, RadioField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from datetime import datetime

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
    name = StringField('Service Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    base_price = FloatField('Base Price ($)', validators=[DataRequired(), NumberRange(min=0)])
    time_required = SelectField('Time Required', 
                              choices=[
                                  ('1 hour', '1 Hour'),
                                  ('2 hours', '2 Hours'),
                                  ('3 hours', '3 Hours'),
                                  ('4 hours', '4 Hours'),
                                  ('6 hours', '6 Hours'),
                                  ('8 hours', '1 Day'),
                                  ('16 hours', '2 Days'),
                                  ('24 hours', '3 Days'),
                              ], 
                              validators=[DataRequired()])
    submit = SubmitField('Submit')

class ApproveForm(FlaskForm):
    """Form for approving service professionals"""
    submit = SubmitField('Approve Professional')

class ServiceRequestForm(FlaskForm):
    """Form for customers to request services"""
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    date_of_request = DateTimeField('Preferred Date', 
                                  format='%Y-%m-%d', 
                                  validators=[DataRequired()],
                                  default=datetime.now)
    remarks = TextAreaField('Additional Remarks')
    submit = SubmitField('Submit Request')

class ReviewForm(FlaskForm):
    rating = RadioField('Rating', 
                       choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                       validators=[DataRequired()])
    comment = TextAreaField('Comment', 
                          validators=[DataRequired(), Length(min=10, max=500)],
                          render_kw={"placeholder": "Please share your experience (minimum 10 characters)"})
    submit = SubmitField('Submit Review')
