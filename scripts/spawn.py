import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'supermarket'))

import subprocess
from retail import SuperMarket
from utils import call_server
from time import sleep
import configparser
import json

class Conductor(SuperMarket):
  def __init__(self):
    self.read_config('supermarket.ini')
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

    self.repair_names = json.loads(config['REPAIRS']['repair_names'])
    self.n_parts = json.loads(config['REPAIRS']['n_parts'])
    self.repair_costs = json.loads(config['REPAIRS']['repair_costs'])
    self.repair_probs = json.loads(config['REPAIRS']['repair_probs'])

    self.drone_n = int(config['DRONE']['drone_n'])
    self.max_drone_load = float(config['DRONE']['max_drone_load'])
    self.max_drone_speed = float(config['DRONE']['max_drone_speed'])

    self.time_factor = int(config['GENERAL']['time_factor'])
    self.log_path = config['GENERAL']['log_path']
    if len(os.path.split(self.log_path)[0]) == 0:
      self.log_path = os.path.join(os.getcwd(), self.log_path)

    server_port = int(config['POSTGREST']['server-port'])
    db_uri = config['POSTGREST']['db-uri']
    db_schema = config['POSTGREST']['db-schema']
    db_anon_role = config['POSTGREST']['db-anon-role']

    with open('postgrest.conf', 'w') as f:
      f.write(f'db-uri = {db_uri}\ndb-schema = {db_schema}\ndb-anon-role = {db_anon_role}\nserver-port = "{server_port}"')

  def load_drones(self):
    for i in range(1, self.drone_n + 1):
      call_server("add_drone",
      {"_id": i, "_name": f"drone_{i}", "_max_load": self.max_drone_load, "_max_speed": self.max_drone_speed,
      "_price": 5000, "_started_serving_at": str(self.time_now)}
    )

  def add_repair_types(self):
    for name, cost in zip(self.repair_names, self.repair_costs):
      call_server("add_repair_type",
        {"_name": name, "_cost": cost }
      )

  @staticmethod
  def get_stdout(p):
    out, err = p.communicate()
    if err is not None:
      err = err.decode('utf-8').strip()
      if len(err) > 0 and "No such process" not in err and 'NOTICE:' not in err:
        raise RuntimeError(err)
    return out.decode('utf-8').strip()

  def open_shop(self):
    # TODO: add logging
    # TODO: escape sleep
    self.controller['shop_open'] = True
    print("Opening Shop")

    self.time_now = self.get_current_time()
    print(f"Current time: {self.time_now}")

    while self.controller['shop_open']:
      try:
        self.handle_orders()
      except KeyboardInterrupt:
        self.get_stdout(
          subprocess.Popen(['kill', stream_pid], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        )
        self.get_stdout(
          subprocess.Popen(['kill', server_pid], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        )
        self.controller['streamer_running'] = False
        self.controller['shop_open'] = False
        print("\nStreamer stopped\nServer stopped\nShop closed")
        
      if self.controller['streamer_running'] is False and self.controller['shop_open']:
        print("Shop open\nStarting Streamer")
        sleep(1)
        stream_pid = self.get_stdout(
          subprocess.Popen(['./scripts/streamer.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        )
        print("Streamer is running")
        self.controller['streamer_running'] = True

      if self.controller['server_running'] is False and self.controller['shop_open']:
        server_pid = self.get_stdout(
          subprocess.Popen(['./scripts/server.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        )
        print("Server started")
        self.controller['server_running'] = True

        sleep(1)
        self.load_drones()
        print("Drones loaded")
        self.add_repair_types()
        print("Repair types added")

if __name__ == '__main__':
  conductor = Conductor()
  conductor.open_shop()