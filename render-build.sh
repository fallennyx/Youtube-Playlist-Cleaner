#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # Make sure we return to where we were
else
  echo "...Using Chrome from cache"
fi

# Install Python and dependencies
echo "...Installing Python and dependencies"
apt-get update && apt-get install -y python3 python3-pip
pip3 install -r requirements.txt

# Set up Flask environment
export FLASK_APP=app.py
export FLASK_ENV=production

# Run Flask migrations or other setup commands (if needed)
# flask db upgrade

# Start your Flask app
echo "...Starting Flask app"
flask run --host=0.0.0.0 --port=$PORT
