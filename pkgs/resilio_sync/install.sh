#!/bin/bash

# echo "deb http://linux-packages.resilio.com/resilio-sync/deb resilio-sync non-free" | sudo tee /etc/apt/sources.list.d/resilio-sync.list
# wget -qO- https://linux-packages.resilio.com/resilio-sync/key.asc | sudo tee /etc/apt/trusted.gpg.d/resilio-sync.asc > /dev/null 2>&1
sudo apt update
sudo apt install resilio-sync


#!/bin/bash

# Enable automatic startup of Sync service under rslsync user
sudo systemctl enable resilio-sync

# Add rslsync user to the group of the current user
sudo usermod -aG $(groups $USER | cut -d' ' -f3) rslsync

# Add current user to the rslsync group
sudo usermod -aG rslsync $USER

# Set read-write permissions for the group on the synced folder
sudo chmod g+rw /path/to/synced_folder



sudo systemctl enable resilio-sync

# Enable sync service automatic startup as user rslsync
sudo systemctl enable resilio-sync

# Enable sync service as current user
sed -i 's/WantedBy=multi-user.target/WantedBy=default.target/g' /usr/lib/systemd/user/resilio-sync.service

# Reload systemd user configuration
systemctl --user daemon-reload

# Enable the service for the current user
systemctl --user enable resilio-sync

echo "Resilio Sync service has been configured and enabled."
echo "You can start, stop, enable, disable, or check status using systemctl --user command."
