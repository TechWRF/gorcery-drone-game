DROP FUNCTION IF EXISTS sm_management.get_stats_by_date;
CREATE FUNCTION sm_management.get_stats_by_date(_start TIMESTAMP, _end TIMESTAMP)
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN json_build_object(
    'id', json_agg(id),
    'order_placed_at', json_agg(order_placed_at),
    'order_sent_at', json_agg(order_sent_at),
    'order_completed_at', json_agg(order_completed_at),
    'weight', json_agg(weight),
    'distance', json_agg(distance),
    'price', json_agg(price)
  )
  FROM sm_management.deliveries 
  WHERE order_placed_at >= _start AND order_placed_at < _end;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_stats_by_drone;
CREATE FUNCTION sm_management.get_stats_by_drone(_id INT)
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN json_build_object(
    'order_placed_at', json_agg(order_placed_at),
    'order_sent_at', json_agg(order_sent_at),
    'order_completed_at', json_agg(order_completed_at),
    'weight', json_agg(weight),
    'distance', json_agg(distance),
    'price', json_agg(price)
  )
  FROM sm_management.deliveries 
  WHERE drone_id = _id;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_active_drones;
CREATE FUNCTION sm_management.get_active_drones()
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN CASE WHEN res IS NULL THEN '{}'::JSON ELSE res END WHEN FROM (
    SELECT json_agg(res)::JSON AS res FROM(
      SELECT id, name, max_load, max_speed, started_serving_at
      FROM sm_management.drones
      WHERE is_active = TRUE
    ) res
  )js;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_inactive_drones;
CREATE FUNCTION sm_management.get_inactive_drones()
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN CASE WHEN res IS NULL THEN '{}'::JSON ELSE res END WHEN FROM (
    SELECT json_agg(res)::JSON AS res FROM(
      SELECT id, name, max_load, max_speed, started_serving_at, stopped_serving_at
      FROM sm_management.drones
      WHERE is_active = FALSE
    ) res
  ) js;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_new_drone_id();
CREATE FUNCTION sm_management.get_new_drone_id()
RETURNS INT
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN id + 1 FROM sm_management.drones ORDER BY id DESC LIMIT 1;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.add_drone;
CREATE FUNCTION sm_management.add_drone(_id INT, _name TEXT, _max_load FLOAT, _max_speed FLOAT, _price FLOAT, _started_serving_at TIMESTAMP, _stopped_serving_at TIMESTAMP = NULL, _is_active BOOLEAN = TRUE)
RETURNS VOID
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  INSERT INTO sm_management.drones(id, name, max_load, max_speed, started_serving_at, stopped_serving_at, is_active, price)
  VALUES (_id, _name, _max_load, _max_speed, _started_serving_at, _stopped_serving_at, _is_active, _price)
  ON CONFLICT DO NOTHING;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.add_repair_type;
CREATE FUNCTION sm_management.add_repair_type(_name TEXT, _cost FLOAT)
RETURNS VOID
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  INSERT INTO sm_management.repair_types(name, cost)
  VALUES (_name, _cost)
  ON CONFLICT DO NOTHING;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.remove_drone;
CREATE FUNCTION sm_management.remove_drone(_id INT, _stopped_serving_at TIMESTAMP)
RETURNS VOID
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RAISE EXCEPTION 'Can''t remove last drone';
  IF (SELECT COUNT(id) FROM sm_management.drones WHERE is_active = TRUE) > 1 THEN
    UPDATE sm_management.drones SET is_active = FALSE, stopped_serving_at = _stopped_serving_at WHERE id = _id;
  ELSE
    RAISE EXCEPTION 'Can''t remove last drone';
  END IF;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_drone;
CREATE FUNCTION sm_management.get_drone(_id INT)
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN json_build_object(
    'name', name,
    'max_load', max_load,
    'max_speed', max_speed,
    'started_serving_at', started_serving_at,
    'stopped_serving_at', stopped_serving_at,
    'is_active', is_active,
    'price', price
  )
  FROM sm_management.drones 
  WHERE id = _id;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_drone_price;
CREATE FUNCTION sm_management.get_drone_price(_id INT)
RETURNS FLOAT
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN price FROM sm_management.drones WHERE id = _id;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.repair_drone;
CREATE FUNCTION sm_management.repair_drone(_drone_id INT, _cost FLOAT, _repair_types SMALLINT[])
RETURNS VOID
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  INSERT INTO sm_management.repairs(drone_id, cost, distance)
  VALUES (
    _drone_id,
    _cost,
    (SELECT SUM(distance) FROM sm_management.deliveries WHERE drone_id = _drone_id)
  )
  ON CONFLICT DO NOTHING;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_repairs_by_drone;
CREATE FUNCTION sm_management.get_repairs_by_drone(_id INT)
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN json_build_object(
    'n_repairs', COUNT(*),
    'total_cost', SUM(cost),
    'km_last_repair', MAX(distance),
    'income_by_drone', (SELECT SUM(price) FROM sm_management.deliveries WHERE drone_id = _id)
  )
  FROM sm_management.repairs
  WHERE drone_id = _id;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.get_credits;
CREATE FUNCTION sm_management.get_credits()
RETURNS BIGINT
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  -- TODO: add get_credits()
END
$$
;