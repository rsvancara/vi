from werkzeug import secure_filename
from flask_wtf.file import FileField
from wtforms import Form, TextAreaField, BooleanField, TextField, PasswordField, SelectField, validators, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class ArticleForm(Form):
       
    title = TextField(u'Title', [validators.Required(),validators.Length(min=4, max=128)])
    slug = TextField(u'Slug', [validators.Required(),validators.Length(min=4, max=128)])
    active = SelectField(u'Status',choices=[('active', 'Active'), ('disabled', 'Disabled')])
    article_type = SelectField(u'Article Type',choices=[('review', 'review'), ('rant', 'rant'),('article', 'article'),('guide','guide')])
    body = TextAreaField(u'Body', [validators.Required()])
    keywords = TextAreaField(u'Key Words',  [validators.Required(),validators.Length(min=4, max=128)])  
    headerurl = TextField(u'Header Image',  [validators.Required(),validators.Length(min=4, max=1024)])  
    
    # email = TextField('Email Address', [validators.Length(min=6, max=35)])
    # password = PasswordField('New Password', [
    #     validators.Required(),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    # confirm = PasswordField('Repeat Password')
    # accept_tos = BooleanField('I accept the TOS', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
