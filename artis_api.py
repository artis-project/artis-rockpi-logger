from enum import Enum
import requests
import os
from eth_abi import encode
from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class ViolationType(Enum):
    TEMPERATURE = 1
    HUMIDITY = 2

class ArtisAPI:

    def __init__(self):
        self.base_url = os.environ.get('ARTIS_API_URL')
        self.__signing_key = os.environ.get('ARTIS_LOGGER_SIGNING_KEY')
        self.artwork_id = os.environ.get('ARTIS_LOGGER_ARTWORK_ID')
        self.logger_address = os.environ.get('ARTIS_LOGGER_ADDRESS')
        self.did = f'did:ethr:{self.logger_address}'
    

    def report_violation(self, timestamp: int, violationType: ViolationType, value: float) -> None:
        # makin a patch request to the api
        url = f'{self.base_url}/artworks/{self.artwork_id}'
        headers = {
            'Content-Type': 'application/json',
            'Did': self.did,
            'Signature': self._sign(self.did),
        }
        data = {
            'violationTimestamp': timestamp,
        }
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code != 200:
            pprint(f'Error: {response.status_code} {response.json()}')
        else:
            print(f'Violation reported: {violationType.name} {value}')
            pprint(response.json())


    def _sign(self, message: str) -> str:
        encoded = encode(['string'], [message])
        hashed = Web3.keccak(encoded)

        signed_message = Account.signHash(hashed, private_key=self.__signing_key)

        return signed_message.signature.hex()
