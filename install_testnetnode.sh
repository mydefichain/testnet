#Variablen
USERNAME=$1
SERVERNAME=$2
DOMAIN=$3
VERSION=$4

#Pruefen ob debian 11 buster installiert:
lsb_release -a
echo "Check OS...Debian 10/11 needed"
sleep 3
#Update...
apt update && apt full-upgrade

#Set Timezone
ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

#Set NTP-Server
cat >> /etc/systemd/timesyncd.conf << EOL
NTP=ptbtime1.ptb.de
NTP=ptbtime2.ptb.de
NTP=ptbtime3.ptb.de
EOL

#Packages installieren:
echo "Install Packages..."
apt install -qqy sudo nano mc ufw curl ftp htop python3 python3-pip pwgen apache2 php libapache2-mod-php

#Hostname
hostnamectl set-hostname ${SERVERNAME}.${DOMAIN}

rm /etc/hosts
touch /etc/hosts

cat >> /etc/hosts << EOL
127.0.0.1 localhost
# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

$(hostname -i) ${SERVERNAME}.${DOMAIN} ${SERVERNAME}
EOL

#Pruefen auf updates:
echo "Updatecheck..."
apt update && apt full-upgrade

sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow ssh/tcp
sudo ufw limit ssh/tcp
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
sudo ufw allow 18555/tcp
sudo ufw allow 6556/tcp
sudo ufw allow 18333/tcp
sudo ufw logging on
sudo ufw -f enable
sudo ufw status

sudo systemctl enable ufw

#Apache

mkdir -p /var/www/${SERVERNAME}.${DOMAIN}
chown -R www-data:www-data /var/www/${SERVERNAME}.${DOMAIN}
chmod -R 775 /var/www/${SERVERNAME}.${DOMAIN}

mkdir -p /var/www/${SERVERNAME}.${DOMAIN}/api/
chown -R www-data:www-data /var/www/${SERVERNAME}.${DOMAIN}/api/
chmod -R 775 /var/www/${SERVERNAME}.${DOMAIN}/api/

touch /etc/apache2/sites-available/${SERVERNAME}.${DOMAIN}.conf

cat >> /etc/apache2/sites-available/${SERVERNAME}.${DOMAIN}.conf << EOL
<VirtualHost *:80>
  ServerAdmin info@${DOMAIN}
  ServerName ${SERVERNAME}.${DOMAIN}
  ServerAlias ${SERVERNAME}.${DOMAIN}
  DocumentRoot /var/www/${SERVERNAME}.${DOMAIN}
  ErrorLog ${APACHE_LOG_DIR}/error.log
  CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOL


a2ensite ${SERVERNAME}.${DOMAIN}
a2dissite 000-default.conf
systemctl restart apache2

touch /etc/apache2/conf-available/servername.conf

cat >> /etc/apache2/conf-available/servername.conf << EOL
ServerName ${SERVERNAME}.${DOMAIN}
EOL

a2enconf servername

apache2ctl configtest
sleep 10

#Secure Apache

touch /etc/apache2/conf-enabled/security.conf

cat >> /etc/apache2/conf-enabled/security.conf << EOL
ServerTokens Prod
ServerSignature Off
TraceEnable Off
EOL

systemctl restart apache2.service

#SECURE THE HOST:
echo "Create User, lock rootshell..."

useradd -m -s /bin/bash -G adm,systemd-journal,sudo,www-data ${USERNAME} && passwd ${USERNAME}

sudo sed -i '/PermitRootLogin/d' /etc/ssh/sshd_config && \
echo "PermitRootLogin no" | sudo tee -a  /etc/ssh/sshd_config

touch "/home/"${USERNAME}"/install_user.sh"
install_user="/home/"${USERNAME}"/install_user.sh"
chmod 744 $install_user

#Latest Snapshot
LATEST=$(curl https://testnet.snapshot-de.mydefichain.com/latest.txt)

cat >> $install_user << EOL
cd ~/

wget https://github.com/DeFiCh/ain/releases/download/v${VERSION}/defichain-${VERSION}-x86_64-pc-linux-gnu.tar.gz
tar -xvzf defichain-${VERSION}-x86_64-pc-linux-gnu.tar.gz
mkdir ~/.defi/
cp ./defichain-${VERSION}/bin/* ~/.defi/
mkdir ~/.defi/data
mkdir ~/.defi/data/
mkdir ~/.defi/data/testnet3/
mkdir ~/script
mkdir ~/.defi/stats

touch ~/.defi/defi.conf

cat >> ~/.defi/defi.conf << EOF
daemon=1
testnet=1
[test]
rpcuser=$(pwgen -s 8 -N 1)
rpcpassword=$(pwgen -s 64 -N 1)
rpcbind=127.0.0.1
rpcport=18554
addnode=89.58.14.177
addnode=154.53.43.103
addnode=161.97.90.159
addnode=194.233.89.209
datadir=/home/${USERNAME}/.defi/data/
gen=0
spv=1
txindex=1
#debug=staking
EOF

#// Scripte kopieren:
cd ~/script/
wget https://mydeficha.in/tools/script/testnet3/restart_defid.sh
wget https://raw.githubusercontent.com/mydefichain/testnet/main/api/api_collector.py
wget https://raw.githubusercontent.com/mydefichain/testnet/main/api/api_calls.txt
wget https://raw.githubusercontent.com/mydefichain/testnet/main/api/subfunctions.py

chmod 744 restart_defid.sh

touch ~/script/credentials.py

cat >> ~//script/credentials.py << EOL2
WWW_DIR = "/var/www/$(hostname)/api/"
API_LIST = "/home/${USERNAME}/script/api_calls.txt"
DEFICONF = "/home/${USERNAME}/.defi/defi.conf"
DEFID = "/home/${USERNAME}/.defi/defid"
EOL2

cd ~/
wget http://testnet.snapshot-de.mydefichain.com/${LATEST}
tar -xvzf ${LATEST} -C ~/.defi/data/testnet3/


crontab -l | { cat; echo "* * * * * pidof defid || ~/.defi/defid"; } | crontab -
crontab -l | { cat; echo "*/5 * * * * python3.9 ~/script/api_collector.py"; } | crontab -

pip3.9 install python-bitcoinrpc
pip3 install python-bitcoinrpc
pip3.9 install psutil
pip3 install psutil

#Wait for Start defid and create API
echo "Wait 60 seconds to start defid and create API. Be patient..."
sleep 60

cd ~/script/
python3.9 api_collector.py

echo "Installation Complete, type ~/.defi/defi-cli getblockcount to check the Sync-State."
sleep 3
EOL


echo "Installation Complete, please reboot now with shutdown -r now and login as "${USERNAME}" and start su "${USERNAME} $install_user
