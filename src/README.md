# Bitshares arbitrage bot
An arbitration bot only works inside bitshares.
The bot builds up the volume of four assets: 
BTS, BRIDGE.BTC, CNY, USD. Market pairs are taken 
from the bitshares node and then are added to the 
chains along which the bot works. The description 
of the arbitration algorithm is in the module 
`src.algorithms.arbitryalgorithm`.

### **How it works**
Here will be block scheme


## **Getting started**

### **Installing Bitshares node and wallet**
...

### **Configuring nginx**
...

### **Installing BitShares Explorer REST API**
Use this manual https://github.com/oxarbitrage/bitshares-explorer-api

### **Installing bot**
The following procedure will work in Debian 
based Linux, more specifically the commands 
to make the guide were executed in Ubuntu 18.10 
with Python 3.7.

```angular2
# Cloning repository #
git clone https://github.com/mkbeh/rin-bitshares-arbitry-bot
cd rin-bitshares-arbitry-bot

# Creating and activating virtual env #
pip install virtualenv 
virtualenv venv
source venv/bin/activate

# Installing bot #
python3.7 setup.py install

# Running #
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
node uri = 
wallet uri = ws://127.0.0.1:8093/ws - example
explorer uri = 

[ACCOUNT]
account name = account_name
wallet password = wallet_password

[OTHER]
data update time = 1      # Hours. Required int
time to reconnect = 350   # Secs. Required int
orders depth = 5          # Amount. Required int
```

When you will fill config , run application again , typing
rin-bot in command line.

#### Note
```angular2
If you want to compile modules by Cython - uncomment
lines in setup.py and change the extension of 
the desired files to .pyx. But Cython compiling not
tested so use it at your own risk.
```