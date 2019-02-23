# Bitshares arbitrage bot
An arbitration bot only works inside bitshares.
The bot builds up the volume of four assets: 
BTS, BRIDGE.BTC, CNY, USD. Market pairs are taken 
from the bitshares node and then are added to the 
chains along which the bot works. The description 
of the arbitration algorithm is in the module 
**src.algorithms.arbitryalgorithm**.


## Getting started

### Install BitShares Explorer REST API
Use this manual https://github.com/oxarbitrage/bitshares-explorer-api#usage

### Install bot.
The following procedure will work in Debian 
based Linux, more specifically the commands 
to make the guide were executed in Ubuntu 18.10 LTS 
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
```
