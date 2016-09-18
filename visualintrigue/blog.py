from werkzeug import secure_filename
from flask_wtf.file import FileField
from wtforms import Form, TextAreaField, BooleanField, TextField, PasswordField, SelectField, validators, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired




class BlogForm(Form):
    
    
    
    title = TextField(u'Title', [validators.Required(),validators.Length(min=4, max=128)])
    slug = TextField(u'URL Slug', [validators.Required(),validators.Length(min=4, max=128)])
    active = SelectField(u'Status',choices=[('active', 'Active'), ('disabled', 'Disabled')])
    body = TextAreaField(u'Body', [validators.Required()])
    photo = FileField(u'Photo', validators=[FileAllowed(['jpg','jpeg'], 'JPEG Images only!')])
    newimage = HiddenField(u"newimage")
    lat = HiddenField(u"lat")
    lng = HiddenField(u"lng")
    keywords = TextAreaField(u'Key Words',  [validators.Required(),validators.Length(min=4, max=128)])
    portfolio = SelectField(u'Portfolio',choices=[('landscape','Landscape'),
        ('cityscape','Cityscape'),
        ('macro','Macro'),
        ('street','Street Photography')])
    
    
    homepage = SelectField(u'Show On Homepage',choices=[('yes', 'Yes'), ('no', 'No')])
    displayorder = SelectField(u'Display Order',choices=[('1', '1'),
                                                          ('2', '2'),
                                                          ('3', '3'),
                                                          ('4', '4'),
                                                          ('5', '5'),
                                                          ('6', '6'),
                                                          ('7', '7'),
                                                          ('8', '8'),
                                                          ('9', '9'),
                                                          ('10', '10'),
                                                          ('11', '11'),
                                                          ('12', '12'),
                                                          ('13', '13'),
                                                          ('14', '14'),
                                                          ('15', '15'),
                                                          ('16', '16'),
                                                          ('17', '17'),
                                                          ('18', '18')],coerce=str)
    collection = SelectField(u'Collection', choices=[('none','none')],coerce=str)
    
    
    
    # email = TextField('Email Address', [validators.Length(min=6, max=35)])
    # password = PasswordField('New Password', [
    #     validators.Required(),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    # confirm = PasswordField('Repeat Password')
    # accept_tos = BooleanField('I accept the TOS', [validators.Required()])

    def __init__(self, *args, **kwargs):

        
        Form.__init__(self, *args, **kwargs)
