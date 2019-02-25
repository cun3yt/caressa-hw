# Setting Up A New Device

1. balino-etcher >> burn aiyprojects-2018-08-03.img.xz file to sd
    1. cd /Users/cuneyt/Desktop/2_caressa/hardware/hw-package-modification/
1. Installation of speaker, ...
    1. echo "dtoverlay=googlevoicehat-soundcard" | sudo tee -a /boot/config.txt
1. check sound etc.
1. ifconfig to get IP
1. connect to raspbie remotely
    1. in local: cat ~/.ssh/raspberry_rsa.pub | pbcopy
    2. ssh pi@<IP>
    3. cat >> authorized_keys
    4. paste and exit (ctrl+d)
1. Add dataplicity connection
    1. curl https://www.dataplicity.com/muw03ius.py | sudo python
1. Run remote build for the device (IDE)
1. Install python dependencies:
    1. cd Work/
    2. pip3 install -r requirements/hardware.txt
1. sudo apt-get install vlc
1. Setup Config
    1. Create user in admin panel
    2. In DB, set user's password (currently copy/paste from another user!!)
    3. set senior_device.userId to the user
    4. cp config.template.json config.json
    5. edit config.json, setting api, user credentials, ...
1. Check if main.py works fine:
    1. make sure ENV like is set to 'prod' in .envrc:
        1. `ENV='prod'`
    1. `python3 ./main.py`
1. Setup caressa service:
    1. sudo ln -s /home/pi/Work/caressa.service /etc/systemd/system/caressa.service
    2. sudo systemctl restart caressa.service (OR sudo systemctl reload-or-restart caressa)
    3. systemctl status caressa
