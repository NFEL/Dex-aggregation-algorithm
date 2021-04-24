from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/"))
w3.isConnected()