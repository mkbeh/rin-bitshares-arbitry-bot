# Asynchronous Bitshares arbitrage bot
An arbitration bot only works inside bitshares.
The bot builds up the volume of four assets: 
BTS, BRIDGE.BTC, CNY, USD. Market pairs are taken 
from third party API using the bitshares node with ES plugin. Then market pairs are added to the 
chains along which the bot works. The description 
of the arbitration algorithm is in the module 
`src.algorithms.arbitryalgorithm`. 
***

### **How bot works**
[TO DO]


## **Getting started**

* [Installing Bitshares node and wallet](#installing-bitshares-node-and-wallet)
    * [Configuring node](#configuring-node)
    * [Configuring wallet](#configuring-wallet)

**The following actions were performed on ubuntu 18.10**

### **Installing Bitshares node and wallet**
> vi /etc/apt/sources.list

```bash
# Add repo.
deb http://security.ubuntu.com/ubuntu xenial-security main
```

> sudo apt-get update

> sudo apt-get install autoconf cmake make automake libtool git libboost-all-dev libssl-dev g++ libcurl4-openssl-dev libgconf-2-4 libcurl3

> wget https://github.com/bitshares/bitshares-core/releases/download/2.0.190219/BitShares-Core-2.0.190219-Linux-cli-tools.tar.gz

> tar -xzvf BitShares-Core-2.0.190219-Linux-cli-tools.tar.gz

> rm BitShares-Core-2.0.190219-Linux-cli-tools.tar.gz

#### **Configuring node**
> sudo apt-get install supervisor

> sudo vi /etc/supervisor/conf.d/bts_node.conf
```bash
[program:bts_node]
command=/home/<user>/programs/witness_node/witness_node --rpc-endpoint="127.0.0.1:8091"
directory=/home/<user>/programs/witness_node/
stdout_logfile=/var/log/supervisor/bts_node_out.log
stderr_logfile=/var/log/supervisor/bts_node_err.log
autostart=true
autorestart=true
numprocs=1
user=<user>
```

When the node is synchronized - go to the next step.

#### **Configuring wallet**
```bash
cd programs/cli_wallet/
./cli_wallet --server-rpc-endpoint=ws://127.0.0.1:8091 -r 127.0.0.1:8093
set_password <your_super_pwd>
unlock <your_super_pwd>
import_key <user_name> <priv_key>
```

**NOTE:**

If error while trying to run wallet:
```
Logging RPC to file: logs/rpc/rpc.log
terminate called after throwing an instance of 'std::runtime_error'
  what():  locale::facet::_S_create_c_locale name not valid
Aborted (core dumped)
```

Try this:
> sudo vi /etc/default/locale
```
# The file should look like this:
LANGUAGE=en_US.UTF-8
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
LC_TYPE=en_US.UTF-8
```

```bash
locale-gen en_US.UTF-8
dpkg-reconfigure locales
```
> sudo vi /etc/supervisor/conf.d/bts_wallet.conf
```bash
[program:bts_wallet]
command=/home/<user>/programs/cli_wallet/cli_wallet --server-rpc-endpoint=ws://127.0.0.1:8091 -r 127.0.0.1:8093
directory=/home/<user>/programs/cli_wallet/
stdout_logfile=/var/log/supervisor/bts_wallet_out.log
stderr_logfile=/var/log/supervisor/bts_wallet_err.log
autostart=true
autorestart=true
numprocs=1
user=<user>
```

> sudo supervisorctl reread

> sudo supervisorctl update

> sudo supervisorctl start bts_node

> sudo supervisorctl start bts_wallet

### **Installing nginx**
> wget http://nginx.org/download/nginx-1.11.3.tar.gz

> tar -xzvf nginx-1.11.3.tar.gz

> rm nginx-1.11.3.tar.gz

> cd nginx-1.11.3/

> sudo apt-get install libpcre3 libpcre3-dev libpcrecpp0v5 zlib1g-dev build-essential libssl1.0-dev

> ./configure --sbin-path=/usr/bin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --with-debug --with-pcre --with-cc-opt="-Wno-error" --with-http_ssl_module --with-threads

> make

> sudo make install

### **Configuring nginx**
Previously buy domain and add 2 CNAME records for subdomens:
wallet.your-domain.com, node.your-domain.com.

#### **Base configuration**
> sudo vi /lib/systemd/system/NGINX.service
```angular2
[Unit]
Description=The NGINX HTTP and reverse proxy server
After=syslog.target network.target remote-fs.target nss-lookup.target

[Service]
Type=forking
PIDFile=/usr/local/nginx/logs/nginx.pid
ExecStartPre=/usr/bin/nginx -t
ExecStart=/usr/bin/nginx
ExecReload=/usr/bin/nginx -s reload
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
> systemctl daemon-reload

> systemctl enable NGINX.service

> systemctl start NGINX.service

> systemctl -l status NGINX.service

#### **Filling nginx.conf**
Don't forget to change stubs in nginx.conf on yours values.

> vi /etc/sysctl.conf
```bash
# Add next line in the end of the file.
fs.file-max = 40000
```
> sysctl -p

> vi /etc/nginx/nginx.conf

```bash
# user  nobody;
worker_processes         auto;
worker_rlimit_nofile     40000;

pid                      /usr/local/nginx/logs/nginx.pid;

events {
    worker_connections   <set_value>;   # worker_rlimit_nofile / worker_processes
    multi_accept         on;
    use                  epoll;
}


http {
    # Basic settings
    sendfile       on;
    tcp_nopush     on;
    tcp_nodelay    on;
    aio            threads;  

    # Logging
    access_log     off;
    error_log      /var/log/nginx/error.log crit;

    # Enable open file cache
    open_file_cache             max=1000 inactive=20s;
    open_file_cache_valid       30s;
    open_file_cache_min_uses    2;
    open_file_cache_errors      on;

    # Keepalive
    keepalive_timeout    30s;
    send_timeout         10s;

    # Hide nginx version information.
    server_tokens        off;
    
    # Websockets
    map $http_upgrade $connection_upgrade {
	    default upgrade;
	    ''        close;
	}
    
    # -- Upstreams --
    upstream subwallet {
        server 127.0.0.1:8093;
    }

    upstream subnode {
    	server 127.0.0.1:8091;
    }   
    
    # --- Servers directives ---
    server {
        # listen                     443 ssl;
        listen                     80;
        server_name                wallet.domain.com;
        
        # <----- Uncomment this after generating ssl certs. ------->
        # ssl_certificate            /etc/letsencrypt/live/wallet.domain.com/fullchain.pem;
        # ssl_certificate_key        /etc/letsencrypt/live/wallet.domain.com/privkey.pem;
        # include                    /etc/letsencrypt/options-ssl-nginx.conf;
        # ssl_dhparam                /etc/letsencrypt/ssl-dhparams.pem;
        # <-----                ------->
    
        location /ws {
            proxy_pass             http://subwallet;
            proxy_http_version     1.1;
            proxy_set_header       Upgrade $http_upgrade;
            proxy_set_header       Connection $connection_upgrade;
    
            proxy_set_header       Host $http_host;
            proxy_set_header       X-Real-IP $remote_addr;
            proxy_set_header       X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header       X-Forwarded-Proto $scheme;
            
            proxy_read_timeout     300s;
            proxy_connect_timeout  10s;

        }
    }

    server {
        listen                     80;
        server_name                node.domain.com;
	
        location /ws {
            proxy_pass             http://subnode;
            proxy_http_version     1.1;
            proxy_set_header       Upgrade $http_upgrade;
            proxy_set_header       Connection $connection_upgrade;

            proxy_set_header       Host $http_host;
            proxy_set_header       X-Real-IP $remote_addr;
            proxy_set_header       X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header       X-Forwarded-Proto $scheme;
            
            proxy_read_timeout     60s;
            proxy_connect_timeout  10s;
        }
    }
}
```
> systemctl restart NGINX.service

or do 

> systemctl reload NGINX.service

#### **Adding ssl**
```bash
IMPORTANT NOTE:
Adding ssl you will get a memory leak due to the fact 
that the aiohttp 3.5.4 library with python3.7 contains a memory leak when working with ssl.
So , do not use ssl until this bug is fixed.
```

```
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot python-certbot-nginx 

certbot --nginx -d wallet.domain.com certonly

crontab -e
# Add next line for auto updating cert.
@daily certbot renew

# Change values in /etc/letsencrypt/options-ssl-nginx.conf.
ssl_session_cache shared:le_nginx_SSL:100m;
ssl_session_timeout 4h;
```

#### **NOTE**
```bash
If something was wrong -> reboot your system and try again , in 99 percent of the happenings it helps :D
```

After previous steps uncomment lines in nginx.conf and replace domens on yours. Then reboot your system.

### Server security setting

#### **Add SSH keys**
```bash
# On your local car.
ssh-keygen
mv key_name* ~/.ssh/
ssh-copy-id user@server_ip

# On remote server. 
# Disable pas auth.
sudo vi /etc/ssh/sshd_config
-> replace yes to no in PasswordAuthentication line
sudo systemctl reload sshd
```

#### **Configuring UFW**
Сhange firewall settings to your liking.
```bash
ufw default deny incoming 
ufw default allow outgoing
ufw allow ssh
ufw enable
ufw allow from <your ip> to any port www
ufw allow from <your ip> to any port 443
```

### **Installing and usage bot**
The following procedure will work in Debian 
based Linux, more specifically the commands 
to make the guide were executed in Ubuntu 18.10 
with Python 3.7.

```
# Installing python 3.7
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz
sudo tar xzf Python-3.7.2.tgz
cd Python-3.7.2
sudo ./configure --enable-optimizations
sudo make install
Python-3.7.2 -V

# Cloning repository
git clone https://github.com/mkbeh/rin-bitshares-arbitry-bot
cd rin-bitshares-arbitry-bot

# Creating and activating virtual env
sudo pip install virtualenv 
virtualenv venv
source venv/bin/activate

pip3.7 install Cython
pip3.7 install numpy

# Installing bot
python3.7 setup.py install

# Running bot
Just type rin-bot in the command line and press enter.
```
On first app startup will be generated config, 
which must be filled. 
Config is located -> /home/\<user>/rin-bot/config.ini

#### **Contents of the config.ini file**
Explorer uri you can get here https://github.com/oxarbitrage/bitshares-explorer-api

```angular2
[DIRS]
output dir = path/to/output/directory/output # name output requried
log dir = path/to/log/directory/logs         # name logs required

[MIN_DAILY_VOLUME]
overall min daily volume = 10  #  Must be non float value
pair min daily volume = 5      #  Must be non float value

[LIMITS]
# Values of the options must be dicts. Values in dicts must have types int 
# or float. Values in dict 'volume limits' expressed in dollars.
volume limits = {"1.3.0": 15, "1.3.113": 15, "1.3.1570": 15, "1.3.121": 15}
min profit limits = {"1.3.0": 0.001, "1.3.113": 0.02, "1.3.1570": 2e-08, "1.3.121": 0.02}

[URI]
node uri = nodr_uri
wallet uri = ws://127.0.0.1:8093/ws      # example
explorer uri = explrer_uri

[ACCOUNT]
account name = account_name
wallet password = wallet_password

[OTHER]
# IMPORTANT: If u want to change 'data update time' don't forget change proxy_read_timeout
# in server directive of wallet subdomain in nginx.conf - otherwise you will get an error 
# associated with websocket connection because nginx will drop some ws connections by timeout.
data update time = 1      # Hours. Required int
time to reconnect = 350   # Reconnect to node or wallet. Secs. Required int
orders depth = 5          # Amount. Required int
```

When you will fill config - go to the next step.

### Adding to supervisor
> sudo vi /etc/supervisor/conf.d/rin-bot.conf
```bash
[program:rin-bot]
command=/home/<user>/rin-bitshares-arbitry-bot/venv/bin/rin-bot
autostart=true
autorestart=true
stopsignal=KILL
numprocs=1
user=<user>
```

> sudo supervisorctl reread

> sudo supervisorctl update

> sudo supervisorctl start rin-bot

#### Logging
Logs, output files and config are available by path /home/\<user>/rin-bot

#### Note
```angular2
If you want to compile modules by Cython - uncomment
lines in setup.py and change the extension of 
the desired files to .pyx. But Cython compiling not
tested so use it at your own risk.
```
### **Milestones**:
* Write own async cmd explorer REST API without web interface.
* Improve bot by adding new features.
* Write full async lib for Bitshares API.
