from enum import Enum
import requests
import os
from eth_abi import encode
from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv
from pprint import pprint
from authenticator import Authenticator
import base64
import json
import datetime

load_dotenv()


class ViolationType(Enum):
    TEMPERATURE = 1
    HUMIDITY = 2


class ArtisAPI:
    def __init__(self, artwork_id: str):
        self.base_url = self.__getApiUrl()
        self.__signing_key = os.environ.get("ARTIS_LOGGER_SIGNING_KEY")
        self.artwork_id = artwork_id
        self.authenticator = Authenticator(self.__signing_key, self.base_url)

    def report_violation(
        self, timestamp: int, violationType: ViolationType, value: float
    ) -> None:
        # makin a patch request to the api
        url = f"{self.base_url}/artworks/{self.artwork_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__refresh_token()}",
        }
        data = {
            "violationTimestamp": timestamp,
        }
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code != 200:
            pprint(f"Error: {response.status_code} {response.json()}")
        else:
            print(f"Violation reported: {violationType.name} {value}")
            pprint(response.json())

    def __getApiUrl(self) -> str:
        """Get the api url from github actions secrets"""
        access_token = os.environ.get("GITHUB_VARIABLES_ACCESS_TOKEN")
        org_name = os.environ.get("GITHUB_ORG_NAME")
        variable_name = os.environ.get("GITHUB_ARTIS_API_URL_VARIABLE_NAME")
        url = (
            f"https://api.github.com/orgs/{org_name}/actions/variables/{variable_name}"
        )
        print(url)
        return (
            requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
            .json()
            .get("value")
        )

    def __refresh_token(self):
        get_exp = lambda token: json.loads(
            base64.b64decode(token.split(".")[1]).decode("utf-8")
        ).get("exp")
        token = os.environ.get("ARTIS_API_AUTH_TOKEN")
        if token is None or get_exp(token) < datetime.datetime.now().timestamp():
            os.environ["ARTIS_API_AUTH_TOKEN"] = self.authenticator.login()
        return os.environ.get("ARTIS_API_AUTH_TOKEN")
