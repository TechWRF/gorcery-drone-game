#!/bin/bash

set -e
set -o pipefail

stream_data() {
  data_path=$(sed -rn '/^log_path = (.+)/p' $config_path | sed "s/log_path = //g")

  tail -f $data_path -n +2 | while read; do
    IFS=',' read -r -a row_arr <<< $REPLY
    for i in 1 2 7 8; do row_arr[i]="'${row_arr[i]}'"; done
    for i in {0..7}; do row_arr[i]="${row_arr[i]},"; done
    row=${row_arr[@]}
    
    psql -d $db_name -qc \
      "INSERT INTO sm_management.deliveries(
        drone_id, id, order_placed_at, weight, distance, packaging_duration, price, order_sent_at, order_completed_at
      ) VALUES ($row)
      ON CONFLICT DO NOTHING;"
  done
}

db_name='supermarket'
config_path='supermarket.ini'

stream_data > /dev/null 2>&1 &
STREAM_PROCESS_ID=$!
echo $STREAM_PROCESS_ID