from werkzeug import secure_filename
from flask_wtf.file import FileField
from wtforms import Form, TextAreaField, BooleanField, TextField, PasswordField, SelectField, validators, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class CollectionForm(Form):
       
    title = TextField(u'Title', [validators.Required(),validators.Length(min=4, max=128)])
    slug = TextField(u'Slug', [validators.Required(),validators.Length(min=4, max=128)])
    collection = TextField(u'Collection', [validators.Required(),validators.Length(min=4, max=128)])
    active = SelectField(u'Status',choices=[('active', 'Active'), ('disabled', 'Disabled')])
    body = TextAreaField(u'Body', [validators.Required()])
    keywords = TextAreaField(u'Key Words',  [validators.Required(),validators.Length(min=4, max=128)])  
    
    # email = TextField('Email Address', [validators.Length(min=6, max=35)])
    # password = PasswordField('New Password', [
    #     validators.Required(),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    # confirm = PasswordField('Repeat Password')
    # accept_tos = BooleanField('I accept the TOS', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
