from stellar_sdk import Keypair, Server, TransactionBuilder, Network
from stellar_sdk.exceptions import NotFoundError, BadRequestError

from dotenv import load_dotenv
import os
load_dotenv()

def fund_new_account(sender_secret: str, new_account_public_key: str, starting_balance: float = 1.0):
    server = Server(horizon_url="https://horizon.stellar.org")

    sender_keypair = Keypair.from_secret(sender_secret)
    sender_public_key = sender_keypair.public_key

    try:
        sender_account = server.load_account(sender_public_key)
    except NotFoundError:
        print("Sender account not found on the Stellar network.")
        return
    except BadRequestError:
        print("Invalid sender account details.")
        return

    try:
        server.load_account(new_account_public_key)
        print("The new account already exists on the Stellar network.")
        return
    except NotFoundError:
        print("New account does not exist and will be created.")

    transaction = (
        TransactionBuilder(
            source_account=sender_account,
            network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
            base_fee=100
        )
        .add_text_memo("Account Funding")
        .append_create_account_op(
            destination=new_account_public_key,
            starting_balance=str(starting_balance)
        )
        .set_timeout(30)
        .build()
    )

    transaction.sign(sender_keypair)

    try:
        response = server.submit_transaction(transaction)
        print("Transaction successful! The new account has been funded and activated.")
        print("Transaction Hash:", response["hash"])
        print("View on Stellar Expert:", f"https://stellar.expert/explorer/public/tx/{response['hash']}")
    except Exception as e:
        print(f"An error occurred: {e}")


sender_secret = os.getenv('private_key')
new_account_public_key = "CHAVE PÚBLICA DA CONTA NOVA SEM FUNDO AQUI"
fund_new_account(sender_secret, new_account_public_key)
