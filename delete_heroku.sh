# Script to delete all three Heroku app

delete_app() {
    local HEROKU_APP_NAME=$1

    heroku apps:destroy --app $HEROKU_APP_NAME --confirm $HEROKU_APP_NAME
}

read -p "Enter Heroku app name for front-end: " FRONT_APP_NAME
read -p "Enter Heroku app name for API: " API_APP_NAME
read -p "Enter Heroku app name for mlflow: " MLFLOW_APP_NAME

delete_app $FRONT_APP_NAME
delete_app $API_APP_NAME
delete_app $MLFLOW_APP_NAME