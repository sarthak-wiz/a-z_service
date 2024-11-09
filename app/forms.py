from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, DateField, SelectField, DateTimeField, IntegerField, RadioField, DecimalField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Optional, ValidationError, Regexp
from datetime import datetime
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    role = SelectField('Role', 
                      choices=[
                          ('', 'Select Role'),
                          ('customer', 'Customer'), 
                          ('professional', 'Professional')
                      ],
                      validators=[DataRequired(message='Please select a role')])
    
    username = StringField('Username', 
                         validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', 
                           validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    
    # Professional-specific fields
    location = StringField('Location', 
                         validators=[Optional(), Length(max=100)])
    pincode = StringField('PIN Code', 
                         validators=[Optional(),
                                   Length(min=6, max=6),
                                   Regexp('^[0-9]*$', 
                                        message='PIN Code must contain only numbers')])

    def validate(self, **kwargs):
        if not super().validate():
            return False
        
        if self.role.data == 'professional':
            if not self.location.data:
                self.location.errors = ['Location is required for professionals']
                return False
            if not self.pincode.data:
                self.pincode.errors = ['PIN Code is required for professionals']
                return False
        
        return True

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class ServiceForm(FlaskForm):
    name = StringField('Service Name', 
                      validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', 
                              validators=[DataRequired(), Length(min=10, max=500)])
    base_price = DecimalField('Base Price', 
                            validators=[DataRequired(), NumberRange(min=0)])
    time_required = StringField('Time Required', 
                              validators=[DataRequired(), Length(max=50)])
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

class ServiceSearchForm(FlaskForm):
    search_term = StringField('Search', validators=[Optional()])
    search_type = SelectField('Search By', 
                            choices=[
                                ('name', 'Service Name'),
                                ('location', 'Location'),
                                ('pincode', 'PIN Code'),
                                ('id', 'Service ID')
                            ])
    submit = SubmitField('Search')

class ProfessionalSearchForm(FlaskForm):
    search_term = StringField('Search', validators=[Optional()])
    search_type = SelectField('Search By', 
                            choices=[
                                ('username', 'Username'),
                                ('professional_id', 'Professional ID'),
                                ('location', 'Location'),
                                ('pincode', 'PIN Code')
                            ])
    submit = SubmitField('Search')

class ProfessionalRegistrationForm(FlaskForm):
    username = StringField('Username', 
                         validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', 
                           validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    location = StringField('Location', 
                         validators=[DataRequired(), Length(max=100)])
    pincode = StringField('PIN Code', 
                         validators=[
                             DataRequired(),
                             Length(min=6, max=6),
                             Regexp('^[0-9]*$', message='PIN Code must contain only numbers')
                         ])
    professional_id = StringField('Professional ID',
                                validators=[
                                    DataRequired(),
                                    Regexp('^PRO[0-9]{5}$', 
                                          message='Professional ID must be in format PRO12345')
                                ])
    submit = SubmitField('Register')

    def validate_professional_id(self, field):
        user = User.query.filter_by(professional_id=field.data).first()
        if user:
            raise ValidationError('This Professional ID is already registered.')
