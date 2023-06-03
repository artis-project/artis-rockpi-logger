import json
import base64
from artis_api import ArtisAPI
from eth_utils.crypto import keccak
from eth_abi.abi import encode
from eth_account import Account
from web3 import Web3

api = ArtisAPI()
data = {
    "iss": "ARTIS-Project",
    "sub": "did:ethr:0x64EE2b0872CddFfa8F63C65c03216404F5D19164",
    "aud": "ARTIS-API",
    "iat": 1623345600,
    "exp": 1623349200,
}
header = {
  "alg": "ECDSA",
  "typ": "JWT"
}

def encode_base64(data):
    json_data = json.dumps(data).encode('utf-8')
    base64_data = base64.b64encode(json_data).decode('utf-8')
    return base64_data

base64_header = encode_base64(header)
base64_payload = encode_base64(data)
signature_data = f"{base64_header}.{base64_payload}"
signature = api._sign(signature_data)
token = ".".join([base64_header, base64_payload, signature])
#print("header: ", base64_header)
#print("payload: ", base64_payload)
#print("signature: ", signature)
print("token: ", token)

# Sign the message using the Ethereum account
header, payload, signature = token.split('.')
print(signature)
MESSAGE = token[:token.rfind('.')]
print(MESSAGE)
decoded_payload = json.loads(base64.b64decode(payload).decode('utf-8'))
did = decoded_payload.get('sub')
print("did: ", did)
# The signature you want to verify
encoded = encode(['string'], [MESSAGE])
keccak_hash = Web3.keccak(encoded)
# The public key you want to use to verify the signature

print("account: ", Account._recover_hash(keccak_hash, signature=signature))