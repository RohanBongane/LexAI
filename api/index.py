import os
import sys

# Ensure the root project directory is on the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

flask_app = create_app()

class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH', '')
        path_info = environ.get('PATH_INFO', '')
        
        # When Vercel rewrites to /api/index.py, HTTP_X_MATCHED_PATH holds the true requested route
        if matched_path and not matched_path.startswith('/api/index'):
            environ['PATH_INFO'] = matched_path
        elif path_info.startswith('/api/index.py'):
            rest = path_info[len('/api/index.py'):]
            environ['PATH_INFO'] = rest if (rest and rest.startswith('/')) else ('/' + rest if rest else '/')
        elif path_info.startswith('/api/index'):
            rest = path_info[len('/api/index'):]
            environ['PATH_INFO'] = rest if (rest and rest.startswith('/')) else ('/' + rest if rest else '/')
            
        return self.wsgi_app(environ, start_response)

flask_app.wsgi_app = VercelPathMiddleware(flask_app.wsgi_app)
app = flask_app
