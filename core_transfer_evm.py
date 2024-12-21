import json
import os
import time
from conflux_web3 import Web3
from cfx_utils.token_unit import (
    to_int_if_drip_units
)

''' Set Network Endpoint
    https://doc.confluxnetwork.org/docs/espace/network-endpoints
'''
provider_rpc = {
    "core_testnet": "https://test.confluxrpc.org",
    "core_mainnet": "https://main.confluxrpc.org",
    "core_mainnet_hk": "https://main.confluxrpc.com",
    "evm_testnet": "https://evmtestnet.confluxrpc.org",
    "evm_mainnet": "https://evm.confluxrpc.org",
    "evm_mainnet_hk": "https://evm.confluxrpc.com",
}

# Our Endpoint
rpc_name = "core_mainnet"

# Initialize Web3 provider
web3 = Web3(Web3.HTTPProvider(provider_rpc[rpc_name]))


''' Set Wallet Config
        Best practice is to set private keys as environment variables via terminal or .env script
        fallback, paste it into the `yourprivatekey` variable below, but be careful, NEVER EVER share your private key
    Windows cmd example:
        set private_key_core=abc123
        set private_key_evm=def456
    Jupyter Notebook example
        ! set private_key_core=abc123
        ! set private_key_evm=def456
    MacOS and *nix shell example
        export private_key_core=abc123
        export private_key_evm=def456
'''
yourprivatekey = ""

# Core Space/ eSpace may need different private keys
if "evm" in rpc_name:
    pk_variable = "private_key_evm"
else:
    pk_variable = "private_key_core"

account_from = {
    "private_key": os.environ.get(pk_variable, yourprivatekey),
    # this will prioritize environment variable then 'yourprivatekey'
}
assert account_from["private_key"], 'account_from["private_key"] is not set'
account = web3.account.from_key(account_from["private_key"])
start_nonce = web3.cfx.get_next_nonce(account.address)


''' Contract config 
    Conflux internal contract: CrossSpaceCall
    https://doc.confluxnetwork.org/docs/core/core-space-basics/internal-contracts/crossSpaceCall
'''
contract_address = "cfx:aaejuaaaaaaaaaaaaaaaaaaaaaaaaaaaa2sn102vjv"
abi_string="""[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes20","name":"sender","type":"bytes20"},{"indexed":true,"internalType":"bytes20","name":"receiver","type":"bytes20"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"data","type":"bytes"}],"name":"Call","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes20","name":"sender","type":"bytes20"},{"indexed":true,"internalType":"bytes20","name":"contract_address","type":"bytes20"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"nonce","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"init","type":"bytes"}],"name":"Create","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"success","type":"bool"}],"name":"Outcome","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes20","name":"sender","type":"bytes20"},{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"nonce","type":"uint256"}],"name":"Withdraw","type":"event"},{"inputs":[{"internalType":"bytes","name":"init","type":"bytes"}],"name":"createEVM","outputs":[{"internalType":"bytes20","name":"","type":"bytes20"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes20","name":"to","type":"bytes20"}],"name":"transferEVM","outputs":[{"internalType":"bytes","name":"output","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes20","name":"to","type":"bytes20"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"callEVM","outputs":[{"internalType":"bytes","name":"output","type":"bytes"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes20","name":"to","type":"bytes20"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"staticCallEVM","outputs":[{"internalType":"bytes","name":"output","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"deployEip1820","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"value","type":"uint256"}],"name":"withdrawFromMapped","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"mappedBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"mappedNonce","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]"""
abi=json.loads(abi_string)
Contract = web3.eth.contract(address=contract_address, abi=abi)

''' Setup default transaction parameters '''
tx_defaults = {
    'chainId': web3.cfx.chain_id,
    'epochHeight': web3.cfx.epoch_number,
    'gasPrice': to_int_if_drip_units(web3.cfx.gas_price),
    'nonce': start_nonce,
    'from': account.address,
    'value': 1
}

# Estimation requires a "to" address parameter
default_to = "0xC2162fA440969DEcd7b2Ba4d9d07937a3B399094"

# estimate once
estimate_result = web3.cfx.estimate_gas_and_collateral(
    Contract.functions.transferEVM(to=default_to).build_transaction(tx_defaults)
    )
tx_defaults['gas'] = estimate_result['gasLimit']
tx_defaults['storageLimit'] = estimate_result['storageCollateralized']

cache = []

if __name__ == '__main__':

    ''' *IMPORTANT*:

        Set repeat_one to True to send the same transation `batch_size` number of times
        Set `batch_size`, `value`, and `to_address`

        --OR--

        Set repeat_one to False to specify unique inputs for each transaction
        Set `values_matrix`

        ------

        `value` and `values_matrix][*][0]` are wei in integers
            https://www.geeksforgeeks.org/what-are-the-different-units-used-in-ethereum/
            For example value = 1 means 1wei or 0.000000000000000001 CFX)
            Use web3.to_wei for conversion:
                web3.to_wei(1, "gwei") == 1000000000 == 0.000000001 CFX
                web3.to_wei(1, "ether") == 1000000000000000000 == 1 CFX
    '''
    repeat_one = False

    if repeat_one:
        # How many transactions to send?
        batch_size = 2

        # Amount to send
        value = 3

        ''' Specify "0x..." eSpace address to send to
            *IMPORTANT*: Leaving "to" parameter blank for `transferEVM`
                results in sending to the zero address
        '''
        to_address = default_to

        values_matrix = [[value, to_address]]
        values_matrix.extend([[value, to_address]] * (batch_size -1))

    else:
        # Specify [value, "0x..."] eSpace address for each transaction
        values_matrix = [
            [3, default_to],
            [6, default_to],
        ]

    # Now we have a matrix of transaction inputs `values_matrix` to iterate over
    
    ''' Build and sign all transactions '''
    for i in range(len(values_matrix)):

        this_params = tx_defaults.copy()
        ''' Add unique transaction parameters to the default set '''
        this_params["value"] = values_matrix[i][0]
        this_params["nonce"] = start_nonce + i
        this_prebuilt_tx = None
        this_prebuilt_tx = Contract.functions.transferEVM(to=values_matrix[i][1]).build_transaction( 
            this_params
            )
        this_tx = None
        this_tx = account.sign_transaction(this_prebuilt_tx)
        cache.append(this_tx)

    ''' Send all and display status '''      
    print("packed %s transactions" % (len(values_matrix)) )  
    start = time.time()
    print("Starting to send transactions @ %s " % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))) )
    res = [web3.cfx.send_raw_transaction(j.rawTransaction) for j in cache]
    print("Sent %s transactions in %s seconds" % (len(values_matrix), time.time() - start) )
    print("From: %s" % (account.address) )
    print("Using Contract: %s" % (contract_address) )
    print("To[Last]: %s" % (values_matrix[-1][1]) )
    print("Gas estimate: %s" % (estimate_result) )
    print("Last Nonce hash: %s" % (res[-1].hex()) )
    print("Last Nonce #: %s" % (this_params["nonce"]))
    print("Awaiting Last Nonce transaction receipt...\n")
    print(web3.eth.wait_for_transaction_receipt(res[-1].hex()) )