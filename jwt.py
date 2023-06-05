import base64
import datetime

from eth_abi.abi import encode
from eth_account import Account
from web3 import Web3
import json

def encode_dict_base64(data: dict):
    return base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")

def issue_token(private_key: str):
  """issue a jwt token signed with the private key of the user"""
  if private_key is None:
    raise ValueError("missing private key")
  try:
    subject = Account.from_key(private_key)
  except Exception:
    raise ValueError("invalid private key")
  timestamp = datetime.datetime.now().timestamp()
  payload = {
    "iss": "ARTIS-Project",
    "sub": f"did:ethr:{subject.address}",
    "aud": "ARTIS-API",
    "iat": timestamp,
    "exp": timestamp + 3600,
  }
  header = {"alg": "ECDSA", "typ": "JWT"}

  base64_header = encode_dict_base64(header)
  base64_payload = encode_dict_base64(payload)

  signature_data = f"{base64_header}.{base64_payload}"

  encoded = encode(["string"], [signature_data])
  hashed = Web3.keccak(encoded)
  signature = subject.signHash(hashed).signature.hex()
  print(type(signature))
  signature = base64.b64encode(
    subject.signHash(hashed).signature.hex().encode("utf-8")
  ).decode("utf-8")

  token = ".".join([base64_header, base64_payload, signature])
  return token