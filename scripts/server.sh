#!/bin/bash

set -e
set -o pipefail

create_api() {
  psql -a -d $db_name -f $postgrest_dir/api.sql -v "ON_ERROR_STOP=1"
  psql -d $db_name -c "CALL sm_management.create_api_user();"
}

start_server() {
  postgrest postgrest.conf
}

postgrest_dir=$PWD/management
db_name='supermarket'

create_api
start_server > /dev/null 2>&1 &
SERVER_PROCESS_ID=$!
echo $SERVER_PROCESS_ID