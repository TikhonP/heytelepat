#!/bin/bash

cd .. # Exit to root directory `heytelepat-speaker`

# Parse arguments
SKIP_DEPENDENCIES=0
while getopts "h?s" opt; do
  case "$opt" in
  h | \?)
    echo "usage: ./install.sh [-h] [-s]"
    exit 0
    ;;
  s)
    SKIP_DEPENDENCIES=1
    ;;
  esac
done

shift $((OPTIND - 1))

[ "${1:-}" = "--" ] && shift

if ((SKIP_DEPENDENCIES == 1)); then
  echo "Skipping apt-get dependencies installation..."
else
  # Installing all apt-get dependencies -------------------------------------------------------

  echo "Installing all apt-get dependencies..."
  {
    sudo apt update
    sudo apt install portaudio19-dev libatlas-base-dev build-essential libssl-dev libffi-dev -y
    sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 -y

    sudo apt install python3-dev python3-pip python3-venv -y
  } &>/dev/null

  # Installing voice card driver ---------------------------

  echo "Installing voice card driver..."
  {
    git clone https://github.com/respeaker/seeed-voicecard.git
    cd seeed-voicecard || exit
    sudo ./install.sh
    cd ..
    rm -rf seeed-voicecard
  } &>/dev/null

fi
exit

# Creating python venv and installing pip dependencies

python3 -m venv env
. env/bin/activate

pip install -U pip
pip install -r installation/requirements.txt

# Creating systemd services --------

cd installation || exit
mkdir services
python render_services.py "$USER" services || exit
sudo mv -v services/* /etc/systemd/system/
sudo systemctl daemon-reload || exit
rm -rf services
cd ..

# Updating speaker to last version

cd update || exit
python update.py --update_only || exit
cd ..

# Granting SUDO to python executable scripts

# Scripts: src/network/add_network.sh, src/network/connect_network.sh,
# updater/start_speaker_service.sh, updater/stop_speaker_service.sh,

sudo chown root:root src/network/add_network.sh src/network/connect_network.sh \
  updater/start_speaker_service.sh updater/stop_speaker_service.sh
sudo chmod 700 src/network/add_network.sh src/network/connect_network.sh \
  updater/start_speaker_service.sh updater/stop_speaker_service.sh

# Enabling system services ---------

sudo systemctl enable speaker
sudo systemctl enable speaker_updater

sudo systemctl start speaker_updater

# shellcheck disable=SC1073
echo "Done! Please reboot system. To start speaker run \`sudo systemctl start speaker\`"
