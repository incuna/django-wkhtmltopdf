#!/usr/bin/env bash

echo '## Installing dependencies'
sudo apt-get install -y openssl build-essential xorg libssl-dev
echo '## Downloading wkhtmltox'
wget http://downloads.sourceforge.net/project/wkhtmltopdf/0.12.0/wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
echo '## Extracting wkhtmltox'
tar xvJf wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
#sudo chown root:root wkhtmltox
current_folder=`pwd`
wkhtmltox_folder=$current_folder/wkhtmltox
wkhtmltox_exec=$wkhtmltox_folder/bin/wkhtmltopdf
echo $wkhtmltox_folder
#sudo mv wkhtmltox /usr/bin/wkhtmltopdf
export WKHTMLTOPDF_CMD=$wkhtmltox_exec
