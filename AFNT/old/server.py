import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/WebPage/html/1_login.html'
        try:
            # Get the directory of the script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the relative file path
            file_path = os.path.join(script_dir, '' + self.path.replace('/', os.path.sep)[1:])
            # print("Opened File!")
            # print("Attempting to open file:", file_path)

            with open(file_path, 'r', encoding='utf-8') as file:
                file_to_open = file.read()
                # print("File content:", file_to_open)

            self.send_response(200)
        except FileNotFoundError as e:
            file_to_open = f"File Not Found: {e}"
            self.send_response(404)
        except Exception as e:
            file_to_open = f"Error reading file: {e}"
            self.send_response(500)  # Internal Server Error
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
    
    def do_POST(self):
        pass

if __name__ == "__main__":
    httpd = HTTPServer(('localhost', 8080), Server)
    print("Connection Established!")
    httpd.serve_forever()