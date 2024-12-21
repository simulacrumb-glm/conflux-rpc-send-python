# conflux-rpc-send-python
Python Scripts to send transactions on Conflux Core Space and Conflux eSpace

## requirements

web3.py
Documentation https://web3py.readthedocs.io/

conflux-web3 (for core space interaction)
Documentation https://python-conflux-sdk.readthedocs.io/

### install requirements
```bash
pip install -r requirements.txt
```

## Scripts

### core_send.py
- Send CFX on Conflux Core Space

### core_transfer_evm.py
- Cross-Space CFX from Conflux Core Space to Conflux eSpace
- Utilizes the [Conflux internal contract: CrossSpaceCall](https://doc.confluxnetwork.org/docs/core/core-space-basics/internal-contracts/crossSpaceCall)

### espace_send.py
- Send CFX on Conflux eSpace
- Include a message

### espace_swap.py
- Swap CFX for an ERC-20 token using https://swappi.io

## Shared features
### Batching
All scripts with the exception of `espace_swap.py` have the ability to send multiple transactions. They are first built and signed in batch and then sent in batch.

A boolen flag `repeat_one` further determines if you want to send the same transaction inputs multiple times or would like to provide unique inputs for each transaction.

###
Report printed to the console showing:
- Number of transactions sent
- Total time taken to send transactions
- From address
- Contract Utilized address (if applicable)
- To[Last]: the `to` address parameter of the last transaction
- Gas Used
- Last Nonce hash for tracing on [Confluxscan](https://confluxscan.io) 
- Last Nonce #
- Last transaction receipt data

### Private Key Management

- All scripts require a wallet private key to sign transactions.
- The best practice is to set private keys as environment variables via terminal or add a .env script. This is HIGHLY recommended and all scripts are setup to read private keys from ENV variables
> As a fallback, they can be pasted into `yourprivatekey` variable within the script
> But be CARFEFUL, NEVER EVER share your private key.


#### Below are exampels of how to set the environment variables

Windows Command Shell
```cmd
set private_key_core=abc123
set private_key_evm=def456
```

Jupyter Notebook
```cmd
! set private_key_core=abc123
! set private_key_evm=def456
```
MacOS and *nix shell
```bash
export private_key_core=abc123
export private_key_evm=def456
```

## Support and further learning
- [Conflux Developer Documentation](https://doc.confluxnetwork.org/)
- [Conflux Devs Telegram](https://t.me/ConfluxDevs)
- [Conflux Network Discord](https://discord.com/invite/confluxnetwork)