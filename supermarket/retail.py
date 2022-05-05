from time import sleep
from datetime import datetime, timedelta
import random
from dispatcher import Dispatch
import os
import uuid

class SuperMarket():
  def __init__(self, drone_n = 10, time_factor = 1, log_path = 'data.csv'):
    # TODO: move config to file
    #market config
    self.weight_ranges_start = [1, 15, 30, 60, 90, 100] # in kg
    self.weight_ranges_probs = (47, 38, 10, 4, 1, 0)

    self.distance_ranges_start = [1, 3, 5, 7, 9, 10] # in km
    self.distance_ranges_probs = (53, 31, 11, 3, 2, 0)

    self.price_per_km = 0.5
    self.price_per_kg = 0.5

    # drone config
    # drone_n
    self.max_drone_load = 30 # in kg
    self.max_drone_speed = 75 # in km/s

    # general config
    self.time_factor = time_factor
  
    self.drone_params = {}
    self.param_names = ['order_id', 'order_placed_at', 'weight', 'distance', 'packaging_duration', 'price', 'order_sent_at', 'order_completed_at']
    [self.init_drone_params(idx) for idx in range(drone_n)]

    self.log_path = log_path
    self.init_log()

  def init_log(self):
    if os.path.isfile(self.log_path) is False: 
      with open(self.log_path, 'w') as f:
        f.write(','.join(['drone_idx'] + self.param_names))

  def init_drone_params(self, drone_idx):
    self.drone_params[drone_idx] = {'is_dispatched': False}
    for name in self.param_names:
      self.drone_params[drone_idx][name] = None

  @staticmethod
  def get_rand_value(ranges_start, ranges_probs):
    start = random.choices(ranges_start, ranges_probs)[0]
    end_idx = ranges_start.index(start) + 1
    range_end = ranges_start[end_idx]
    return random.randint(start, range_end)

  def place_order(self, time_now):
    return time_now, \
      self.get_rand_value(self.weight_ranges_start, self.weight_ranges_probs), \
      self.get_rand_value(self.distance_ranges_start, self.distance_ranges_probs)
      
  def pack_order(self, weight):
    packages = [self.get_package_weight(weight)]
    weight -= self.max_drone_load
    while weight > 0:
      packages.append(self.get_package_weight(weight))
      weight -= self.max_drone_load
    return packages, max([2, weight / 7.5])

  def get_package_weight(self, weight):
    return min([self.max_drone_load, weight])

  def get_free_drone_idx(self):
    return [drone_idx for drone_idx, params in self.drone_params.items() if params['is_dispatched'] is False]

  def get_returned_drone_idx(self):
    return [drone_idx for drone_idx, params in self.drone_params.items() if params['is_dispatched'] is None]

  def command_dispatch(self, drone_idx, order_placed_at, weight, distance, packaging_duration):
    self.drone_params[drone_idx]['order_id'] = uuid.uuid4()
    self.drone_params[drone_idx]['order_placed_at'] = order_placed_at
    self.drone_params[drone_idx]['weight'] = weight
    self.drone_params[drone_idx]['distance'] = distance
    self.drone_params[drone_idx]['packaging_duration'] = packaging_duration
    self.drone_params[drone_idx]['price'] = self.price_per_kg * weight + self.price_per_km * distance
    self.drone_params[drone_idx]['is_dispatched'] = True
    return Dispatch(self.drone_params, drone_idx, self.max_drone_speed, self.time_factor)

  def write_data(self, drone_idxs):
    log_data = '\n'
    for drone_idx in drone_idxs:
      params = ','.join([str(self.drone_params[drone_idx][param]) for param in self.param_names])
      log_data += f'{drone_idx},{params}\n'

    if len(log_data) > 1:
      with open(self.log_path, 'a') as f:
        f.write(log_data[:-1])

  def open_shop(self, time_now = datetime.now()):
    while True:
      order_placed_at, weight, distance = self.place_order(time_now)
      packages, packaging_duration = self.pack_order(weight)
      
      while len(self.get_free_drone_idx()) < len(packages):
        drone_idxs = self.get_returned_drone_idx()
        self.write_data(drone_idxs)
        [self.init_drone_params(drone_idx) for drone_idx in drone_idxs]
        if len(drone_idxs) == 0:
          sleep(0.1)

      dispatches = [
        self.command_dispatch(drone_idx, order_placed_at, weight, distance, packaging_duration)
        for drone_idx, weight in zip(self.get_free_drone_idx(), packages)
      ]
      [d.start() for d in dispatches]

      time_now += timedelta(minutes=packaging_duration)
      sleep(0.1)

if __name__ == '__main__':
  time_factor = 10
  drone_n = 10

  log_dir = os.path.join(os.getcwd(), 'supermarket_data')
  log_path = os.path.join(log_dir, 'data.csv')
  if os.path.isdir(log_dir) is False:
    os.mkdir(log_dir)

  super_market = SuperMarket(drone_n, time_factor, log_path)
  super_market.open_shop()
