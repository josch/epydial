#!/bin/bash

export DISPLAY=:0

xsetroot -cursor /usr/share/epydial/data/emptycursor /usr/share/epydial/data/emptycursor

cd /usr/share/epydial

while /bin/true; do
  ./epydial.py
  sleep 5
done
