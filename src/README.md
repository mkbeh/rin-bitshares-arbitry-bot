# Asynchronous Bitshares arbitrage bot
An arbitration bot only works inside bitshares.
The bot builds up the volume of four assets: 
BTS, BRIDGE.BTC, CNY, USD. Market pairs are taken 
from the bitshares node and then are added to the 
chains along which the bot works. The description 
of the arbitration algorithm is in the module 
`src.algorithms.arbitryalgorithm`. 
***
Further installation assumes that your node, wallet 
and explorer are on one server, and the bot is on another.

### **How bot works**
[TO DO]


## **Getting started**

[TO DO] Сделать содержание со ссылками для перехода
к отдельным пунктам доки.

### **Installing Bitshares node and wallet**
> sudo apt-get update

> sudo apt-get install autoconf cmake make automake libtool git libboost-all-dev libssl-dev g++ libcurl4-openssl-dev

> wget https://github.com/bitshares/bitshares-core/releases/download/2.0.190219/BitShares-Core-2.0.190219-Linux-cli-tools.tar.gz

> tar -xzvf BitShares-Core-2.0.190219-Linux-cli-tools.tar.gz

> rm BitShares-Core-2.0.190219-Linux-cli-tools.tar.gz

#### **Adding node and wallet to supervisor**
[TO DO]

#### Configuring wallet.
```bash
./cli_wallet --server-rpc-endpoint=wss://bitshares.openledger.info/ws -r 127.0.0.1:8093
set_password <your_super_pwd>
unlock <your_super_pwd>
import_key <user_name> <priv_key>
```

**NOTE:**

If error while trying to run wallet:
```bash
Logging RPC to file: logs/rpc/rpc.log
terminate called after throwing an instance of 'std::runtime_error'
  what():  locale::facet::_S_create_c_locale name not valid
Aborted (core dumped)
```

Try this:
```bash
sudo vi ~/.bashrc

# Add line to the end of the file
export LC_ALL=C
```

### **Installing nginx**
> wget http://nginx.org/download/nginx-1.11.3.tar.gz

> tar -xzvf nginx-1.11.3.tar.gz

> rm nginx-1.11.3.tar.gz

> cd nginx-1.11.3/

> sudo apt-get install libpcre3 libpcre3-dev libpcrecpp0v5 libssl-dev zlib1g-dev build-essential

> ./configure --sbin-path=/usr/bin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --with-debug --with-pcre --with-cc-opt="-Wno-error" --with-http_ssl_module

> make

> sudo make install

### **Configuring nginx**

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

#### **Adding ssl**
```bash
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot python-certbot-nginx 

cd /run/
ln -s /usr/local/nginx/logs/nginx.pid nginx.pid

certbot --nginx -d wallet.domain.com certonly

crontab -e
# Add next line for auto updating cert.
@daily certbot renew
```

#### **Filling nginx.conf**
> vi /etc/nginx/nginx.conf

```bash
# user  cyberpunk;
worker_processes  auto;

events {
    worker_connections  2048;
    multi_accept on;
    use epoll;
}


http {

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    # Enable open file cache
    open_file_cache		max=1000 inactive=20s;
    open_file_cache_valid	30s;
    open_file_cache_min_uses	2;
    open_file_cache_errors	on;

    # Keepalive
    keepalive_timeout 300;

    send_timeout 10;

    # Hide nginx version information.
    server_tokens off;
    
    # Websockets
    map $http_upgrade $connection_upgrade {
	    default upgrade;
	    ''        close;
	}

    upstream subwallet {
	server 127.0.0.1:8093;
    }

    upstream subnode {
    	server 127.0.0.1:8094;
    }   

    server {
        listen 443 ssl;

        ssl_certificate         /etc/letsencrypt/live/wallet.domain.com/fullchain.pem;
        ssl_certificate_key     /etc/letsencrypt/live/wallet.domain.com/privkey.pem;
        include                 /etc/letsencrypt/options-ssl-nginx.conf;
        ssl_dhparam             /etc/letsencrypt/ssl-dhparams.pem;

        server_name wallet.domain.com;

        location /ws {
            proxy_pass http://subwallet;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;

            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    
    server {
        listen 80;
        server_name node.domain.com;

        location /ws {
            proxy_pass http://subnode;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;

            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    
    server {
        listen 80;
        server_name api.domain.com;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/tmp/app.sock;
        }
    }
} 

```
> systemctl restart NGINX.service


### **Installing BitShares Explorer REST API**

#### **NOTE**
```bash
Do everything that is described in the following guide until creating nginx config.
```
Use this manual https://github.com/oxarbitrage/bitshares-explorer-api

### **Installing and usage bot**
The following procedure will work in Debian 
based Linux, more specifically the commands 
to make the guide were executed in Ubuntu 18.10 
with Python 3.7.

```bash
# Cloning repository
git clone https://github.com/mkbeh/rin-bitshares-arbitry-bot
cd rin-bitshares-arbitry-bot

# Creating and activating virtual env
pip install virtualenv 
virtualenv venv
source venv/bin/activate

# Installing bot
python3.7 setup.py install

# Running bot
Just type rin-bot in the command line and press enter.

On first app startup will be generated config, 
which must be filled.
```

#### **Contents of the config.ini file**
```angular2
[DIRS]
output dir = path/to/output/directory/output # name output requried
log dir = path/to/log/directory/logs         # name logs required

[MIN_DAILY_VOLUME]
overall min daily volume = 10  #  Must be non float value
pair min daily volume = 5      #  Must be non float value

[LIMITS]
# Options values must be dicts. Values in dicts must have types int 
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
data update time = 1      # Hours. Required int
time to reconnect = 350   # Reconnect to node or wallet. Secs. Required int
orders depth = 5          # Amount. Required int
```

When you will fill config , run application again , typing
rin-bot in command line again , being in a previously 
activated virtual environment.

#### Logging
[TO DO]

#### Note
```angular2
If you want to compile modules by Cython - uncomment
lines in setup.py and change the extension of 
the desired files to .pyx. But Cython compiling not
tested so use it at your own risk.
```
### **Roadmap**:
* Write own async cmd explorer REST API without web interface instead 
oxarbitrage explorer.
* Improve bot by adding new features.
* Write full async lib for Bitshares API.
