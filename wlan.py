import network
import time
from machine import WDT, idle

CURSOR_UP_ONE = '\x1b[1A' 
ERASE_LINE = '\x1b[2K' 


class WLANManager:
    def __init__(self, 
                 ssid: str, 
                 password: str, 
                 timeout: int = 10,
                 wdt: WDT = None):
        """
        Initialize WLAN manager
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            timeout: Connection timeout in seconds
        """
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.wlan = network.WLAN(network.STA_IF)
        self.wdt = wdt
    
    def connect(self):
        """Connect to WiFi network"""
        print("Starting WLAN connection...")
        print(f"SSID: {self.ssid}, password: {'*' * len(self.password)}")
        
        self.wlan.active(False)
        time.sleep(1)
        self.wlan.active(True)
        
        if self.wlan.isconnected():
            print("Already connected")
            return True
        
        print(f"Connecting to {self.ssid}...")
        self.wlan.connect(self.ssid, self.password)
        
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > self.timeout:
                print("Connection timeout")
                return False
            if self.wdt:
                self.wdt.feed()
            print(f'Waiting for connection... {int(time.time() - start_time)}s elapsed', end="\r")
            idle()
        
        print("Connected!")
        print(f"IP: {self.wlan.ifconfig()[0]}")
        return True
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
            print("Disconnected")
        self.wlan.active(False)
    
    def is_connected(self):
        """Check if connected to WiFi"""
        return self.wlan.isconnected()
    
    def get_ip(self):
        """Get IP address"""
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[0]
        return None
    
    def reconnect(self):
        """Reconnect to WiFi"""
        self.disconnect()
        time.sleep(1)
        ret_code = self.connect()
        time.sleep(0.5)
        return ret_code