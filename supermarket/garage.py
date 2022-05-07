import random
import requests

class Repairs():
  def __init__(self, drone_idx, costs, probs):
    self.drone_idx = drone_idx

    self.names = ["inspection", "new_motor", "new_speed_controller", "new_gps_module", "new_battery", "new_obstacle_sensor", "new_height_sensor"]
    self.n_parts = [0, 4, 1, 1, 1, 2, 2]
    self.costs = costs
    self.probs = probs

    self.repairs = {name: 0 for name in self.names}

  def get_drone_price(self):
    return float(requests.post('http://localhost:3000/rpc/get_drone_price', data={"_id": self.drone_idx}).text)

  def diagnose(self):
    diagnose_result = random.choices(self.names, self.probs)[0]
    self.repairs[diagnose_result] += 1
    return diagnose_result

  def read_diagnose(self):
    drone_price = self.get_drone_price()
    if drone_price <= 5000:
      n_repairs = random.randint(1, 3)
    else:
      n_repairs = 1
      
    for i in range(n_repairs - 1):
      repair_name = random.choices(self.names[1:], self.probs[1:])[0]
      self.repairs[repair_name] += 1

    for name, n in zip(self.names[1:], self.n_parts[1:]):
      self.repairs[name] = min([n, self.repairs[name]])

  def inspect_drone(self):
    diagnose_result = self.diagnose()
    if diagnose_result == self.names[0]:
      return [diagnose_result]
    else:
      self.read_diagnose()

    repair_list = []
    for name, n in self.repairs.items():
      repair_list += [name] * n
    return repair_list

if __name__ == "__main__":
  drone_idx = 0
  repairs = Repairs(drone_idx)
  repair_list = repairs.inspect_drone()
  print(repair_list)