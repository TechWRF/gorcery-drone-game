import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'supermarket'))

from retail import SuperMarket
from utils import call_server, init_data_file, init_log_file, read_config, create_postgrest_conf, logging, get_pid, open_pipe
from time import sleep

class Conductor(SuperMarket):
  def __init__(self):
    self.weight_ranges_start, self.weight_ranges_probs, \
    self.distance_ranges_start, self.distance_ranges_probs, \
    self.price_per_km, self.price_per_kg, \
    self.repair_names, self.n_parts, \
    self.repair_costs, self.repair_probs, \
    self.drone_n, self.max_drone_load, self.max_drone_speed, \
    self.time_factor, self.data_path, self.log_path, \
    postgrest_conf_values = \
      read_config('supermarket.ini')

    create_postgrest_conf(postgrest_conf_values)

    SuperMarket.__init__(self)
    init_data_file(self.data_path, self.param_names)
    init_log_file(self.log_path)

    self.shop_open = False
    self.stream_pid = None
    self.server_pid = None 

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

  def stop_process(self, pid):
    if pid is not None:
      open_pipe(['bash', '-c', f'if ps -p {pid} > /dev/null; then kill {pid}; fi'])

  def close_if_error(self, err):
    if err is not None and len(err) > 0 and 'NOTICE:' not in err:
      logging(self.log_path, err)
      self.close_shop()
      raise RuntimeError(err)

  def close_shop(self):
    self.stop_process(self.stream_pid)
    self.stream_pid = None
    logging(self.log_path, "Streamer stopped")

    self.stop_process(self.server_pid)
    self.server_pid = None
    logging(self.log_path, "Server stopped")

    self.shop_open = False
    logging(self.log_path, "------- Shop closed -------")

  def open_shop(self):
    # TODO: escape sleep
    logging(self.log_path, "------- Opening Shop -------")
    self.shop_open = True

    self.time_now = self.get_current_time()
    logging(self.log_path, f"Current game time: {self.time_now}")

    while self.shop_open:
      try:
        self.handle_orders()
      except KeyboardInterrupt:
        self.close_shop()
        return
        
      if self.stream_pid is None:
        self.stream_pid, err = get_pid(open_pipe(['./scripts/streamer.sh']))
        self.close_if_error(err)
        logging(self.log_path, "Streamer is running")

      if self.server_pid is None:
        self.server_pid, err = get_pid(open_pipe(['./scripts/server.sh']))
        self.close_if_error(err)
        sleep(1)
        logging(self.log_path, "Server started")
        
        self.load_drones()
        logging(self.log_path, "Drones loaded")

        self.add_repair_types()
        logging(self.log_path, "Repair types added")

if __name__ == '__main__':
  conductor = Conductor()
  conductor.open_shop()