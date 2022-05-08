import random
from utils import call_server

class Repairs():
  def __init__(self, repair_names, n_parts, repair_costs, repair_probs):
    self.repair_names = repair_names
    self.repair_ids = list(range(1, len(repair_names) + 1))
    self.n_parts = n_parts
    self.repair_costs = repair_costs
    self.repair_probs = repair_probs

    self.repairs = {id: 0 for id in self.repair_ids}
  
  def diagnose(self):
    diagnose_result = random.choices(self.repair_ids, self.repair_probs)[0]
    self.repairs[diagnose_result] += 1
    return diagnose_result

  def read_diagnose(self, drone_price):
    if drone_price <= 5000:
      n_repairs = random.randint(1, 3)
    else:
      n_repairs = 1
      
    for i in range(n_repairs - 1):
      repair_name = random.choices(self.repair_ids[1:], self.repair_probs[1:])[0]
      self.repairs[repair_name] += 1

    for name, n in zip(self.repair_ids[1:], self.n_parts[1:]):
      self.repairs[name] = min([n, self.repairs[name]])

  def inspect_drone(self, drone_id):
    diagnose_result = self.diagnose()
    if diagnose_result - 1 == 0:
      return [diagnose_result], [self.repair_names[diagnose_result-1]]
    else:
      drone_price = float(call_server("get_drone_price", {"_id": drone_id}))
      self.read_diagnose(drone_price)

    repair_types = []
    for id, n in self.repairs.items():
      repair_types += [id] * n
    return repair_types, [self.repair_names[i-1] for i in repair_types]
  
  def repair_drone(self, drone_id, repair_types):
    call_server("repair_drone",
      {"_drone_id": drone_id, 
      "_cost": sum([self.repair_costs[i-1] for i in repair_types]),
      "_repair_types": "{%s}" % ", ".join([str(id) for id in repair_types])}
    )

if __name__ == "__main__":
  repair_names = ["inspection", "new_motor", "new_speed_controller", "new_gps_module", "new_battery", "new_obstacle_sensor", "new_height_sensor"]
  n_parts = [0, 4, 1, 1, 1, 2, 2]
  repair_costs = [75, 50, 100, 150, 200, 125, 125]
  repair_probs = [45, 15, 10, 10, 10, 5, 5]

  drone_id = 1
  repairs = Repairs(repair_names, n_parts, repair_costs, repair_probs)
  repair_types, repair_list = repairs.inspect_drone(drone_id)
  print(repair_types, repair_list)
  repairs.repair_drone(drone_id, repair_types)