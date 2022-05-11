from threading import Thread
from time import sleep
from datetime import timedelta

class Dispatch(Thread):
  def __init__(self, drone_params, drone_idx, max_drone_speed, time_factor):
    Thread.__init__(self)
    self.drone_idx = drone_idx
    self.drone_params = drone_params

    self.order_placed_at = self.drone_params[drone_idx]['order_placed_at']
    self.weight = self.drone_params[drone_idx]['weight']
    self.distance = self.drone_params[drone_idx]['distance']
    self.packaging_duration = self.drone_params[drone_idx]['packaging_duration']

    self.max_drone_speed = max_drone_speed
    self.time_factor = time_factor

  def run(self):
    return self.dispatch_drone()

  @staticmethod
  def send_order(time_now):
    return time_now

  def wait_for_drone_return(self, order_sent_at):
    drone_speed = self.max_drone_speed - 1.5 * self.weight
    delivery_time = self.distance / drone_speed
    return_time = self.distance / self.max_drone_speed
    wait_time = delivery_time + return_time
    sleep(wait_time * 60 / self.time_factor)
    return order_sent_at + timedelta(hours=wait_time)

  def dispatch_drone(self):
    sleep(self.packaging_duration * 60 / self.time_factor)
    time_now = self.order_placed_at + timedelta(minutes=self.packaging_duration)

    order_sent_at = self.send_order(time_now)
    order_completed_at = self.wait_for_drone_return(order_sent_at)

    self.drone_params[self.drone_idx]['order_sent_at'] = order_sent_at
    self.drone_params[self.drone_idx]['order_completed_at'] = order_completed_at
    self.drone_params[self.drone_idx]['is_dispatched'] = None