import os
import json
import requests
import configparser
from datetime import datetime
from subprocess import Popen, PIPE

def get_server_url():
  config = configparser.ConfigParser()
  config.read('supermarket.ini')
  return f"http://localhost:{int(config['POSTGREST']['server-port'])}/rpc"

def call_server(method, data):
  res = requests.post(url="/".join([get_server_url(), method]), data=data)
  if res.status_code != 200:
    raise RuntimeError(res.text)
  return res.text

def read_config(config_path):
  config = configparser.ConfigParser()
  config.read(config_path)
  return json.loads(config['MARKET']['weight_ranges_start']), json.loads(config['MARKET']['weight_ranges_probs']), \
    json.loads(config['MARKET']['distance_ranges_start']), json.loads(config['MARKET']['distance_ranges_probs']), \
    float(config['MARKET']['price_per_km']), float(config['MARKET']['price_per_kg']), \
    json.loads(config['REPAIRS']['repair_names']), json.loads(config['REPAIRS']['n_parts']), \
    json.loads(config['REPAIRS']['repair_costs']), json.loads(config['REPAIRS']['repair_probs']), \
    int(config['DRONE']['drone_n']), float(config['DRONE']['max_drone_load']), float(config['DRONE']['max_drone_speed']), \
    int(config['GENERAL']['time_factor']), config['GENERAL']['data_path'], config['GENERAL']['log_path'], \
    [int(config['POSTGREST']['server-port']), config['POSTGREST']['db-uri'], config['POSTGREST']['db-schema'], config['POSTGREST']['db-anon-role']]

def create_postgrest_conf(conf_values):
  server_port, db_uri, db_schema, db_anon_role = conf_values
  with open('postgrest.conf', 'w') as f:
    f.write(f'db-uri = {db_uri}\ndb-schema = {db_schema}\ndb-anon-role = {db_anon_role}\nserver-port = "{server_port}"')

def init_data_file(data_path, param_names):
  if os.path.isdir(os.path.split(data_path)[0]) is False:
    raise Exception(f'Please create required dirs manually for: {data_path}')
  
  if os.path.isfile(data_path) is False: 
    with open(data_path, 'w') as f:
      f.write(','.join(['drone_idx'] + param_names))

def init_log_file(log_path):
  if os.path.isdir(os.path.split(log_path)[0]) is False:
    raise Exception(f'Please create required dirs manually for: {log_path}')
  
  if os.path.isfile(log_path) is False: 
    with open(log_path, 'w') as f:
      pass

def decode_clean(input):
  if input is not None:
    return input.decode('utf-8').strip()
  return input

def logging(log_path, message):
  with open(log_path, "a") as f:
    f.write(f"[{datetime.now()}] {message}\n")

def get_pid(p):
  out, err = p.communicate()
  return decode_clean(out), decode_clean(err)

def open_pipe(cmd):
  return Popen(cmd, stdout=PIPE, stderr=PIPE)