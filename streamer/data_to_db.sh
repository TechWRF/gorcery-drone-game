#!/bin/bash

set -e
set -o pipefail

setup_db() {
  psql -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$db_name';" | grep -q 1 || psql -d postgres -c "CREATE DATABASE $db_name;"
  psql -d $db_name -c \
    "CREATE TABLE IF NOT EXISTS deliveries (
      drone_idx INT,
      order_id TEXT,
      order_placed_at TIMESTAMP,
      weight FLOAT,
      distance FLOAT,
      packaging_duration FLOAT,
      price FLOAT,
      order_sent_at TIMESTAMP,
      order_completed_at TIMESTAMP,
      UNIQUE(order_id)
    );"
}

stream_data() {
  data_path=$(sed -rn '/^log_path = (.+)/p' $config_path | sed "s/log_path = //g")

  tail -f $data_path -n +2 | while read; do
    IFS=',' read -r -a row_arr <<< $REPLY
    for i in 1 2 7 8; do row_arr[i]="'${row_arr[i]}'"; done
    for i in {0..7}; do row_arr[i]="${row_arr[i]},"; done
    row=${row_arr[@]}
    
    echo $row
    psql -d $db_name -qc \
      "INSERT INTO deliveries(
        drone_idx, order_id, order_placed_at, weight, distance, packaging_duration, price, order_sent_at, order_completed_at
      ) VALUES ($row)
      ON CONFLICT DO NOTHING;"
  done
}

db_name='supermarket'
config_path='supermarket.ini'

setup_db
stream_data