# Setting Up A New Device for Production

1. Install BalenaEtcher to burn a Raspberry PI image.
1. Download aiyprojects-2018-08-03.tar extract it to `aiyprojects-2018-08-03.img.xz`.
1. Start BalenaEtcher, burn `aiyprojects-2018-08-03.img.xz` file to the SD card:
    1. Example location: /Users/cuneyt/Desktop/2_caressa/hardware/hw-package-modification/
1. To install the speaker driver run the command below:
    1. echo "dtoverlay=googlevoicehat-soundcard" | sudo tee -a /boot/config.txt
1. check sound, microphone, connection etc. (there are files on the desktop)
1. ifconfig to get IP
1. connect to raspbie remotely
    1. in local: cat ~/.ssh/raspberry_rsa.pub | pbcopy
    2. ssh pi@<IP>
    3. mkdir ~/.ssh/
    3. cat >> ~/.ssh/authorized_keys
    4. paste and exit (ctrl+d)
1. Add dataplicity connection
    1. curl https://www.dataplicity.com/hdg7m8mc.py | sudo python
    1. go to dataplicity dashboard give a name to the new device
    1. install Porthole from dataplicity
    1. add connecting in Porthole new device (port: 22) to one local port number(ex: 9001)
    1. keep Porthole open
1. Run remote build for the device (IDE): 
    1. remote-build.sh
1. Install python dependencies:
    1. cd Work/
    2. pip3 install -r requirements/hardware.txt
1. sudo apt-get install vlc

1. Setup Config
    1. Create user in admin panel
    1. In DB, set user's password (currently copy/paste from another user!!)
    1. set senior_device.userId to the user
    1. cp config.template.json config.prod.json (this is for production, if you want development: cp config.template.json config.dev.json)
    1. edit config.prod.json, setting api, user credentials, ...
1. Check if main.py works fine:
    1. make sure ENV like is set to 'prod' in .envrc:
        1. `ENV='prod'`
    1. `source ~/Work/.envrc`
    1. `python3 ~/Work/main.py`
1. Setup caressa service:
    1. sudo ln -s /home/pi/Work/caressa.service /etc/systemd/system/caressa.service
    1. sudo systemctl enable caressa.service (OR sudo systemctl reload-or-restart caressa)
    1. sudo systemctl restart caressa.service (OR sudo systemctl reload-or-restart caressa)
    1. systemctl status caressa
   

## Troubleshooting

* Warning **: Error retrieving accessibility bus address:
    sudo apt-get install at-spi2-core
