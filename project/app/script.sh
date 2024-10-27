#!/bin/bash

pylint src --recursive y -E
if [ $? -gt 0 ]
then
  exit 1
fi

cd src || { echo "Directory 'src' not found."; exit 1; }

gunicorn --bind 0.0.0.0:8008 --timeout=10800 app:main
