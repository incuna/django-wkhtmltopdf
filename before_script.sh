#!/usr/bin/env bash
WKHTMLTOX_FOLDER="`pwd`/wkhtmltox_folder"

echo '## Installing dependencies'
sudo apt-get install -y openssl build-essential xorg libssl-dev
echo '## Downloading wkhtmltopdf 0.12.0'
wget http://downloads.sourceforge.net/project/wkhtmltopdf/0.12.0/wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
mkdir -p $WKHTMLTOX_FOLDER
echo "## Extracting wkhtmltox into $WKHTMLTOX_FOLDER"
tar xvJf wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz -C $WKHTMLTOX_FOLDER
export WKHTMLTOPDF_CMD=$WKHTMLTOX_FOLDER/wkhtmltox/bin/wkhtmltopdf
echo $WKHTMLTOPDF_CMD --version
