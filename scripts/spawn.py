import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'supermarket'))

import subprocess
from retail import SuperMarket
from time import sleep
import configparser
import json

class Conductor(SuperMarket):
  def __init__(self, config_path = 'supermarket.ini'):
    self.read_config(config_path)
    SuperMarket.__init__(self)
    self.controller = {"shop_open": False, "streamer_running": False, "server_running": False}

  def read_config(self, config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    self.weight_ranges_start = json.loads(config['MARKET']['weight_ranges_start'])
    self.weight_ranges_probs = json.loads(config['MARKET']['weight_ranges_probs'])

    self.distance_ranges_start = json.loads(config['MARKET']['distance_ranges_start'])
    self.distance_ranges_probs = json.loads(config['MARKET']['distance_ranges_probs'])

    self.price_per_km = float(config['MARKET']['price_per_km'])
    self.price_per_kg = float(config['MARKET']['price_per_kg'])

    self.drone_n = int(config['DRONE']['drone_n'])
    self.max_drone_load = float(config['DRONE']['max_drone_load'])
    self.max_drone_speed = float(config['DRONE']['max_drone_speed'])

    self.time_factor = int(config['GENERAL']['time_factor'])
    self.log_path = config['GENERAL']['log_path']
    if len(os.path.split(self.log_path)[0]) == 0:
      self.log_path = os.path.join(os.getcwd(), self.log_path)

    self.server_port = config['POSTGREST']['server-port']
    db_uri = config['POSTGREST']['db-uri']
    db_schema = config['POSTGREST']['db-schema']
    db_anon_role = config['POSTGREST']['db-anon-role']

    with open('postgrest.conf', 'w') as f:
      f.write(f"db-uri = {db_uri}\ndb-schema = {db_schema}\ndb-anon-role = {db_anon_role}\nserver-port = {self.server_port}")

  @staticmethod
  def get_stdout(p):
    out, err = p.communicate()
    if err is not None:
      err = err.decode('utf-8').strip()
      if len(err) > 0 and "No such process" not in err:
        raise RuntimeError(err)
    return out.decode('utf-8').strip()

  def open_shop(self):
    self.controller['shop_open'] = True
    print("Opening Shop")

    time_now = self.get_current_time()
    while self.controller['shop_open']:
      try:
        self.handle_orders(time_now)
      except KeyboardInterrupt:
        p = subprocess.Popen(['kill', stream_pid], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.get_stdout(p)

        p = subprocess.Popen(['kill', stream_pid], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.get_stdout(p)

        self.controller['streamer_running'] = False
        self.controller['shop_open'] = False
        print("\nStreamer stopped\nServer stopped\nShop closed")
        
      if self.controller['streamer_running'] is False and self.controller['shop_open']:
        print("Shop open\nStarting Streamer")
        sleep(1)
        streamer = subprocess.Popen(['./scripts/streamer.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stream_pid = self.get_stdout(streamer)
        print("Streamer is running")
        self.controller['streamer_running'] = True

      if self.controller['server_running'] is False and self.controller['shop_open']:
        print("Starting server")
        server = subprocess.Popen(['./scripts/server.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        server_pid = self.get_stdout(server)
        print(f"Server is listening on port {self.server_port}")
        self.controller['server_running'] = True

if __name__ == '__main__':
  conductor = Conductor()
  conductor.open_shop()