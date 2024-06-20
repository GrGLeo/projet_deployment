#!/bin/bash
source .env

# Function to check if a variable is set
check_env_var() {
  local var_name=$1
  if [ -z "${!var_name}" ]; then
    echo "Error: $var_name is not set in the environment."
    exit 1
  fi
}

# Check required environment variables
check_env_var "ARTIFACT_STORE_URI"
check_env_var "AWS_ACCESS_ID"
check_env_var "AWS_ACCESS_KEY"

deploy_front() {
  local HEROKU_FRONT_APP_NAME=$1

  echo "Deploying front-end to Heroku..."
  cd front

  heroku create $HEROKU_FRONT_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_FRONT_APP_NAME
  heroku container:release web -a $HEROKU_FRONT_APP_NAME

  echo "Front-end deployment completed."
  cd ..
}

deploy_api() {
  local HEROKU_API_APP_NAME=$1

  echo "Deploying API to Heroku..."
  cd api

  heroku create $HEROKU_API_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_API_APP_NAME
  heroku container:release web -a $HEROKU_API_APP_NAME

  heroku_info=$(heroku apps:info -a $HEROKU_API_APP_NAME --json)
  API_URL=$(echo $heroku_info | jq -r '.app.web_url')

  echo "Retrieved API_URL: $API_URL"

  echo "API deployment completed."
  cd ..
}

deploy_mlflow() {
  local HEROKU_MLFLOW_APP_NAME=$1

  echo "Deploying mlflow with PostgreSQL to Heroku..."
  cd mlflow

  heroku create $HEROKU_MLFLOW_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_MLFLOW_APP_NAME
  heroku container:release web -a $HEROKU_MLFLOW_APP_NAME
  heroku_info=$(heroku apps:info -a $HEROKU_MLFLOW_APP_NAME --json)
  MLFLOW_APP_URI=$(echo $heroku_info | jq -r '.app.web_url')
  heroku addons:create heroku-postgresql:essential-0 -a $HEROKU_MLFLOW_APP_NAME
  echo "Waiting 2 minutes for addons creation..."
  sleep 120

  DATABASE_URL=$(heroku config:get DATABASE_URL -a $HEROKU_MLFLOW_APP_NAME)
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
deploy_mlflow $MLFLOW_APP_NAME

heroku config:set ARTIFACT_STORE_URI=$ARTIFACT_STORE_URI AWS_ACCESS_ID=$AWS_ACCESS_ID AWS_ACCESS_KEY=$AWS_ACCESS_KEY BACKEND_STORE_URI=$BACKEND_STORE_URI APP_URI=$MLFLOW_APP_URI -a $API_APP_NAME
heroku config:set API_URL=$API_URL -a $FRONT_APP_NAME

echo "All deployments completed"