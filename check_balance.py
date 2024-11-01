from stellar_sdk import Keypair, Server
from dotenv import load_dotenv
import os

load_dotenv()

def verificar_saldo(private_key):
    url = "https://horizon.stellar.org"
    server = Server(horizon_url=url)

    keypair = Keypair.from_secret(private_key)
    public_key = keypair.public_key
    account = server.accounts().account_id(public_key).call()

    for balance in account['balances']:
        asset_type = balance['asset_type']
        asset_balance = balance['balance']
        print(f"Saldo: {asset_balance} {asset_type}")

private_key = os.getenv('private_key')
verificar_saldo(private_key)
