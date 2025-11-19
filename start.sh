#!/bin/bash

python3 bot.py &

gunicorn fake:app