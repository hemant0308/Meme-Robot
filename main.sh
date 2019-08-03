#!/bin/bash
/home/hemant0328/practice/meme-robot/env/bin/python3 /home/hemant0328/practice/meme-robot/main.py
echo "$?"
echo `date`
#*/30 * * * * /home/hemant0328/practice/meme-robot/main.sh >> /home/hemant0328/practice/meme-robot/logs/`(date +"%H:%M,%d-%b-%Y")`.log