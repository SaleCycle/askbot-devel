#!/bin/bash

set -e

docker build -t 423137131647.dkr.ecr.eu-west-1.amazonaws.com/askbot .
aws --profile prod ecr get-login | sh
docker push 423137131647.dkr.ecr.eu-west-1.amazonaws.com/askbot:latest

echo "Success!!"
echo "Now deploy this new docker image by doing an inoccuous edit to UserData in the askbot cloudformation template and executing the update script."
