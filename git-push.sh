#!/bin/bash
git add .
read -p "Enter commmit message: " message
git commit -m "$message"
git push
