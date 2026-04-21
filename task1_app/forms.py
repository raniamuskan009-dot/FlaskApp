from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=50),
        Regexp("^[A-Za-z ]+$", message="Only letters allowed")
    ])

    phone = StringField('Phone', validators=[
        DataRequired(),
        Regexp("^[0-9]+$", message="Only numbers allowed")
    ])

    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

    submit = SubmitField('Submit')