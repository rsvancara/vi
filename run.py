from flask import Flask, flash, request, session, redirect, url_for, render_template,jsonify
from visualintrigue import siteconfig
from visualintrigue import util
import logging
from werkzeug.contrib.fixers import ProxyFix
from werkzeug import secure_filename
import os
from datetime import datetime
import requests

app = Flask('visualintrigue')

logger = logging.getLogger('app')

app.secret_key = siteconfig.SECRETKEY 

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
    return render_template('reviews.html',title="Visual Intrigue Reviews")

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

    if photo is None:
        return redirect(url_for('notfound'))
     
    image_url = siteconfig.AMAZON_BASE_URL + photo['files']['large']['path']
    lowrez_url = siteconfig.AMAZON_BASE_URL + photo["files"]['lrlarge']['path']
    small_url = siteconfig.AMAZON_BASE_URL + photo["files"]['lrmedium']['path']
    return render_template('photo.html',title=photo['title'],photo=photo,image_url=image_url,lowrez_url=lowrez_url,small_url = small_url)

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
    photos = util.getUrl("/dbapi/api/v1.0/frontpageservice/" + size)
    return jsonify(photos)

@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html',title='Unauthorized Request')

@app.route('/article/<id>')
def article_view(id):
    """ View Article """
    article = util.getUrl("/dbapi/api/v1.0/article/" + id)
    return render_template('article.html',title=article['title'],article=article)

@app.route('/search')
def search():   
    return render_template("search.html",title="Search")

@app.route('/contact')
def contact():   
    return render_template("contact.html",title="Contact")

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
    
