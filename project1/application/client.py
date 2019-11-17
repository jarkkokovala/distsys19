import requests
import socket
import threading
import json
from urllib.parse import urlparse
from requests.exceptions import HTTPError
import time

class Client:
  
  def __init__(self, ip_address, port, name_node_ip_address, name_node_port):
    """
    Initialize the node
    :param ip_address: Ip address
    :param port: Port number
    :param name_node_ip_address: ip address of the name node
    :param name_node_port: port of the name node
    :return:
    """
    self.address = (ip_address, port)
    self.name_node_address = (name_node_ip_address, name_node_port)
  
  def request_a_filenode(self, file_name=""):
    url = 'http://%s:%i/filenode' % self.name_node_address
    params = {
        'ip_address': self.address[0],
        'port': self.address[1],
        'file_name': file_name}
    try:
        response = requests.get(url=url, params=params)
        if response.status_code == 200:
          rjson = response.json()
          file_node = (rjson['ip_address'], rjson['port'])
          return file_node
        else:
          print("No filenodes available")
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    return None
  
  def send_file_to_filenode(self, file_node, file_name, content):
    url = 'http://%s:%i/newfile' % file_node
    data = {
      'content': content
    }
    jsondata = json.dumps(data).encode()
    headers = {
      'Content-Length': bytes(len(jsondata)),
      'File-Name': file_name,
      'File-Modification-Time': str(time.time()),
      'Instrumentation-Id': ""
    }
    response = requests.put(url=url, data=jsondata, headers=headers)
    return response.status_code
  
  def request_file_from_filenode(self, file_name, file_node):
    url = 'http://%s:%i/file' % file_node
    headers = {
      'File-Name': file_name
    }
    try:
      response = requests.get(url=url, headers=headers)
      if response.status_code == 200:
        text = response.json()['content']
        return text
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    return None

  def get_file(self, file_name):
    # TODO: This is where the actual file loading happens
    while True:
      print("Give some content to the file:")
      content = input()
      if len(content) > 0:
        return content

  def ask_file_name(self):
    fileName = None
    while True:
      print("Name of the file:")
      fileName = input()
      if 0 < len(fileName) <= 20:
        return fileName
  
  def save_new_file(self):
    fileName = self.ask_file_name()
    content = self.get_file(fileName)
    file_node = self.request_a_filenode()
    print("FileNode:", file_node)
    res = self.send_file_to_filenode(file_node, fileName, content)
    if res == 200:
      print("\nSUCCESSFULLY SAVED FILE %s\n" % fileName)
    else:
      print("\nCOULD NOT SAVE FILE %s\n" % fileName)
    self.start_ui()
  
  def fetch_file(self):
    fileName = self.ask_file_name()
    file_node = self.request_a_filenode(fileName)
    file = self.request_file_from_filenode(fileName, file_node)
    if file:
      print("\n*********************** %s ***********************\n" % fileName)
      print(file)
      print("\n********************************************************\n")
    else:
      print("\nCOULD NOT READ FILE %s\n" % fileName)
    self.start_ui()
  
  def start_ui(self):
    action = None
    while True:
      print("Choose one of the options:")
      print("(1) Save a file")
      print("(2) Read a file")
      print("(q) Quit")
      action = input()
      if action == "q":
          break
      try:
        if 1 <= int(action) <= 2:
          break
      except ValueError:
        continue
    
    if action == "q":
      print("Quitting")
    elif action == "1":
      self.save_new_file()
    elif action == "2":
      self.fetch_file()

  
  def run(self):
    self.start_ui()
