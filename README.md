Show Wiener Linien depature times.

Edit the config.json file with your data:

update_interval: how often is the data updated and display refreshed in [s]
wlan: wland configuration
wdt_interval: Watchdogtimer interval in [s] - should be larger than the refresh interval
station_ids: List of station ids. See resources->wienerlinien-ogd-linien.csv

{
  "station_ids": [
    1444,
    1478,
    1477,
    1550,
    462,
    485,
    535,
    541,
    1445,
    1550
  ],
  "update_interval": 45,
  "wlan": {
    "ssid": "MyNetworkSSID",
    "password": "MySecurePassword",
    "timeout": 60,
    "reconnect_interval": 300,
    "max_retries": 100
  },
  "wdt_interval": 50000
}
