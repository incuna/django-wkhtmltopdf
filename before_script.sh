#!/usr/bin/env bash

sudo apt-get install -y openssl build-essential xorg libssl-dev
wget http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.11.0_rc1-static-amd64.tar.bz2
tar xvjf wkhtmltopdf-0.11.0_rc1-static-amd64.tar.bz2
sudo chown root:root wkhtmltopdf-amd64
export WKHTMLTOPDF_CMD=`pwd`/wkhtmltopdf-amd64
$WKHTMLTOPDF_CMD --version
