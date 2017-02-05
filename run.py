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
    
    stories = []
    #blogs = mongo.db.blog.find({'status':'active','homepage':'yes'}).sort("created",-1)
    
    collections = mongo.db.collections.find({'status':'active'}).sort("created",-1)
    
    for c in collections:
        photos = mongo.db.photos.find({'status':'active','collection':c['collection'],'homepage':'yes'}).sort('displayorder').limit(1)
        
        for b in photos:
            
            b['ctitle'] = c['title']
            b['cslug'] = c['slug']
            b['created'] = c['created']
            b['summary'] = util.summary_text(c['body'])
            b['type'] = 'photo'
            stories.append(b)
            break

    articles = mongo.db.articles.find({'status':'active'}).sort("created",-1)

    for a in articles:
        r = {}
        r['created'] = a['created']
        r['summary'] = util.summary_text(a['body'])
        r['cslug'] = a['slug']
        r['type'] = 'article'
        r['title'] = a['title']
        r['teaserurl'] = a['teaserurl'] 
        stories.append(r)

    sorted_stories = sorted(stories,key=lambda x:x['created'],reverse=True)
    #d = {d['created']:d for d in stories} 
 
    #sorted_stories = []
    #for k in sorted(d.keys()):
    #    sorted_stories.append(k)


    return render_template('frontpage.html',title='Visually Intriguing Photography One Adventure at a Time',photos=sorted_stories,baseurl=siteconfig.AMAZON_BASE_URL)

@app.route('/articles')
def articles():
    return render_template('articles.html',title="Visual Intrigue Articles")

@app.route('/reviews')
def reviews():
    return render_template('reviews.html',title="Visual Intrigue Articles")

@app.route('/portfolio/<portfolio>')
def portfolio(portfolio=all):
    logger.info("requested specific portfolio")
    
    blogs = None
    
    if portfolio != 'all':
        blogs = mongo.db.blog.find({'status':'active','homepage':'yes','portfolio':portfolio}).sort("created",-1)
    else:
        blogs = mongo.db.blog.find({'status':'active','homepage':'yes'}).sort("created",-1)

    return render_template('portfolio.html',title='Portfolio' + portfolio,blogs=blogs,portfolio=portfolio,baseurl=siteconfig.AMAZON_BASE_URL)


@app.route('/photo/view/<slug>')
def photo_view(slug):
    logger.info("requested photo view")
    return render_template('about.html',title=slug)


@app.route('/about')
def about():
    logger.info("requested about")
    return render_template('about.html',title='Visual Intrigue Photography',container="container")


@app.route('/admin/collection/create', methods=['GET', 'POST'])
@flask_login.login_required
def collection_add():
    logger.info("requested add collection")

    form = CollectionForm(request.form)

    if(request.method == 'POST' and form.validate()):
        # Make sure that this contains a unique slug, since we are basing URLS off the slug
        # and these should be unqiue
        collection = mongo.db.collections.find_one({'slug':form.slug.data})

        if collection:
            flash('Slug already exists for collection entry, please use a different one.','alert-warning')
            return render_template('createcollection.html',title='Create New Collection Post',form=form)
        
        mongo.db.collections.insert(
          {
            "slug": util.slugify(form.slug.data),
            "title": form.title.data,
            "body": form.body.data,
            "status": "active",
            "created": datetime.now(),
            "updated": datetime.now(),
            "keywords": form.keywords.data,
            "collection": form.collection.data,
            "uuid" : uuid.uuid4()
          }
        )
        
        flash('Collection entry successfully created','alert-success')
        return redirect('/admin/collection/list')
    
    return render_template('createcollection.html',title='Create New Collection',form=form)


@app.route('/admin/collection/edit/<id>',methods=['GET', 'POST'])
@flask_login.login_required
def collection_edit(id=None):
    logger.info("requested add collection")
    
    if id is None:
        flash('Could not find photo entry for id provided','alert-warning')
        
    result = {}
    form = CollectionForm()
    # Make sure that this contains a unique slug, since we are basing URLS off the slug
    # and these should be unqiue
    collection = mongo.db.collections.find_one({'slug':id})    
    form.body.data = collection['body']
    form.title.data = collection['title']
    form.slug.data = collection['slug']
    form.active.data = collection['status']
    if 'collection' in collection:
        form.collection.data = collection['collection']
    if 'keywords' in collection:
        form.keywords.data = collection['keywords']     

    if(request.method == 'POST'):
        form = CollectionForm(request.form)

        if(form.validate()):
            
            # If the slug is different, then we need to check that it is not in use 
            if collection['slug'] != form.slug.data:
                logger.info("Found duplicate slug")
                slugcount = mongo.db.collections.count({'slug':form.slug.data})
                if slugcount >= 1:
                    flash('Slug already in use. Please select a unique slug','alert-warning')
                    return render_template('editcollection.html',title='Edit Collection Post',id=id,form=form, collection=collection) 
            
            mongo.db.collections.update(
               {
                "slug":id,
               },
               {
                 "slug": util.slugify(form.slug.data),
                 "title": form.title.data,
                 "body": form.body.data,
                 "status": form.active.data,    
                 "updated": datetime.now(),
                 "created": collection['created'],
                 "collection": form.collection.data,
                 "keywords": form.keywords.data,
                 "uuid": uuid.uuid4()
               }            
            )

            return redirect('/admin/collection/list')
        else:
            flash('Validation Error','alert-warning')
            
    return render_template('editcollection.html',title='Edit Collection Post',id=id,form=form, collection=collection)    


@app.route('/admin/photo/create/<id>', methods=['GET', 'POST'])
@flask_login.login_required
def photo_add(id):
    logger.info("requested add photo")

    # get the collection slug
    collection = mongo.db.collections.find_one({'slug':id})
    if collection is None:
        return redirect(url_for('error'))    

    collections = mongo.db.collections.find().sort([("collection",pymongo.ASCENDING),])
    # generate array of tuples
    collection_list = [('none','none'),]
    for collectionitem in collections:
        if 'collection' in collectionitem:
            collection_list.append((collectionitem['collection'],collectionitem['collection']))
            logger.debug(collectionitem['collection'])
    
    form = PhotoForm(request.form)
    
    form.collection.data = collection['collection']
    
    form.collection.choices = collection_list
    
    if(request.method == 'POST' and form.validate()):        
        logger.info("dumping " + str(request.files['photo']))
        result = util.save_file(request.files['photo'])
        if result['status'] is False:
            flash("No file has been provided, please select a file","alert-warning")
            return render_template('createphoto.html',title='Create New Photo Post',form=form,collection=collection)
        form.newimage = 1
        
        # Make sure that this contains a unique slug, since we are basing URLS off the slug
        # and these should be unqiue
        photo = mongo.db.photos.find_one({'slug':form.slug.data})

        if photo:
            flash('Slug already exists for photo entry, please use a different one.','alert-warning')
            return render_template('createphoto.html',title='Create New Photo Post',form=form,collection=collection)
        
        collection_single = mongo.db.collections.find_one({"collection":form.collection.data})
        
        if collection_single is None:
            collection_single = {}
            collection_single['slug'] = 'none'

        
        mongo.db.photos.insert(
          {
            "slug": util.slugify(form.slug.data),
            "title": form.title.data,
            "body": form.body.data,
            "status": "active",
            "created": datetime.now(),
            "updated": datetime.now(),
            "files": result['files'],
            "exif":result['exif'],
            "portfolio": form.portfolio.data,
            "keywords": form.keywords.data,
            "homepage": form.homepage.data,
            "displayorder": form.displayorder.data,
            "lat": form.lat.data,
            "lng": form.lng.data,
            "collection": form.collection.data,
            "collection_slug": collection_single['slug'],
            "uuid": uuid.uuid4()
            
          }
        )
        
        flash('Photo entry successfully created','alert-success')
        return redirect('/admin/photo/list/' + collection['slug'])
    
    return render_template('createphoto.html',title='Create New Blog Post',form=form,collection=collection)


@app.route('/admin/photo/list/<id>')
@flask_login.login_required
def photo_list_collection(id):
    logger.info("requested photo list")
    
    collection = mongo.db.collections.find_one({'slug':id})
    if collection is None:
        return redirect(url_for('error'))
    
    photos = mongo.db.photos.find({'collection':collection['collection']}).sort("created",-1)
    if photos is None:
        return redirect(url_for('error'))
    
    return render_template('photo_list.html',title='Manage Photo Entries',photos=photos,collection=collection)


@app.route('/admin/photo/list')
@flask_login.login_required
def photo_list():
    #logger.info("requested blog list")
    #blogs = mongo.db.blog.find().sort("created",-1)    
    #return render_template('blog_list.html',title='Manage Blog Entries',blogs=blogs)
    return redirect(url_for('error'))

@app.route('/admin/collection/list')
@flask_login.login_required
def collection_list():
    logger.info("requested blog list")
    collections = mongo.db.collections.find().sort("created",-1)
    return render_template('collection_list.html',title='Collection List',collections=collections)


@app.route('/admin/collection/delete/<id>',methods=['GET'])
@flask_login.login_required
def collection_delete(id=None):
    
    if id is None:
        flash("Invalid blog id passed to delete function!",'alert-warning')
        return redirect(url_for('blog_list'))
    
    collection = mongo.db.collections.find_one({'slug':id})
    if collection:
        slugcount = mongo.db.blog.count({'collection':collection['collection']})
        if slugcount >= 1:
            flash('Collection has blogs associated with it, please remove them before deleting the collection','alert-warning')
            return redirect(url_for('collection_list')) 

        mongo.db.collections.remove({'slug':id})
        
        flash("Collection entry deleted",'alert-success')
    
        logger.info("requested collection delete")
        return redirect(url_for('collection_list'))

    flash('Error deleting collection entry.  Please see logs for details.')
    return redirect(url_for('error'))


@app.route('/admin/photo/delete/<id>',methods=['GET'])
@flask_login.login_required
def blog_delete(id=None):
    
    if id is None:
        flash("Invalid photo id passed to delete function!",'alert-warning')
        return redirect(url_for('photo_list'))
    
    photo = mongo.db.photos.find_one({'slug':id})
    

    if photo:
        if 'files' not in blog:
            try:
               util.delete_image(blog['original'])
               util.delete_image(blog['thumb']['path'])
               util.delete_image(blog['medium']['path'])
               util.delete_image(blog['lrmedium']['path'])
               util.delete_image(blog['large']['path'])
               util.delete_image(blog['lrlarge']['path'])
            except Exception as e:
                logger.error("Error deleting photo %s with error: %s" %(id,e))
        mongo.db.blog.remove({'slug':id})
        
        flash("Photo entry deleted",'alert-success')
    
        logger.info("requested photo delete")
        return redirect('/admin/photos/list/' + blog['collection_slug'])

    flash('Error deleting photo entry.  Please see logs for details.')
    return redirect(url_for('error'))


def getCollectionChoices():
    photo = mongo.db.photos.find_one({'slug':id})    

    collections = mongo.db.collections.find().sort([("collection",pymongo.ASCENDING),])

    # generate array of tuples
    collection_list = [('none','none'),]
    for collection in collections:
        if 'collection' in collection:
            collection_list.append((collection['collection'],collection['collection']))
    
    return collection_list

    
@app.route('/admin/photo/edit/<id>',methods=['GET', 'POST'])
@flask_login.login_required
def blog_edit(id=None):
    logger.info("requested add photo")
    
    if id is None:
        flash('Could not find photo entry for id provided','alert-warning')
    
    result = {}
    form = PhotoForm()
    # Make sure that this contains a unique slug, since we are basing URLS off the slug
    # and these should be unqiue
    photo = mongo.db.photos.find_one({'slug':id})
    if photo is None:
        flash('Could not find photo entry for id provided','alert-warning')
        return redirect(url_for('error'))  
    collection = {'collection':'none','slug':'none'}

    if 'collection' in photo: 
        collection = mongo.db.collections.find_one({'collection':photo['collection']})
    if collection is None:
        collection = {'collection':'none','slug':'none'}

    #form = BlogForm(request.form)
    form.body.data = photo['body']
    form.title.data = photo['title']
    form.slug.data = photo['slug']
    form.active.data = photo['status']
    
    form.lat.data = 0
    form.lng.data = 0
    
    if 'lat' in photo:
        form.lat.data = photo['lat']
    if 'lng' in photo:
        form.lng.data = photo['lng']
    
    if 'displayorder' in photo:
        form.displayorder.data = photo['displayorder']
    else:
        form.displayorder.data = '1'
        
    form.newimage = "0"
    if ('keywords') in photo:    
        form.keywords.data = photo['keywords']
    
    if ('portfolio') in photo:
        form.portfolio.data = photo['portfolio']
    else:
        form.portfolio.data = 'master'
    
    if('homepage') in photo:
        form.homepage.data = photo['homepage']
    
    result['files'] = photo['files']
    
    if 'exif' in photo:  
        result['exif'] = photo['exif']
    else:
        result['exif'] = {}
    
    image = "http://www.kickoff.com/chops/images/resized/large/no-image-found.jpg"
    if 'files' in photo:
        image = siteconfig.AMAZON_BASE_URL + photo['files']['medium']['path']
    
    collections = mongo.db.collections.find().sort([("collection",pymongo.ASCENDING),])
    # generate array of tuples
    collection_list = [('none','none'),]
    for c in collections:
        if 'collection' in c:
            collection_list.append((c['collection'],c['collection']))
            logger.debug(c['collection'])
    form.collection.choices = collection_list
    
    form.collection.data = collection['collection']

    if(request.method == 'POST'):
        form = BlogForm(request.form)
        # Add the list after the form instantiation because it will disapear otherwise
        form.collection.choices = collection_list

        if(form.validate()):

            logger.info("dumping " + str(request.files['photo']))
            #print(form.newimage)
            
            if form.newimage.data == "1": 
                result = util.save_file(request.files['photo'])
                if result['status'] is False:
                    flash("No file has been provided, please select a file","alert-warning")
                    return render_template('createimage.html',title='Create New Blog Post',form=form)
            
            # If the slug is different, then we need to check that it is not in use 
            if photo['slug'] != form.slug.data:
                logger.info("Found duplicate slug")
                slugcount = mongo.db.photos.count({'slug':form.slug.data})
                if slugcount >= 1:
                    flash('Slug already in use. Please select a unique slug','alert-warning')
                    return render_template('editphoto.html',title='Edit Blog Post',id=id,form=form, photo=photo) 
            
            collection_single = mongo.db.collections.find_one({"collection":form.collection.data})
            if collection_single is None:
                collection_single = {}
                collection_single['slug'] = 'none'
            
            mongo.db.photos.update(
               {
                "slug":id,
               },
               {
                 "slug": util.slugify(form.slug.data),
                 "title": form.title.data,
                 "body": form.body.data,
                 "status": form.active.data,    
                 "updated": datetime.now(),
                 "created": photo['created'],
                 "files": result['files'],
                 "exif":result['exif'],
                 "portfolio": form.portfolio.data,
                 "keywords": form.keywords.data,
                 "homepage": form.homepage.data,
                 "collection": form.collection.data,
                 "collection_slug": collection_single['slug'],
                 "lat": form.lat.data,
                 "lng": form.lng.data,
                 "displayorder":form.displayorder.data,
                 "uuid": uuid.uuid4(),
               }            
            )

            return redirect('/admin/photo/list/'+collection['slug'])
        else:
            flash('Validation Error','alert-warning')
            
    return render_template('editphoto.html',title='Edit Photo Post',id=id,form=form, photo=photo,image=image,collection=collection)    


@app.route('/stories/<id>')
def stories(id = None):
    """ Collection Detail Display """
    collection = None
    
    if id is not None:
        collection = mongo.db.collections.find_one({'slug':id})
        
    if collection is None:
        return redirect(url_for('notfound'))
    
    photos = mongo.db.photos.find({'collection':collection['collection'],'status':'active'}).sort('displayorder',1)

    description = util.summary_text(collection['body'])
    firstphoto = None
    if photos.count() > 0:
        firstphoto = photos[0]
        

    return render_template('story.html',title=collection['title'],
                           collection=collection,photos=photos,
                           baseurl=siteconfig.AMAZON_BASE_URL,
                           firstphoto=firstphoto,
                           description=description)


@app.route('/notfound',methods=['GET','POST'])
def notfound():
    
    return render_template('404.html',title='Page Not Found')

@app.route('/photo/<id>', methods=['GET'])
def photo(id=None):
    """
    Photo detail display
    """
    photo = None
    if id is not None:
        photo = mongo.db.photos.find_one({'slug':id}) 
    
    if photo is None:
        return redirect(url_for('notfound'))
     
    image_url = siteconfig.AMAZON_BASE_URL + photo['files']['large']['path']
    lowrez_url = siteconfig.AMAZON_BASE_URL + photo["files"]['lrlarge']['path']
    return render_template('photo.html',title=photo['title'],photo=photo,image_url=image_url,lowrez_url=lowrez_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("requested login")
    if request.method == 'GET':
        return render_template('login.html',title='')

    email = request.form['email']
     
    if email in siteconfig.USERS and request.form['pw'] == siteconfig.USERS[email]['pw']:
        user = User()
        user.id = email
        
        flask_login.login_user(user)
        flash('You were successfully logged in','alert-success')
        return redirect(url_for('collection_list'))

    return render_template('badlogin.html')


@app.route('/error', methods=['GET','POST'])
def error():
    return "ERROR"


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
    
    
@app.route('/logout')
@flask_login.login_required
def logout():
    """Logout the current user."""
    logger.info("requested logout")
    flask_login.logout_user()
    return redirect(url_for('index'))


@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html',title='Unauthorized Request')


@app.route('/article/<id>')
def article_view(id):
    """ View Article """
    article = mongo.db.articles.find_one({'slug':id})
    return render_template('article.html',title=article['title'],article=article)


@app.route('/admin/article/list')
@flask_login.login_required
def article_list():
    """ List articles """
    articles = mongo.db.articles.find().sort("created",-1)
    
    return render_template('article_list.html',title="List Articles",articles=articles   )


@app.route('/admin/article/create',methods=['GET', 'POST'])
@flask_login.login_required
def article_create():
    """ Create article """
    
    form = ArticleForm()
    
    if(request.method == 'POST'):
        form = ArticleForm(request.form)
        
        if(form.validate()):
            
            article = mongo.db.articles.find_one({'slug':form.slug.data})
    
            if article:
                flash('Slug already exists for article, please use a different one.','alert-warning')
                return render_template('createarticle.html',title='Create New Article',form=form,)
     
            mongo.db.articles.insert(
              {
                "slug": util.slugify(form.slug.data),
                "title": form.title.data,
                "body": form.body.data,
                "status": form.active.data,
                "created": datetime.now(),
                "updated": datetime.now(),
                "keywords": form.keywords.data,
                "uuid": uuid.uuid4(),
                "headerurl": form.headerurl.data,
                "teaserurl": form.teaserurl.data
                
              }
            )
            
            flash('Article successfully created','alert-success')            
            
            return redirect('/admin/article/list')
        else:
            flash('Validation Error','alert-warning')
    
    return render_template('createarticle.html',title="Create Article",form=form)


@app.route('/admin/article/edit/<id>',methods=['GET', 'POST'])
@flask_login.login_required
def article_edit(id):
    """ Edit article """
    
    if id is None:
        flash("Invalid article id passed to delete function!",'alert-warning')
        return redirect(url_for('article_list'))
    
    form = ArticleForm()
    article = mongo.db.articles.find_one({'slug':id})
    if article is None:
        flash('Could not find article for id provided','alert-warning')
        return redirect(url_for('error'))  

    #form = BlogForm(request.form)
    form.body.data = article['body']
    form.title.data = article['title']
    form.slug.data = article['slug']
    form.active.data = article['status']
    if 'headerurl' in article:
        form.headerurl.data = article['headerurl']

    if 'teaserurl' in article:
        form.teaserurl.data = article['teaserurl']

    form.keywords.data = article['keywords']

    if(request.method == 'POST'):
        form = ArticleForm(request.form)
        if(form.validate()):
            # If the slug is different, then we need to check that it is not in use 
            if article['slug'] != form.slug.data:
                slugcount = mongo.db.articles.count({'slug':form.slug.data})
                if slugcount >= 1:
                    flash('Slug already in use. Please select a unique slug','alert-warning')
                    return render_template('editarticle.html',title='Edit Article',id=id,form=form) 
    
     
            mongo.db.articles.update(
              {
                "slug":id,
              },
              {
                "slug": util.slugify(form.slug.data),
                "title": form.title.data,
                "body": form.body.data,
                "status": form.active.data,
                "updated": datetime.now(),
                'created': article['created'],
                "keywords": form.keywords.data,
                "headerurl": form.headerurl.data,
                "teaserurl": form.teaserurl.data
              }
            )
            
            flash('Article successfully updated','alert-success')            
            
            return redirect('/admin/article/list')
        else:
            flash('Validation Error','alert-warning')
    
    return render_template('editarticle.html',title="Edit Article",form=form,id=id)


@app.route('/admin/article/delete/<id>')
@flask_login.login_required
def article_delete(id):
    """ delete article by id """
    if id is None:
        flash("Invalid article id passed to delete function!",'alert-warning')
        return redirect(url_for('article_list'))
    
    article = mongo.db.articles.find_one({'slug':id})
    
    if article:

        mongo.db.articles.remove({'slug':id})
        
        flash("Article deleted",'alert-success')

        return redirect('/admin/article/list')

    flash('Error deleting article.  Please see logs for details.')
    return redirect(url_for('error'))

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
    
