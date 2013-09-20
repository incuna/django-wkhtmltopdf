#!/usr/bin/env bash

sudo apt-get install -y openssl build-essential xorg libssl-dev
wget http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.11.0_rc1-static-i386.tar.bz2
tar xvjf wkhtmltopdf-0.11.0_rc1-static-i386.tar.bz2
sudo chown root:root wkhtmltopdf-i386
sudo mv wkhtmltopdf-i386 /usr/bin/wkhtmltopdf
export WKHTMLTOPDF_CMD=/usr/bin/wkhtmltopdf
