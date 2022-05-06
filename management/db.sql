DROP SCHEMA IF EXISTS sm_management CASCADE;
CREATE SCHEMA sm_management;

CREATE PROCEDURE sm_management.create_api_user()
LANGUAGE 'plpgsql'
AS $$
BEGIN
  --recreate role for reading data
  IF (SELECT 1 FROM pg_roles WHERE rolname='sm_manager') IS NOT NULL THEN
    DROP OWNED BY sm_manager CASCADE;
  END IF;
  DROP ROLE IF EXISTS sm_manager;
  CREATE ROLE sm_manager;

  GRANT USAGE ON SCHEMA sm_management TO sm_manager;
  GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA sm_management TO sm_manager;

  --recreate admin
  IF (SELECT 1 FROM pg_roles WHERE rolname='sm_admin') IS NOT NULL THEN
    DROP OWNED BY sm_admin CASCADE;
  END IF;
  DROP ROLE IF EXISTS sm_admin;
  CREATE ROLE sm_admin WITH NOINHERIT LOGIN PASSWORD 'admin';

  -- add ability for admin to switch to sm_manager role
  GRANT sm_manager TO sm_admin;
END
$$
;

CREATE TABLE sm_management.drones (
  id INT,
  name TEXT,
  max_load FLOAT,
  max_speed FLOAT,
  started_serving_at TIMESTAMP,
  stopped_serving_at TIMESTAMP,
  is_active BOOLEAN,
  UNIQUE(id)
);

CREATE TABLE sm_management.deliveries (
  drone_id INT,
  id TEXT,
  order_placed_at TIMESTAMP,
  weight FLOAT,
  distance FLOAT,
  packaging_duration FLOAT,
  price FLOAT,
  order_sent_at TIMESTAMP,
  order_completed_at TIMESTAMP,
  UNIQUE(id)
);

CREATE TABLE sm_management.repair_types (
  id INT,
  name TEXT,
  cost FLOAT,
  UNIQUE(id)
);

CREATE TABLE sm_management.repairs (
  id INT,
  drone_id INT,
  distance FLOAT,
  UNIQUE(id)
);