from flask import Flask, flash, request, session, redirect, url_for, render_template,jsonify
import flask.ext.login as flask_login
from flask.ext.pymongo import PyMongo
from visualintrigue import siteconfig
from visualintrigue import util
from visualintrigue.blog import BlogForm
from visualintrigue.photo import PhotoForm
from visualintrigue.article import ArticleForm
from visualintrigue.collection import CollectionForm
import logging
from visualintrigue.user import User
from werkzeug.contrib.fixers import ProxyFix
import pymongo
import random
import uuid
from werkzeug import secure_filename
import os
from datetime import datetime
import requests


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

    sorted_stories = util.getUrl("/dbapi/api/v1.0/frontpage")  

    return render_template('frontpage.html',title='Visually Intriguing Photography One Adventure at a Time',photos=sorted_stories,baseurl=siteconfig.AMAZON_BASE_URL)

@app.route('/articles')
def articles():

    articles = util.getUrl("/dbapi/api/v1.0/listarticles")
    
    return render_template('articles.html',title="Visual Intrigue Articles",articles=articles)

@app.route('/reviews')
def reviews():
    return render_template('reviews.html',title="Visual Intrigue Articles")

@app.route('/portfolio/<portfolio>')
def portfolio(portfolio='all'):
    logger.info("requested specific portfolio")
    
    photos = None
     
    photos = util.getUrl("/dbapi/api/v1.0/listportfolios/" + portfolio)


    return render_template('portfolio.html',title='Portfolio' + portfolio,blogs=photos,portfolio=portfolio,baseurl=siteconfig.AMAZON_BASE_URL)

@app.route('/about')
def about():
    logger.info("requested about")
    return render_template('about.html',title='Visual Intrigue Photography',container="container")


@app.route('/stories/<id>')
def stories(id = None):
    """ Collection Detail Display """
    collection = None

    result = util.getUrl("/dbapi/api/v1.0/getstory/" + id)    


    return render_template('story.html',title=result['collection']['title'],
                           collection=result['collection'],photos=result['photos'],
                           baseurl=siteconfig.AMAZON_BASE_URL,
                           firstphoto=result['firstphoto'],
                           description=result['collection']['summary'])


@app.route('/notfound',methods=['GET','POST'])
def notfound():
    
    return render_template('404.html',title='Page Not Found')

@app.route('/photo/<id>', methods=['GET'])
def photo(id=None):
    """
    Photo detail display
    """

    photo = util.getUrl("/dbapi/api/v1.0/getphoto/" + id)

    #photo = None
    #if id is not None:
    #    photo = mongo.db.photos.find_one({'slug':id}) 
    # 
    if photo is None:
        return redirect(url_for('notfound'))
     
    image_url = siteconfig.AMAZON_BASE_URL + photo['files']['large']['path']
    lowrez_url = siteconfig.AMAZON_BASE_URL + photo["files"]['lrlarge']['path']
    return render_template('photo.html',title=photo['title'],photo=photo,image_url=image_url,lowrez_url=lowrez_url)

@app.route('/error', methods=['GET','POST'])
def error():
    return "ERROR"

# TODO...CONVERT TO DBAPI
@app.route('/image/frontpageservice/<size>',methods=['GET'])
def frontpageservice(size):
    """ Returns a JSON String of the images included in the
        frontpage image rotation.  The order of the list is
        randomized
    """
    #imagelist = [{'url':'https://s3.amazonaws.com/visualintrigue-3556/92ff9249-ca37-48ed-aa65-c5e0f7a6b66b_lowrez_1600px.jpeg'}]
    imagelist = []
    photos = mongo.db.photos.find({'homepage':'yes','status':'active'})
    if photos is None:
        return jsonify(imagelist)
    
    tlist = []
    
    for photo in photos:
        if size in photo['files']:
            tlist.append(siteconfig.AMAZON_BASE_URL + photo['files'][size]['path'])
         
    i = len(tlist)-1
    
    while i > 1:
        j = random.randrange(i)  # 0 <= j <= i
        tlist[j], tlist[i] = tlist[i], tlist[j]
        i = i - 1

    for t in tlist:
        imagelist.append({'url':t})

    return jsonify({'urls':imagelist})
    

@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html',title='Unauthorized Request')


@app.route('/article/<id>')
def article_view(id):
    """ View Article """
    article = mongo.db.articles.find_one({'slug':id})
    return render_template('article.html',title=article['title'],article=article)


@app.route('/filebrowser')
@flask_login.login_required
def file_browser():
    
    files = {'status':'error'}
    if os.path.exists(siteconfig.MEDIA):
        files = util.path_hierarchy(siteconfig.MEDIA)
        #return(jsonify(files))
    return render_template('fbrowse.html',files=files)

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in siteconfig.USERS:
        return None

    user = User()
    user.id = email
    return user

@app.route('/search')
def search():   
    return render_template("search.html",title="Search")

@app.route('/contact')
def contact():   
    return render_template("contact.html",title="Contact")

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

@app.template_filter()
def formatmongodb_datetime_filter(value):
    date_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    return date_obj.strftime('%Y/%m/%d %H:%M')

@app.template_filter()
def getday(value):
    date_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    return date_obj.strftime('%d')
  
@app.template_filter()
def getmonthyear(value):
    date_obj = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    return date_obj.strftime('%B %Y: %A')




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
    
    
    app.run(host="0.0.0.0")
    
