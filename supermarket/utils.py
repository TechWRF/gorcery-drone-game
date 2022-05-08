import requests
import configparser

def get_server_url():
    config = configparser.ConfigParser()
    config.read('supermarket.ini')
    return f"http://localhost:{int(config['POSTGREST']['server-port'])}/rpc"

def call_server(method, data):
  res = requests.post(url="/".join([get_server_url(), method]), data=data)
  if res.status_code != 200:
    raise RuntimeError(res.text)
  return res.text