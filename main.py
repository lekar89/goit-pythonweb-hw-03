import mimetypes
import json
from pathlib import Path
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from helper import add_response_to_db
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
storage_dir = BASE_DIR / 'storage'
storage_dir.mkdir(exist_ok=True)
data_file = storage_dir / 'data.json'
jinja = Environment(loader=FileSystemLoader("templates"))



class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message':
                self.send_html('message.html')
            case '/read':
                self.render_template('read.jinja')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', 404)

    def do_POST(self):
        size = self.headers.get("Content-Length")
        body = self.rfile.read(int(size)).decode('utf-8')
        parse_body = urllib.parse.unquote_plus(body)
        r = parse_body.split('&')
        r = {item.split('=')[0]: item.split('=')[1] for item in r}
        messages = {}
        timestamp = datetime.now().isoformat()
        messages[timestamp] = r
        add_response_to_db(messages, data_file)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def render_template(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(data_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        template = jinja.get_template(filename)
        content = template.render(messages=data)
        self.wfile.write(content.encode())

    def send_html(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static(self, file):
        self.send_response(200)
        self.send_header('Content-type', mimetypes.guess_type(file)[0])
        self.end_headers()
        with open(file, 'rb') as file:
            self.wfile.write(file.read())


    
        



def run():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, Handler)
    print('Starting server...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Server is shutting down...')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run()