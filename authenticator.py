import base64
from web3.eth.base_eth import Account
from eth_account.messages import encode_defunct
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast
from uuid import uuid4
import pytz
import json
from functools import wraps
import binascii
import requests


@dataclass
class LoginPayloadData:
    domain: str
    address: str
    nonce: str
    type: str
    version: str
    expiration_time: datetime
    issued_at: datetime
    statement: Optional[str] = None
    chain_id: Optional[int] = None

    @staticmethod
    def from_json(json: Dict[str, Any], timeformat: str) -> "LoginPayloadData":
        return LoginPayloadData(
            json["domain"],
            json["address"],
            json["nonce"],
            json["type"],
            json["version"],
            datetime.strptime(json["expiration_time"], timeformat),
            datetime.strptime(json["issued_at"], timeformat),
            json.get("statement"),
            json.get("chain_id"),
        )


class Authenticator:
    def __init__(
        self,
        signing_key: str,
        url: str,
        timeformat="%Y-%m-%dT%H:%M:%S%z",
    ):
        self._signing_key = signing_key
        self.url = url
        self.timeformat = timeformat
        self.signing_account = Account.from_key(signing_key)

    def login(self):
        # fetch login payload from artis-server
        response = requests.post(
            f"{self.url}/auth/payload",
            json={"address": self.signing_account.address, "chainId": 11155111},
        )
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} {response.json()}")
        payload = response.json()["payload"]
        # generate message
        message = self._generate_message(
            LoginPayloadData.from_json(payload, timeformat=self.timeformat)
        )
        # sign message
        signature = self._sign_message(message)
        # send login request
        response = requests.post(
            f"{self.url}/auth/login",
            json={
                "payload": {
                    "payload": payload,
                    "signature": signature,
                }
            },
        )
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} {response.json()}")
        return response.json()["token"]

    def _generate_message(self, payload) -> str:
        """
        Generates an EIP-4361 compliant message to sign based on the login payload
        """
        typeField = "Ethereum" if payload.type == "evm" else "Solana"
        header = f"{payload.domain} wants you to sign in with your {typeField} account:"
        prefix = f"{header}\n{payload.address}"
        if payload.statement:
            prefix += f"\n\n{payload.statement}\n"
        else:
            prefix += "\n\n"
        suffixArray = []
        versionField = f"Version: {payload.version}"
        suffixArray.append(versionField)
        if payload.chain_id:
            chainField = f"Chain ID: {payload.chain_id if payload.chain_id else str(1)}"
            suffixArray.append(chainField)
        nonceField = f"Nonce: {payload.nonce}"
        suffixArray.append(nonceField)
        time = payload.issued_at.strftime(self.timeformat)
        issuedAtField = f"Issued At: {time}"
        suffixArray.append(issuedAtField)
        time = payload.expiration_time.strftime(self.timeformat)
        expiryField = f"Expiration Time: {time}"
        suffixArray.append(expiryField)

        suffix = "\n".join(suffixArray)
        return f"{prefix}\n{suffix}"

    def _sign_message(self, message: str) -> str:
        """
        Sign a message with the admin wallet
        """

        message_hash = encode_defunct(text=message)
        sig = self.signing_account.sign_message(message_hash)
        return sig.signature.hex()
