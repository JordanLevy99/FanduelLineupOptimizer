#!/bin/bash
# need to find a way to implement relative pathing based on current working directory in relation to the project root
#  , with the ultimate goal of getting this bash script to work from my notebooks directory (optional)
# TODO: Change chromedriver name based on OS environment variable specified in the config

cd src
pwd
rm -f chromedriver
wget https://chromedriver.storage.googleapis.com/$1/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
rm chromedriver_mac64.zip
