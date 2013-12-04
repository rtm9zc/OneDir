#!/bin/bash
sudo chmod ugo+rwx /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.py
sudo rm /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.py
sudo chmod ugo+rwx /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.pyc
sudo rm /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.pyc
sudo cp patchCode/ionotify.py /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.py
sudo cp patchCode/ionotify.pyc /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.pyc

echo Watchdog patched!