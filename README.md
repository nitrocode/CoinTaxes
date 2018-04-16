# CoinTaxes

This will fill out IRS form 8949 for the following exchanges:

* Coinbase
* GDAX
* Bittrex data

It assumes all short term sales and will use the highest cost buy order for cost basis. This will lower the amount of taxes you will have to pay. It will make a .txf that you can import into TurboTax, and it will fill out the IRS form 8949. This has only been tested on Windows.

## Enhancements

This project was forked off of [CryptoTaxes](https://github.com/gsugar87/CryptoTaxes) by gsugar87.

* Cleaned up documentation
* Converted `credentials.py` to `config.yml`
* Fixed code
  * Updated old api functions to new ones
  * Added cross platform code so it works on Windows, OSX, and Linux
  * Made structure more flexible by adding exchanges package
  * Added code docs
* Renamed so pip package wouldn't confuse with the original project
* Added an open license
* See `TODO.md` for more details

## Dependencies

### pip dependencies

    pip install -r requirements.txt

### pdf toolkit

Install [pdftk](https://www.pdflabs.com/tools/pdftk-server/) from a binary and make sure the command `pdftk` is in the path.

If using Ubuntu it's easier to install.

    apt-get install pdftk 

## Instructions

Assuming you have API keys for the exchanges you want. Edit `config.yml` and uncomment the exchanges and insert keys, secrets, and passphrases. Fill out your name and social in the file to have that written into the PDF.

Then finally, Run the script

    python CoinTaxes.py

### Get the API credentials

#### Coinbase

1. Sign into your Coinbase account
2. Go to the [API page](https://www.coinbase.com/settings/api) and click on `New API Key`
3. In the popup window check `all` under Accounts:
    * `wallet:accounts:read`
    * `wallet:addresses:read`
    * `wallet:buys:read`
    * `wallet:deposits:read`
    * `wallet:sells:read`
    * `wallet:transactions:read`
    * `wallet:user:read`
4. Click Create to see the API key and secret.
5. Insert the API Key into the correct variables in `config.yml` e.g.

        coinbase:
            key: 'abcdefg1234'
            secret: 'zxcvbasdf1234qwer'

#### GDAX

1. Sign into GDAX
2. Go to [API page](https://www.gdax.com/settings/api) and under Permissions, check `View` and then click `Create API Key.`
3. Enter the two-factor authentication code if you are asked for it
4. Insert the API creds into the correct variables in `config.yml` e.g.
 
        gdax:
            key: 'qwerty123'
            secret: 'poiuyt999'
            passphrase: 'mnbvc000'

#### Bittrex

 Unfortunately, the Bittrex API does not let you get your entire transaction history via an API. In order to get your entire history, you must login to your Bittrex account, go to https://bittrex.com/History, and then click on "Load All."  This will download your entire history in a csv file called "fullOrders.csv". Move this file into the CryptoTaxes directory, and it will be read in.

# Donate

If you find this code useful, feel free to donate!

## me

* BTC: 1LENSt469CoAmZBp1zSvdbSKtCacjSez3i
* LTC: LbweDjdHMaHZJtkjmP11rpC7ftXYfFPKop
* ETH: 0x13fc2D16fC97877Cf6C35A56F8d2e646152cc2e6
* Doge: AEztxkBZ1qBDrye6o3UYphRWPNQHDUYmoW
* BCH: qrf0rve9wjajr4g8h24ed3ff9kx0zqn86vlvmkyn7g

## gsugar87

Original developer's crypto wallets are at the [bottom of his repo](https://github.com/gsugar87/CryptoTaxes).
