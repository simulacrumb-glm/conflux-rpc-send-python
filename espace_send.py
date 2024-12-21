import os
import time
from web3 import Web3

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
rpc_name = "evm_mainnet"

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
account = web3.eth.account.from_key(account_from["private_key"])
start_nonce = web3.eth.get_transaction_count(account.address)


''' Include calldata
    Only include if you want to include a message or inscription
    Costs gas to include!
'''
calldata_str = "Conflux4ever!"
#calldata_str = 'data:,{"p":"cfxs-20","op":"mint","tick":"BSIM","amt":"1000"}'
hex_data = web3.to_hex(calldata_str.encode('utf-8'))

''' Setup default transaction parameters '''
tx_defaults = {
    'chainId': web3.eth.chain_id,
    "nonce": start_nonce,
    'gasPrice': web3.eth.gas_price,
    'from': account.address,
    "value": 0,
    "data": hex_data
}

address_for_estimation = Web3.to_checksum_address(account.address)

''' Estimate once '''
estimate_result = web3.eth.estimate_gas(tx_defaults)
tx_defaults['gas'] = estimate_result

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

        # Specify "0x..." eSpace address to send to
        to_address = ""

        values_matrix = [[value, to_address]]
        values_matrix.extend([[value, to_address]] * (batch_size -1))

    else:
        # Specify [value, "0x..."] eSpace address for each transaction
        values_matrix = [
            [3, ""],
            [6, ""],
        ]

    # Now we have a matrix of transaction inputs `values_matrix` to iterate over
    
    for i in range(len(values_matrix)):

        this_params = tx_defaults.copy()
        ''' Add unique transaction parameters to the default set '''
        this_params["to"] = address_for_estimation
        this_params["value"] = values_matrix[i][0]
        this_params["nonce"] = start_nonce + i
        this_tx = None
        this_tx = account.sign_transaction(this_params)
        cache.append(this_tx)

    ''' Send all and display status '''      
    print("packed %s transactions" % (len(values_matrix)) )  
    start = time.time()
    print("Starting to send transactions @ %s " % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))) )
    res = [web3.eth.send_raw_transaction(j.rawTransaction) for j in cache]
    print("Sent %s transactions in %s seconds" % (len(values_matrix), time.time() - start) )
    print("From: %s" % (account.address) )
    print("To[Last]: %s" % (this_params["to"]) )
    print("Gas estimate: %s" % (estimate_result) )
    print("Last Nonce hash: %s" % (res[-1].hex()) )
    print("Last Nonce #: %s" % (this_params["nonce"]))
    print("Awaiting Last Nonce transaction receipt...\n")
    print(web3.eth.wait_for_transaction_receipt(res[-1].hex()) )
