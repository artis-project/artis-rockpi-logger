from eth_utils.crypto import keccak
from eth_abi.abi import encode
from eth_account import Account

# Sign the message using the Ethereum account
MESSAGE = "eyJhbGciOiAiRUNEU0EiLCAidHlwIjogIkpXVCJ9.eyJpc3MiOiAiQVJUSVMtUHJvamVjdCIsICJzdWIiOiAiZGlkOmV0aHI6MHg4YzVlZGM2ZTljMWY2OGE5ZTBjZmIwYjBhNjZlOGUwYTViNmUzYzBlIiwgImF1ZCI6ICJBUlRJUy1BUEkiLCAiaWF0IjogMTYyMzM0NTYwMCwgImV4cCI6IDE2MjMzNDkyMDB9"

print('message: ', MESSAGE)

# The signature you want to verify
signature = "0x0a66a63272ae11feeb4bea69de7ac813ac8b64e2edd53bf17e5ec34dc7e178477702d0f28cc47c52145fd63489de04bffd1425017528bf5040d83ac9a67f61581b"

keccak_hash = keccak(primitive=encode(['string'], [MESSAGE]))
# The public key you want to use to verify the signature

print(Account._recover_hash(keccak_hash, signature=signature))