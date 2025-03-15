import time
import pywifi
from pywifi import const

def start_wifi_direct(ssid="PlaylistShare"):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    iface.disconnect()
    time.sleep(1) # To disconnect

    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = "12345678"

    iface.remove_all_network_profiles()
    temp_profile = iface.add_network_profile(profile)

    iface.connect(temp_profile) # Start Wi-Fi Direct
    time.sleep(5)

    print(f"Wi-Fi Direct '{ssid}' started successfully.")

start_wifi_direct()