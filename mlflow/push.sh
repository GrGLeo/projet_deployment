#!/bin/bash

get_docker_tag() {
  read -p "Enter Docker tag: " DOCKER_TAG
}

get_heroku_app_name() {
  read -p "Enter Heroku app name: " HEROKU_APP_NAME
}

confirm_push_to_heroku() {
  while true; do
    read -p "Do you want to push the container to Heroku? (yes/no): " yn
    case $yn in
        [Yy]* ) PUSH_TO_HEROKU=true; break;;
        [Nn]* ) PUSH_TO_HEROKU=false; break;;
        * ) echo "Please answer yes or no.";;
    esac
  done
}

get_docker_tag

docker build . -t $DOCKER_TAG

confirm_push_to_heroku

if $PUSH_TO_HEROKU; then
  get_heroku_app_name

  heroku create $HEROKU_APP_NAME
  heroku container:login
  heroku container:push web -a $HEROKU_APP_NAME
  heroku container:release web -a $HEROKU_APP_NAME
  heroku open -a $HEROKU_APP_NAME
  heroku apps:info -a $HEROKU_APP_NAME --json | jq -r '.app.web_url'
  echo "Copy the above url to the .env APP_URI"
  heroku config -a my-awesome-app
fi

echo "Script execution completed."
