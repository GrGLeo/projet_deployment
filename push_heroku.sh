#!/bin/bash

deploy_front() {
  local HEROKU_APP_NAME=$1

  echo "Deploying front-end to Heroku..."
  cd front

  heroku create $HEROKU_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_APP_NAME
  heroku container:release web -a $HEROKU_APP_NAME

  echo "Front-end deployment completed."
  cd ..
}

deploy_api() {
  local HEROKU_APP_NAME=$1

  echo "Deploying API to Heroku..."
  cd api

  heroku create $HEROKU_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_APP_NAME
  heroku container:release web -a $HEROKU_APP_NAME

  heroku_info=$(heroku apps:info -a $HEROKU_APP_NAME --json)
  APP_URI=$(echo $heroku_info | jq -r '.app.web_url')

  echo "Retrieved APP_URI: $API_URL"

  echo "API deployment completed."
  cd ..
}

deploy_mlflow() {
  local HEROKU_APP_NAME=$1

  echo "Deploying mlflow with PostgreSQL to Heroku..."
  cd mlflow

  heroku create $HEROKU_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_APP_NAME
  heroku container:release web -a $HEROKU_APP_NAME
  heroku addons:create heroku-postgresql:essential-0 -a $HEROKU_APP_NAME
  echo "Waiting 2 minutes for addons creation..."
  sleep 120

  DATABASE_URL=$(heroku config:get DATABASE_URL -a $HEROKU_APP_NAME)
  BACKEND_STORE_URI=${DATABASE_URL/postgres:\/\//postgresql:\/\/}

  echo "Retrieved BACKEND_STORE_URI: $BACKEND_STORE_URI"

  echo "mlflow deployment completed."
  cd ..
}

# Get app name for Heroku
read -p "Enter Heroku app name for front-end: " FRONT_APP_NAME
read -p "Enter Heroku app name for API: " API_APP_NAME
read -p "Enter Heroku app name for mlflow: " MLFLOW_APP_NAME

deploy_front $FRONT_APP_NAME

deploy_api $API_APP_NAME
echo "API_URL=$API_URL" > variables.txt

deploy_mlflow $MLFLOW_APP_NAME
echo "APP_URI=$APP_URI" >> variables.txt
echo "BACKEND_STORE_URI=$BACKEND_STORE_URI" >> variables.txt

echo "All deployments completed. Variables saved to variables.txt."
