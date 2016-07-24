import re
import unicodedata
from werkzeug import secure_filename
import os
from visualintrigue import siteconfig
from datetime import datetime
import uuid
import boto3
import boto.s3.connection
import subprocess




def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
  

def save_file(file):
    
    #n = datetime.now()
    #t = n.timetuple()
    #y, m, d, h, min, sec, wd, yd, i = t

    if file:

        #filename = secure_filename(file.filename)
        #file.save(os.path.join(siteconfig.UPLOAD_PATH, filename))
        #uploadpath = os.path.join(siteconfig.UPLOAD_PATH, str(y), str(m), str(d), str(h), str(min), str(sec))
        
        #pathtodir(uploadpath)
        
        path_uuid = str(uuid.uuid4())
        
        orig_filename = path_uuid + "_orig.jpeg"
        
        
        file.save(os.path.join(siteconfig.UPLOAD_PATH,orig_filename))
        
        file_array = [os.path.join(siteconfig.UPLOAD_PATH,orig_filename)]
        image_dict = {'original':orig_filename}
        
        # create small thumbnail
        resize_image(os.path.join(siteconfig.UPLOAD_PATH,orig_filename),50,os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_50px.jpeg"))
        file_array.append(os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_50px.jpeg"))
        
        image_dict['thumb'] = {'path':path_uuid + "_50px.jpeg"}
        (width,height) = get_image_size(os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_50px.jpeg"))
        image_dict['thumb'] = {'width':width,'height':height,'path':path_uuid + "_50px.jpeg"}
        
        
        # create medium thumb
        resize_image(os.path.join(siteconfig.UPLOAD_PATH,orig_filename),900,os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_900px.jpeg"))
        file_array.append(os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_900px.jpeg"))
        
        image_dict['medium'] = {'path':path_uuid + "_900px.jpeg"}
        (width,height) = get_image_size(os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_900px.jpeg"))
        image_dict['medium'] = {'width':width,'height':height,'path':path_uuid + "_900px.jpeg"}
        
        # create fullsize image
        resize_image(os.path.join(siteconfig.UPLOAD_PATH,orig_filename),1600,os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_1600px.jpeg"))
        file_array.append(os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_1600px.jpeg"))
        

        (width,height) = get_image_size(os.path.join(siteconfig.UPLOAD_PATH,path_uuid + "_1600px.jpeg"))
        image_dict['large'] = {'width':width,'height':height,'path':path_uuid + "_1600px.jpeg"}

        
        
        # upload file(s) to s3
        for uploadfile in file_array:
            
            s3 = boto3.resource('s3',aws_access_key_id=siteconfig.AMAZON_KEY, aws_secret_access_key=siteconfig.AMAZON_SECRET)
            data = open(os.path.join(siteconfig.UPLOAD_PATH,uploadfile), 'rb')
            s3.Bucket(siteconfig.AMAZON_BUCKET).put_object(Key=os.path.basename(uploadfile), Body=data, ContentType='image/jpeg')
            data.close()
        
        bare_files_list = []
        # clean up the files
        for uploadfile in file_array:
            os.remove(uploadfile)
            bare_files_list.append(os.path.basename(uploadfile))
        
        return {'status':True,'message':"File upload was a success", 'files':image_dict}
    else:
        return {'status':False,'message':"No file provided",'files':None}

def delete_image(files = {}):
    
    # upload file(s) to s3
    for s3file in files:
        
        s3 = boto3.resource('s3',aws_access_key_id=siteconfig.AMAZON_KEY, aws_secret_access_key=siteconfig.AMAZON_SECRET)
        
        bucket = s3.Bucket(siteconfig.AMAZON_BUCKET)
        
        key = s3.Key(s3file)
        
        bucket.delete_key(key)
    

def resize_image(filepath,width,dest):
    """ Resize an image with fixed width and maintain aspect ratio """
    
    try:
        proc = subprocess.Popen([siteconfig.CONVERT_COMMAND,filepath,'-quality','100','-quality','85','-resize', str(width) +'x',dest],stdout=subprocess.PIPE)
    
        output = proc.communicate()[0]
        print(output)
        return True
    except Exception as e:
        raise(Exception("Error converting image file with error: %s" %(e)))
    
    return False

def get_image_size(filepath):
    width = 0
    height = 0
    try:
        dim = subprocess.Popen([siteconfig.IDENTIFY_COMMAND,"-format","\"%w,%h\"",filepath], stdout=subprocess.PIPE).communicate()[0]
        (width, height) = [ int(x) for x in re.sub('[\t\r\n"]', '', dim.decode()).split(',') ]
    except Exception as e:
        raise Exception("Error obtaining dimensions of the image: %s"%(str(e)))
    
    return (width, height)




def pathtodir(path):
    if not os.path.exists(path):
        l=[]
        p = "/"
        l = path.split("/")
        i = 1
        while i < len(l):
            p = p + l[i] + "/"
            i = i + 1
            if not os.path.exists(p):
                os.mkdir(p)
def main():
    pass


if __name__ == "__main__":
    main()
    
