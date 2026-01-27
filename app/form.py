from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
#import sqlalchemy as sa
from app import sess_SA
from app.models import Users

# ...

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = sess_SA.query(Users).filter(Users.login == username.data).one()
        # user = sess_SA.scalar(sa.select(Users).where(
        #     Users.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    # def validate_email(self, email):
    #     user = db.session.scalar(sa.select(User).where(
    #         User.email == email.data))
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')