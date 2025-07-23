#!/bin/bash

# Aumentar limite de inotify watches
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Configurar permissões
chmod +x setup.sh 