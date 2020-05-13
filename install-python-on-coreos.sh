#!/bin/bash
# ctaglia

# Copy this file via scp for installing python in destination machine. Exec as root
# create directory for python install
sudo mkdir -p /opt/bin
sudo chown -hR core:core /opt
cd /opt

# check for newer versions at http://downloads.activestate.com/ActivePython/releases/
wget http://downloads.activestate.com/ActivePython/releases/3.6.0.3600/ActivePython-3.6.0.3600-linux-x86_64-glibc-2.3.6-401834.tar.gz
tar -xzvf ActivePython-3.6.0.3600-linux-x86_64-glibc-2.3.6-401834.tar.gz
mv ActivePython-3.6.0.3600-linux-x86_64-glibc-2.3.6-401834 apy && cd apy && ./install.sh -I /opt/python/

# create symlinks 
ln -s /opt/python/bin/easy_install-3.6 /opt/bin/easy_install
ln -s /opt/python/bin/pip3.6 /opt/bin/pip
ln -s /opt/python/bin/python3.6 /opt/bin/python
ln -s /opt/python/bin/virtualenv /opt/bin/virtualenv

# Add bashrc as a file not symlink. And add /opt/python
cd ~/
rm .bashrc
cp /usr/share/skel/.bashrc .
echo 'PATH=/opt/python/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
