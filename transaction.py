import base64
from stellar_sdk import Keypair, Network, Server, TransactionBuilder
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk import Operation
from stellar_sdk.exceptions import BadSignatureError
from stellar_sdk.exceptions import NotFoundError
from requests import get, RequestException

from dotenv import load_dotenv
import os
load_dotenv()

SERVER_URL = "https://horizon.stellar.org" #"http://localhost:8000"


###
# Desafio 2:
# - Utilizar o Stellar SDK em **Python** ou **JavaScript**.
# - Assinar a msg "DEV30K" usando a chave privada
# - Criar uma transação `menage_data_op` a assinatura da msg no campo MEMO.
# - Enviar para a rede Mainnet da Stellar.
# - Explicar os critérios de aceite: hash da transação no forms
###

def create_account(public_key, server):
    url = "http://localhost:8000/friendbot"
    params = {"addr": public_key}
    timeout = 30
    try:
        r = get(url, params=params, timeout=timeout)
        r.raise_for_status()
    except RequestException as e:
        raise ValueError(f"Erro ao obter fundos do Friendbot: {str(e)}") from e
    account = server.accounts().account_id(public_key).call()
    balances = account["balances"]
    print(f"✅ Conta criada com sucesso: {public_key}")
    print("🔄 Saldo da Conta:")
    for balance in balances:
        asset_type = balance["asset_type"]
        balance_amount = balance["balance"]
        print(f"   - Tipo de Ativo: {asset_type}, Saldo: {balance_amount}")
    return account


def validate_account(public_key, server):
    try:
        account = server.load_account(public_key)
        print("✅ A conta de destino foi validada!")
        return account
    except NotFoundError:
        print("🚫 A conta de destino não existe!")
        print("🔧 Criando a conta...")
        return create_account(public_key, server)


def write(private_key):
    sender_keypair = Keypair.from_secret(private_key)
    server = Server(horizon_url=SERVER_URL)
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE

    sender_account = validate_account(sender_keypair.public_key, server)

    mensagem = "DEV30K".encode()
    assinatura = sender_keypair.sign(mensagem)
    assinatura_b64 = base64.b64encode(assinatura).decode()
    data_key = "desafio"

    print(f"📝 Mensagem Assinada (base64): {assinatura_b64}")

    transaction = (
        TransactionBuilder(
            source_account=sender_account,
            network_passphrase=network_passphrase,
            base_fee=100,
        )
        .set_timeout(30)
        .add_text_memo("DEV30K")
        .append_manage_data_op(data_name=data_key, data_value=assinatura)
        .build()
    )
    transaction.sign(sender_keypair)

    try:
        response = server.submit_transaction(transaction)
        print("✅ Transação enviada com sucesso!")
        print(f"🔗 Hash da Transação: {response['hash']}")

        # Salvar o hash da transação em um arquivo
        tx_hash = response["hash"]
        with open("tx_hash.txt", "w", encoding="utf-8") as f:
            f.write(tx_hash)
        print("📝 Hash da transação salvo em 'tx_hash.txt'.")
    except Exception as e:
        print("🚨 Erro ao enviar a transação:")
        print(e)


def read(private_key):
    # Configurações iniciais
    sender_keypair = Keypair.from_secret(private_key)
    PUBLIC_KEY = sender_keypair.public_key
    # URL do Horizon na Standalone Network
    server = Server(horizon_url=SERVER_URL)
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE

    # Ler o hash da transação do arquivo
    try:
        with open("tx_hash.txt", "r") as f:
            tx_hash = f.read().strip()
    except FileNotFoundError:
        print("🚨 Arquivo 'tx_hash.txt' não encontrado. Execute o Script 1 primeiro.")
        return

    print(f"🔗 Hash da Transação: {tx_hash}")

    # Recuperar a transação pelo hash
    try:
        tx = server.transactions().transaction(tx_hash).call()
    except NotFoundError:
        print("🚫 Transação não encontrada na rede.")
        return
    except Exception as e:
        print("🚨 Erro ao recuperar a transação:")
        print(e)
        return

    # Recuperar o envelope XDR da transação
    try:
        envelope_xdr = tx["envelope_xdr"]
        te = TransactionEnvelope.from_xdr(envelope_xdr, network_passphrase)
    except Exception as e:
        print("🚨 Erro ao decodificar o envelope XDR:")
        print(e)
        return

    # Extrair a operação Manage Data com a chave "desafio"
    manage_data_op = None
    for op in te.transaction.operations:
        x = isinstance(op, Operation)
        y = op.data_name == "desafio"
        if x and y:
            manage_data_op = op
            break

    if not manage_data_op:
        print(
            "🚫 Operação 'manage_data' com a chave 'desafio' não encontrada na transação."
        )
        print(f"👀 {te.transaction.operations}")
        return

    # Extrair o valor da operação (assinatura em bytes)
    assinatura_bytes = manage_data_op.data_value

    # Codificar a assinatura em base64 para exibição
    assinatura_b64 = base64.b64encode(assinatura_bytes).decode()
    print(f"🗝️ Chave de Dados: {manage_data_op.data_name}")
    print(f"📝 Valor de Dados (base64): {assinatura_b64}")

    # Mensagem original
    mensagem = "DEV30K".encode()

    # Criar um objeto Keypair a partir da chave pública
    try:
        keypair = Keypair.from_public_key(PUBLIC_KEY)
    except Exception as e:
        print("🚨 Erro ao criar Keypair a partir da chave pública:")
        print(e)
        return

    # Verificar a assinatura
    try:
        keypair.verify(mensagem, assinatura_bytes)
        print(
            "✅ A assinatura é válida. A mensagem foi assinada pela chave pública fornecida."
        )
    except BadSignatureError:
        print(
            "❌ A assinatura é inválida. A mensagem não foi assinada pela chave pública fornecida."
        )
    except Exception as e:
        print("🚨 Erro ao verificar a assinatura:")
        print(e)


if __name__ == "__main__":
    private_key = os.getenv('private_key')
    write(private_key)
    read(private_key)
