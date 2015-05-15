import json
import os
import openerp.tests

PORT = openerp.tools.config['xmlrpc_port']
DB = openerp.tools.config['db_name']

class NHPhantomJSTestCase(openerp.tests.HttpCase):

    def __init__(self, methodName='runTest'):
        super(NHPhantomJSTestCase, self).__init__(methodName)

    def phantom_js(self, url_path, code, ready="window", login=None, timeout=60, **kw):
        """ Test js code running in the browser
        - optionnally log as 'login'
        - load page given by url_path
        - wait for ready object to be available
        - eval(code) inside the page
        To signal success test do:
        console.log('ok')
        To signal failure do:
        console.log('error')
        If neither are done before timeout test fails.
        """
        options = {
            'port': PORT,
            'db': DB,
            'url_path': url_path,
            'code': code,
            'ready': ready,
            'timeout': timeout,
            'login': login,
            'session_id': self.session_id,
        }
        options.update(kw)
        options.setdefault('password', options.get('login'))
        phantomtest = os.path.join(os.path.dirname(__file__), 'nhphantomtest.js')
        cmd = ['phantomjs', phantomtest, json.dumps(options)]
        self.phantom_run(cmd, timeout)
