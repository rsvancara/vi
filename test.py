import os
import unittest
import tempfile
from flask import Flask
from visualintrigue import siteconfig
from visualintrigue import util
from visualintrigue import app
#import run




class VisualIntrigueTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, vitest.app.config['DATABASE'] = tempfile.mkstemp()
        #app = Flask('visualintrigue')
        app.secret_key = siteconfig.SECRETKEY 
        self.app_context = app.app_context()
        self.app_context.push()
        app.testing = True
        self.app = app.test_client()
        


    def tearDown(self):
        pass
        #os.close(self.db_fd)
        #os.unlink(vitest.app.config['DATABASE'])


    def test_about_status_code(self):

        result = self.app.get('/about')
        print(result) 
        self.assertEqual(result.status_code,200)




if __name__ == '__main__':
    unittest.main()
