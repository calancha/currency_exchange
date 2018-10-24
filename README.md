# Microservice to forge curency exchange API

Simple python script to make requests to the forge currency exchange service
https://1forge.com/forex-data-api/api-documentation#quotes

# Usage

```
python currency_exchange.py --pairs=XXXYYY --api_key=APIKEY --debug
```

APIKEY must be a valid key for the forge service.

The argument of --pairs must be a comma separated list of
supported currency pairs, e.g. EURUSD,JPYEUR.