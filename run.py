from flask import Flask, flash, request, session, redirect, url_for, render_template
import flask.ext.login as flask_login
from flask.ext.pymongo import PyMongo
from visualintrigue import siteconfig
from visualintrigue import util
from visualintrigue.blog import BlogForm
import logging
from visualintrigue.user import User
from werkzeug.contrib.fixers import ProxyFix


#from wtforms import Form, BooleanField, TextField, PasswordField, SelectField, validators
from werkzeug import secure_filename
import os
from datetime import datetime


app = Flask('visualintrigue')
app.config['MONGO_URI'] = siteconfig.MONGO_URI

mongo = PyMongo(app)

logger = logging.getLogger('app')

app.secret_key = siteconfig.SECRETKEY 
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@app.route('/')
@app.route('/index')
def index():
    logger.info("requested index")
    blogs = mongo.db.blog.find({'status':'active','homepage':'yes'}).sort("created",-1)
    
    return render_template('frontpage.html',title='Home',blogs=blogs,baseurl=siteconfig.AMAZON_BASE_URL)

@app.route('/blog/view/<slug>')
def blog_view(slug):
    logger.info("requested blog view")
    return render_template('about.html',title=slug)


@app.route('/about')
def about():
    logger.info("requested about")
    return render_template('about.html',title='About')

@app.route('/blog/create', methods=['GET', 'POST'])
@flask_login.login_required
def blog_add():
    logger.info("requested add blog")
    form = BlogForm(request.form)

    if(request.method == 'POST' and form.validate()):
        
        logger.info("dumping " + str(request.files['photo']))
        
        result = util.save_file(request.files['photo'])
        if result['status'] is False:
            flash("No file has been provided, please select a file","alert-warning")
            return render_template('createblog.html',title='Create New Blog Post',form=form)
        
        
        form.newimage = 1
        
        # Grab the file from the request...WTF filefield does not seem to be working
        #file = request.files['photo']
        #if file:
        #    filename = secure_filename(file.filename)
        #    file.save(os.path.join(siteconfig.UPLOAD_PATH, filename))
        
        # Make sure that this contains a unique slug, since we are basing URLS off the slug
        # and these should be unqiue
        blog = mongo.db.blog.find_one({'slug':form.slug.data})

        if blog:
            flash('Slug already exists for blog entry, please use a different one.','alert-warning')
            return render_template('createblog.html',title='Create New Blog Post',form=form)
        
        
        mongo.db.blog.insert(
          {
            "slug": util.slugify(form.slug.data),
            "title": form.title.data,
            "body": form.body.data,
            "status": "active",
            "created": datetime.now(),
            "updated": datetime.now(),
            "files": result['files'],
            "portfolio": form.portfolio.data,
            "keywords": form.keywords.data,
            "homepage": form.homepage.data
          }
        )
        
        flash('Blog entry successfully created','alert-success')
        return redirect('/blog/list')
    
    return render_template('createblog.html',title='Create New Blog Post',form=form)

@app.route('/blog/list')
@flask_login.login_required
def blog_list():
    logger.info("requested blog list")
    
    #blogs = mongo.db.blogs.find({"$or": [{"status":"deleted"},{"status":"active"}]})
    blogs = mongo.db.blog.find().sort("created",-1)
    #for blog in blogs:
    #    logger.info("found")
    
    return render_template('blog_list.html',title='Manage Blog Entries',blogs=blogs)

@app.route('/blog/delete/<id>',methods=['GET'])
@flask_login.login_required
def blog_delete(id=None):
    
    if id is None:
        flash("Invalid blog id passed to delete function!",'alert-warning')
        return redirect(url_for('blog_list'))
    
    blog = mongo.db.blog.find_one({'slug':id})
    if blog:
        if 'files' not in blog:
            try:
                util.delete_image(blog['files'])
            except Exception as e:
                logger.error("Error deleting blog %s with error: %s" %(id,e))
        mongo.db.blog.remove({'slug':id})
        
        flash("Blog entry deleted",'alert-success')
    
        logger.info("requested blog delete")
        return redirect(url_for('blog_list'))

    flash('Error deleting blog entry.  Please see logs for details.')
    return redirect(url_for('error'))


@app.route('/blog/edit/<id>',methods=['GET', 'POST'])
@flask_login.login_required
def blog_edit(id=None):
    logger.info("requested add blog")
    
    if id is None:
        flash('Could not find blog entry for id provided','alert-warning')
        
    
    result = {}
    form = BlogForm()
    # Make sure that this contains a unique slug, since we are basing URLS off the slug
    # and these should be unqiue
    blog = mongo.db.blog.find_one({'slug':id})    

    #form = BlogForm(request.form)
    form.body.data = blog['body']
    form.title.data = blog['title']
    form.slug.data = blog['slug']
    form.active.data = blog['status']
    form.newimage = "0"
    if ('keywords') in blog:    
        form.keywords.data = blog['keywords']
    
    
    
    #portfolioitems  = []
    #for item in mongo.db.portfolio.find():
    #    portfolioitems.append([item['portfolio'],item['portfolio']])
    #form.portfolio.choices = [(item['portfolio'], item['portfolio']) for item in mongo.db.portfolio.find()]
    
    if ('portfolio') in blog:
        form.portfolio.data = blog['portfolio']
    else:
        form.portfolio.data = 'master'
    
    if('homepage') in blog:
        form.homepage.data = blog['homepage']
    
    result['files'] = blog['files']
    
    photo = "http://www.kickoff.com/chops/images/resized/large/no-image-found.jpg"
    if 'files' in blog:
        photo = siteconfig.AMAZON_BASE_URL + blog['files']['medium']['path']

    if(request.method == 'POST'):
        form = BlogForm(request.form)
        if(form.validate()):
            
            logger.info("dumping " + str(request.files['photo']))
            #print(form.newimage)
            
            
            if form.newimage.data == "1": 
                result = util.save_file(request.files['photo'])
                if result['status'] is False:
                    flash("No file has been provided, please select a file","alert-warning")
                    return render_template('createblog.html',title='Create New Blog Post',form=form)
            
            # If the slug is different, then we need to check that it is not in use 
            if blog['slug'] != form.slug.data:
                logger.info("Found duplicate slug")
                slugcount = mongo.db.blog.count({'slug':form.slug.data})
                if slugcount >= 1:
                    flash('Slug already in use. Please select a unique slug','alert-warning')
                    return render_template('editblog.html',title='Edit Blog Post',id=id,form=form, blog=blog) 
            
            mongo.db.blog.update(
               {
                "slug":id,
               },
               {
                 "slug": util.slugify(form.slug.data),
                 "title": form.title.data,
                 "body": form.body.data,
                 "status": form.active.data,    
                 "updated": datetime.now(),
                 "created": blog['created'],
                 "files": result['files'],
                 "portfolio": form.portfolio.data,
                 "keywords": form.keywords.data,
                 "homepage": form.homepage.data
               }            
            )

            return redirect('/blog/list')
        else:
            flash('Validation Error','alert-warning')
            
    return render_template('editblog.html',title='Edit Blog Post',id=id,form=form, blog=blog,photo=photo)    

@app.route('/notfound',methods=['GET','POST'])
def notfound():
    
    return render_template('404.html',title='Page Not Found')

@app.route('/photo/<id>', methods=['GET'])
def photo(id=None):
    
    blog = None
    if id is not None:
        blog = mongo.db.blog.find_one({'slug':id}) 
    
    if blog is None:
        return redirect(url_for('notfound'))
    
    
    image_url = siteconfig.AMAZON_BASE_URL + blog['files']['large']['path']
    
    return render_template('photo.html',title=("Visualintrigue-%s"%blog['title']),blog=blog,image_url=image_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("requested login")
    if request.method == 'GET':
        return render_template('login.html',title='Login')

    email = request.form['email']
    
    if request.form['pw'] == siteconfig.USERS[email]['pw']:
        user = User()
        user.id = email
        
        
        flask_login.login_user(user)
        flash('You were successfully logged in','alert-success')
        return redirect(url_for('blog_list'))

    return 'Bad login'

@app.route('/error', methods=['GET','POST'])
def error():
    return "ERROR"

@app.route('/blog/frontpageservice',methods=['GET'])
@flask_login.login_required
def frontpageservice():
    """ Returns a JSON String of the images included in the
        frontpage image rotation.  The order of the list is
        randomized
    """
    
    imagelist = [{}]
    
    return jsonify(imagelist)
    


@app.route('/logout')
@flask_login.login_required
def logout():
    """Logout the current user."""
    logger.info("requested logout")
    #session.clear()
    #user = current_user
    #user.authenticated = False
    flask_login.logout_user()
    return redirect(url_for('index'))


@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html',title='Unauthorized Request')


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in siteconfig.USERS:
        return None

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in siteconfig.USERS:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauthorized.html',title='Unauthorized Request')

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

app.wsgi_app = ProxyFix(app.wsgi_app)


if __name__ == '__main__':
    
    
    app.debug = True
    
    
    if app.debug == True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR) 
        
    # create a file handler

    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)

    # create a logging format

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger

    logger.addHandler(handler)
        
    logger.info("Application started")
    
    app.jinja_env.filters['datetimefilter'] = datetimefilter
    
    
    app.run()
    
