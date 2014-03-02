#!/usr/bin/env bash

sudo apt-get install -y openssl build-essential xorg libssl-dev
wget http://downloads.sourceforge.net/project/wkhtmltopdf/0.12.0/wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
tar xvJf wkhtmltox-linux-amd64_0.12.0-03c001d.tar.xz
sudo chown root:root wkhtmltox
sudo mv wkhtmltox /usr/bin/wkhtmltopdf
export WKHTMLTOPDF_CMD=/usr/bin/wkhtmltopdf
