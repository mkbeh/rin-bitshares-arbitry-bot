# Bitshares arbitrage bot
An arbitration bot only works inside bitshares.
The bot builds up the volume of four assets: 
BTS, BRIDGE.BTC, CNY, USD. Market pairs are taken 
from the bitshares node and then are added to the 
chains along which the bot works. The description 
of the arbitration algorithm is in the module 
`src.algorithms.arbitryalgorithm`.


## Getting started

### Installing Bitshares node and wallet
...

### Configuring nginx
...

### Installing BitShares Explorer REST API
Use this manual https://github.com/oxarbitrage/bitshares-explorer-api

### Installing bot
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
Just type rin in the command line and press enter.

On first app startup will be generated config, 
which must be filled. When you will fill config , 
run application again
```

#### Note
```angular2
If you want to compile modules by Cython - uncomment
lines in setup.py and change the extension of 
the desired files to .pyx. Cython compiling does not
testing.
```