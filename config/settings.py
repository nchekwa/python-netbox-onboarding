from os import environ 
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))


import http.server
import socketserver
import threading
import os
import socket



def init():
    global yaml
    global rest
    yaml = {}
    rest = {}

def init_http_header():
    global headers
    headers={
        'Authorization': 'Token ' + yaml['netbox_token'],
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


def init_http_server(path, port):
    main_path = os.getcwd()
    web_dir = os.path.join('/', *main_path.split("/") , *path.split("/") )
    #print(os.getcwd())
    #print(web_dir)
    os.chdir(web_dir)
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    sa = httpd.socket.getsockname()
    print ("Serving HTTP on", sa[0], "port", sa[1], "...")
    httpd.serve_forever()

def start_http_thread(path='.', port=8011):
    daemon = threading.Thread(name='init_http_server',
                            target=init_http_server,
                            args=(path, port))
    daemon.setDaemon(True) 
    daemon.start()
