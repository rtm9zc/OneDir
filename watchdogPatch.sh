#!/bin/bash
sudo chmod ugo+rwx /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.py
sudo rm /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.py
sudo cp patchCode/inotify.py /usr/local/lib/python2.7/dist-packages/watchdog/observers/inotify.py

echo Watchdog patched!