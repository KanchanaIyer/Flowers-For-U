#!/bin/bash

# Exit on any error
set -e

# check if user is root (because root can always change permissions)
if [ "$(id -u)" != "0" ]; then
    echo "You must be root to run this script"
    exit 1
fi

# check if in the correct directory (FLOWERS4U/
if [ ! -d "Flowers4U" ]; then
    echo "Not in the correct directory"
    echo "Please run this script from the Flowers4U/ directory"
    exit 1
fi

# check if a config path was passed
if [ -z "$1" ]; then
    echo "No config path passed"
    echo "Using default config path: /var/www/Flowers4U/config/config.ini"
    CONFIG_PATH="/var/www/Flowers4U/config/config.ini"
else
    CONFIG_PATH=$1
fi

# pull latest code if merge conflict occurs, abort
echo "Pulling latest code"
git pull origin master || exit 1


# fix permissions
echo "Fixing permissions"
find . -type d -exec chmod 775 {} \;
find . -type f -exec chmod 664 {} \;

# fix ownership and group
echo "Fixing ownership and group"
chown -R www-data:www-data .

# install dependencies
pip install -r requirements.txt

# modify .env file
echo "FLOWERS_CONFIG_PATH=$CONFIG_PATH" > .env

# Done
echo "Completed deployment"