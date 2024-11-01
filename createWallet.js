const StellarSdk = require("@stellar/stellar-sdk")

const pair = StellarSdk.Keypair.random()

const [publicKey, privateKey] = [pair.publicKey(), pair.secret()]

console.log(`Public key: ${publicKey}\nprivate key: ${privateKey}`)
