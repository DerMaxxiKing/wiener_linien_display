from wlan import WLANManager
from json import load
from wiener_linien_query_service import WienerLinienMonitor
from machine import WDT, deepsleep
import crowpanel


def main():
    
    # load config from file
    
    
    
    with open("config.json", "r") as file:
        config = load(file)
        
    wdt = WDT(timeout=int(config.get("wdt_interval", 6000)))
    wdt.feed()
    # wdt=None
        
    wlan_config = config.get("wlan", {})
    wlan_manager = WLANManager(
        ssid=wlan_config.get("ssid", "YourSSID"),
        password=wlan_config.get("password", "YourPassword"),
        timeout=int(wlan_config.get("timeout", 15)),
        wdt=wdt
    )
    
    wlan_manager.connect()
    if not wlan_manager.is_connected():
        print("Failed to connect to WLAN, entering deep sleep.")
        raise Exception("WLAN Connection Failed")
    
    print(f'Wlan is connected: {wlan_manager.is_connected()}, IP: {wlan_manager.get_ip()}')
    
    panel = crowpanel.CrowPanel42()
    
    
    # Replace with your desired station IDs (RBL numbers)
    station_ids = config.get("station_ids", [1444, 1478])
    monitor = WienerLinienMonitor(station_ids,
                                  wdt=wdt,
                                  panel=panel,
                                  wlan=wlan_manager,
                                  refresh_interval=int(config.get("update_interval", 60)))
    monitor.run()
    
    
if __name__ == "__main__":
    main()