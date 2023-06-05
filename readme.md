# ARTIS rockpi logger

IoT device with the purpose of logging temperature and humidity data. It is programmed to store the collected data on a local database but sending any violations to the artis-apito be stored and recorded on the blockchain.

## Setup
1. connect device to power using usb-c port
2. connect device to a wifi network using a screen and keyboard or by connecting it to your computer using ethernet
3. establish a ssh session (rock@172.20.10.2) to start the logging script
4. execute the following commands
```bash
$ git clone https://github.com/artis-project/artis-rockpi-logger.git
$ cd artis-rockpi-logger
# edit the .env file and add all the necessary variables including
# the alert threshold for temperature and humidity in degrees celcius and percent respectively
$ pip install -r requirements.txt
$ sudo .venv/bin/python3 logging_script.py
# in a different terminal session
$ source .venv/bin/activate
$ python3 violation_script.py --temperature-threshold <celcius> --humidity-threshold <percentage>
``` 
