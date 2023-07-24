# artis-rockpi-logger

The artis-rockpi-logger repository contains the code to be run on a rockpi equipped with a DHT-22 sensor. The sensor is responsible for recording temperature and humidity data as well as reporting any violation of a specified threshold to the *artis-server* via a API call.

## External services setup

### Metamask accounts & wallets

[metamask](https://metamask.io/) is a web3 wallet provider that simplifies blockchain wallet and account creation. For this project we need multiple accounts that are easily created with metamask.

- Sign up for metamask
- create accounts for
    - the smartcontract admin
    - the logger
- note the private key for later

### Github Variables

Because the services in this project are intertwined we use github variables at an organization level to share two pieces of information. Firstly the address of the deployed smartcontract that is consumed by the *artis-server* to interact with the newest deployed contract and secondly the API url of the deployed *artis-server* instance that is consumed by the *artis-rockpi-logger* in order to query the newest version of the deployed REST API.

To create or update these variables manually:

```bash
gh variable set ARTIS_API_URL --org artis-project
gh variable set ARTIS_SC_ADDRESS --org artis-project
```

In our CI/CD setup these variables are updated (automatically) and queried by each service independently. In order to authenticate we are using personal access tokens:

- create a fine-grained personal access token to allow reading and writing to variables (if you want you can seperate read and write into two tokens)
    - to allow personal access tokens: artis-project > settings > Third-party Access > Personal access tokens > Allow access via fine-grained access tokens > do not require administrator approval > Allow access via personal access tokens (classic) > enroll
        - or ask an administrator to do this for you
    - to create: <your github account> > settings > Developer settings > Personal access tokens > Fine-grained tokens > generate new token
        - name: ACCESS_ARTIS_ORG_VARIABLES
        - Resource owner: artis-project
        - Permissions > Organizations permissions > Variables > Read and write
        - generate token and note for later



## Development
In order to run and deploy this code we need access to a couple of secrets that are currently stored as an environment variable.
`.env`
---
ARTIS_LOGGER_SIGNING_KEY = \<logger-private-key\> *(0x prefix!)*

GITHUB_ARTIS_API_URL_VARIABLE_NAME = “ARTIS_API_URL”

GITHUB_ORG_NAME = “artis-project”

GITHUB_VARIABLES_ACCESS_TOKEN = \<personal access token to read org variables\>

---

After connecting to the rockpi via ssh and cloning the repository, the code dependencies are defined in the requirements.txt file and the Rockfruit_Python_DHT folder. They can be installed with this command:

```bash
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
## slightly adapted repository from Tim Parbs (originally from Tony DiCola)
cd Rockfruit_Python_DHT
sudo python3 setup.py install
```

## Starting the logging script

The logging script can be started with this command:

```bash
sudo .venv/bin/python3 logging_script.py
```

This script records and stores valid readings in a local database. To detect and report any violations a different script is run simultaneously.

```bash
source ./.venv/bin/activate
python3 violation_script.py --temperature-threshold <celcius> --humidity-threshold <percent>
```

## Learn More
If you want to know more about the project check out the full project report in the [artis-thesis](https://github.com/artis-project/artis-thesis) repository
