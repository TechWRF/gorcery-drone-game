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
  WHERE id = _id;
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
  RETURN json_agg(res)::JSON FROM(
    SELECT id, name, max_load, max_speed, started_serving_at
    FROM sm_management.drones
    WHERE is_active = TRUE
  ) res;
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
  RETURN json_agg(res)::JSON FROM(
    SELECT id, name, max_load, max_speed, started_serving_at, stopped_serving_at
    FROM sm_management.drones
    WHERE is_active = FALSE
  ) res;
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
CREATE FUNCTION sm_management.add_drone(_id INT, _name TEXT, _max_load FLOAT, _max_speed FLOAT, _started_serving_at TIMESTAMP, _stopped_serving_at TIMESTAMP = NULL, _is_active BOOLEAN = TRUE)
RETURNS VOID
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  INSERT INTO sm_management.drones(id, name, max_load, max_speed, started_serving_at, stopped_serving_at, is_active) VALUES (
    _id, _name, _max_load, _max_speed, _started_serving_at, _stopped_serving_at, _is_active
  );
END
$$
;

DROP FUNCTION IF EXISTS sm_management.remove_drone;
CREATE FUNCTION sm_management.remove_drone(_id INT)
RETURNS VOID
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  UPDATE sm_management.drones SET is_active = FALSE WHERE id = _id;
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
    'id', id,
    'name', name,
    'max_load', max_load,
    'max_speed', max_speed,
    'started_serving_at', started_serving_at
  )
  FROM sm_management.drones 
  WHERE id = _id;
END
$$
;

DROP FUNCTION IF EXISTS sm_management.repair_drone;
CREATE FUNCTION sm_management.repair_drone(_id INT)
RETURNS JSON
LANGUAGE 'plpgsql'
AS
$$
BEGIN
  RETURN '{}';
END
$$
;