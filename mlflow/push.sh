#!/bin/bash


get_heroku_app_name() {
  read -p "Enter Heroku app name: " HEROKU_APP_NAME
}

get_heroku_app_name

heroku create $HEROKU_APP_NAME
heroku container:login
heroku container:push web -a $HEROKU_APP_NAME
heroku container:release web -a $HEROKU_APP_NAME
heroku_info=$(heroku apps:info -a $HEROKU_APP_NAME --json)
APP_URI=$(echo $heroku_info | jq -r '.app.web_url')
echo "Retrieved web_url: $web_url"

heroku addons:create heroku-postgresql:essential-0 -a $HEROKU_APP_NAME

# Wait for 2 minutes to ensure database creation 
echo "Waiting for 2 minutes..."
sleep 120

BACKEND_STORE_URI=$(heroku config:get DATABASE_URL -a $HEROKU_APP_NAME)
BACKEND_STORE_URI=${DATABASE_URL/postgres:\/\//postgresql:\/\/}

echo "Script execution completed."
