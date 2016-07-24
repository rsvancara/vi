from werkzeug import secure_filename
from flask_wtf.file import FileField
from wtforms import Form, TextAreaField, BooleanField, TextField, PasswordField, SelectField, validators, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class Portfolio(Form):
    portfolio = TextField(u'Portfolio', [validators.Required(),validators.Length(min=4, max=25)])
    key = TextField(u'URL Slug', [validators.Required(),validators.Length(min=4, max=25)])
    privacy = SelectField(u'Privacy',choices=[('none', 'None'), ('private', 'Private')])
    
    
    
    
    # email = TextField('Email Address', [validators.Length(min=6, max=35)])
    # password = PasswordField('New Password', [
    #     validators.Required(),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    # confirm = PasswordField('Repeat Password')
    # accept_tos = BooleanField('I accept the TOS', [validators.Required()])
