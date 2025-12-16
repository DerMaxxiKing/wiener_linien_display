import requests
import machine
import crowpanel
import time
from wlan import WLANManager
import gc

# import datetime

rtc = machine.RTC()


class WienerLinienMonitor:
    BASE_URL = "https://www.wienerlinien.at/ogd_realtime/monitor"

    def __init__(self, 
                 station_ids,
                 wlan: WLANManager,
                 wdt:machine.WDT = None,
                 panel:crowpanel.CrowPanel42 = None,
                 refresh_interval:int=60):
        """
        station_ids: list of integers or strings (RBL numbers)
        wdt: optional watchdog timer to feed during long operations
        """
        self.station_ids = station_ids if isinstance(station_ids, list) else [station_ids]
        self.wdt = wdt
        self.wlan = wlan
        self.panel = panel
        if self.panel:
            self.display = panel.get_display()
            self.display.fill(1)  # Clear display (assuming 1 is white)
            self.display.text("Wiener Linien Monitor - initializing", 5, 5, 0)
            self.display.show()
            
        self.refresh_interval = refresh_interval  # seconds
        self.get_time()
        
        self.departures = {}
        gc.collect()
        

    def get_time(self):
        try:
            print("Synchronizing time with NTP server...")
            import ntptime
            ntptime.settime()
            time.sleep(2)
            print("Local time after synchronization：%s" %str(time.localtime()))
        except Exception as e:
            print(f"Error syncing time: {e}")
            
    def get_current_time(self, as_str:bool=False):
        if as_str:
            c_time = time.localtime()
            return f'{c_time[2]}.{c_time[1]}.{c_time[0]} {c_time[3]:02}:{c_time[4]:02}:{c_time[5]:02}'
        else:
            return time.localtime()

    def fetch_departures(self, station_id):
        response = requests.get(self.BASE_URL + f'?rbl={station_id}', timeout=10)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        else:
            print(f"Fetching data for station ID {station_id}: {response.status_code}")
        if self.wdt:
            self.wdt.feed()
        return response.json()

    def parse_departures(self, data):
        monitors = data.get('data', {}).get('monitors', [])
        for monitor in monitors:
            stop_name = monitor.get('locationStop', {}).get('properties', {}).get('title', 'Unknown')
            
            if stop_name not in self.departures.keys():
                self.departures[stop_name] = {}
            
            for line in monitor.get('lines', []):
                line_name = line.get('name', 'Unknown')
                towards = line.get('towards', 'Unknown')
                
                if line_name not in self.departures[stop_name].keys():
                    self.departures[stop_name][line_name] = {}
                    
                if towards not in self.departures[stop_name][line_name].keys():
                    self.departures[stop_name][line_name][towards] = []
                
                for dep in line.get('departures', {}).get('departure', []):
                    planned = dep.get('departureTime', {}).get('timePlanned')
                    real = dep.get('departureTime', {}).get('timeReal')
                    countdown = dep.get('departureTime', {}).get('countdown')
                    self.departures[stop_name][line_name][towards].append({
                        'planned': self._format_time(planned),
                        'real': self._format_time(real),
                        'countdown': countdown
                    })

    def _format_time(self, timestr):
        if not timestr:
            return None
        # API returns ISO8601 format, e.g., "2024-06-01T12:34:00Z"
        try:
            # dt = datetime.fromisoformat(timestr.replace('Z', '+00:00'))
            # return dt.strftime('%H:%M:%S')
            return timestr
        except Exception:
            return timestr

    def display_departures(self):
        
        self.display.fill(1)  # Clear display (assuming 1 is white)
        if self.departures is None:
            self.departures = {}
            
        self.display.text(self.get_current_time(as_str=True), 5, 5, 0)
        
        y = 25
        
        for station, lines in self.departures.items():
            
            if not lines:
                continue
            
            self.display.text(station, 0, y, 0)
            y += 20
            
            for line, towardss in lines.items():
                for towards, deps in towardss.items():
                    dep_times = ', '.join(f"{dep['countdown']}" for dep in deps)
                    if len(towards) > 14:
                        towards = towards[:13] + '.'
                    display_text = f'{line} -> {towards}: {dep_times}'
                    print(display_text)
                    if len(display_text) > 50:
                        display_text = display_text[:37] + '...'
                    
                    self.display.text(display_text, 0, y, 0)
                    y += 20
            y += 10  # Extra space between stations
            
        self.departures = {}
        
        self.display.show()
        # self.display.sleep()
        print("Departures displayed on panel.")
        gc.collect()

    def run(self):
        while True:
            
            self.departures = {}
            
            for station_id in self.station_ids:
                print(f'\nDepartures for station ID {station_id}:')
                try:
                    print(f'Current time: {self.get_current_time(as_str=True)}')
                except Exception as e:
                    print(f'Error getting current time: {e}')
                    
                try:
                    if self.wlan and not self.wlan.is_connected():
                        print("WLAN not connected, attempting to reconnect...")
                        if not self.wlan.reconnect():
                            print("Failed to reconnect to WLAN.")
                            continue
                    
                    data = self.fetch_departures(station_id)
                    self.parse_departures(data)
                    gc.collect()
                except Exception as e:
                    print(f"  Error fetching data for station {station_id}: {e}")
                
            if self.display:
                try:
                    self.display_departures()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error displaying departures: {e}")
                    
            if self.wdt:
                self.wdt.feed()
            print(f"\nSleeping for {self.refresh_interval} seconds...\n")
            
            if self.refresh_interval >= 60:
                machine.lightsleep(self.refresh_interval * 1000)  # Sleep for refresh_interval seconds
            else:
                time.sleep(self.refresh_interval)
            if self.wdt:
                self.wdt.feed()
    