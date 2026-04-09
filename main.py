import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os
from datetime import datetime

print("Current working directory:", os.getcwd())
class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print(f"POST path: {self.path}")
        data = self.rfile.read(int(self.headers['Content-Length']))
        print("data:", data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print("data_parse:", data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print("data_dict:", data_dict)
        
        # path to json file
        file_path = 'storage/data.json'

        
        current_time = str(datetime.now())
        new_entry = {current_time: data_dict}

        # read existing data from file if it exists, otherwise start with an empty dictionary
        data_to_save = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as fd:
                try:
                    data_to_save = json.load(fd)
                except json.JSONDecodeError:
                    # If the file is empty or corrupted, we can start with an empty dictionary
                    data_to_save = {}

        # 3. Add the new entry to the dictionary
        data_to_save.update(new_entry)

        # 4. Write the updated dictionary back to the file
        with open(file_path, 'w', encoding='utf-8') as fd:
            json.dump(data_to_save, fd, ensure_ascii=False, indent=4)
                

           
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        print("pr_url:", pr_url)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 8080)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()