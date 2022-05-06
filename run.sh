#!/bin/bash

set -e
set -o pipefail

create_db() {
  psql -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$db_name';" | grep -q 1 || psql -d postgres -c "CREATE DATABASE $db_name;"
  psql -a -d $db_name -f $postgrest_dir/db.sql -v "ON_ERROR_STOP=1"
}

create_api() {
  psql -a -d $db_name -f $postgrest_dir/api.sql -v "ON_ERROR_STOP=1"
  psql -d $db_name -c "CALL sm_management.create_api_user();"
}

start_webserver() {
  postgrest postgrest.conf
}

install_postgrest() {
  sudo apt-get update -y
  sudo apt-get install wget -y

  postgrest=postgrest-v$postgrest_v-linux-static-x64.tar.xz
  wget https://github.com/PostgREST/postgrest/releases/download/v$postgrest_v/$postgrest

  sudo tar xvf $postgrest -C '/usr/local/bin'
  rm $postgrest
}

postgrest_v=9.0.0
postgrest_dir=$PWD/management
db_name='supermarket'

if [ "$1" = "start" ]; then
  start_webserver
elif [ "$1" = "re-api-start" ]; then
  create_api
  start_webserver
elif [ "$1" = "re-db-start" ]; then
  create_db
  create_api
  start_webserver
elif [ "$1" =  "install-postgrest" ]; then
  install_postgrest
else
  echo "job not found"
  exit 1
fi;