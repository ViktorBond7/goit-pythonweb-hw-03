from fileinput import filename
import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("."))


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        # path to json file
        file_path = "storage/data.json"

        current_time = str(datetime.now())
        new_entry = {current_time: data_dict}

        # read existing data from file if it exists, otherwise start with an empty dictionary
        data_to_save = {}

        if not os.path.exists("storage"):
            os.makedirs("storage")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as fd:
                try:
                    data_to_save = json.load(fd)
                except json.JSONDecodeError:
                    # If the file is empty or corrupted, we can start with an empty dictionary
                    data_to_save = {}

        # 3. Add the new entry to the dictionary
        data_to_save.update(new_entry)

        # 4. Write the updated dictionary back to the file
        with open(file_path, "w", encoding="utf-8") as fd:
            json.dump(data_to_save, fd, ensure_ascii=False, indent=4)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.send_template("info.html")

        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        with open(filename, "rb") as fd:
            self.send_response_with_body(fd.read(), status=status)

    def send_response_with_body(
        self, body: bytes, content_type="text/html", status=200
    ):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(body)

    def send_template(self, filename):
        messages_list = self.fetch_data("storage/data.json")
        if not messages_list:
            messages_list = {"No messages": {"username": "N/A", "message": "N/A"}}
        template = env.get_template(filename)
        rendered_html = template.render(messages_list=messages_list)

        self.send_response_with_body(rendered_html.encode("utf-8"))

    def fetch_data(self, filename):
        if not os.path.exists(filename):
            return {}

        with open(filename, "r", encoding="utf-8") as fd:
            try:
                return json.load(fd)
            except json.JSONDecodeError:
                return {}

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
