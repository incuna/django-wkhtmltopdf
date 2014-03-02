#!/usr/bin/env bash

echo '## Installing dependencies'
sudo apt-get install -y openssl build-essential xorg libssl-dev
echo '## Downloading wkhtmltox'
wget http://downloads.sourceforge.net/project/wkhtmltopdf/0.12.0/wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
echo '## Extracting wkhtmltox'
tar xvJf wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
#sudo chown root:root wkhtmltox
current_folder=`pwd`
wkhtmltopdf_binary=$current_folder/wkhtmltox/bin/wkhtmltopdf
echo $wkhtmltopdf_binary
#sudo mv wkhtmltox /usr/bin/wkhtmltopdf
echo "## Exporting WKHTMLTOPDF_CMD system enviroment variable"
echo "WKHTMLTOPDF_CMD=$wkhtmltopdf_binary"
export WKHTMLTOPDF_CMD=$wkhtmltopdf_binary

