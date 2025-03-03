import time
import pywifi
from pywifi import const
import urllib.request

def startWifiConnection(wifi_ssid,wifi_pw,deviceNum):

    pywifi.set_loglevel('DEBUG')

    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]

    iface.scan_results()

    iface.disconnect()
    time.sleep(1)
    assert iface.status() in\
        [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]

    profile = pywifi.Profile()
    profile.ssid = 'RUNCODING_'+str(deviceNum)
    # profile.auth = const.AUTH_ALG_OPEN
    # profile.akm.append(const.AKM_TYPE_WPA2PSK)
    # profile.cipher = const.CIPHER_TYPE_CCMP
    # profile.key = '12345678'

    # iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)

    # just 10 trying...
    conn = 0
    while iface.status() != const.IFACE_CONNECTED:
        conn = conn + 1
        iface.connect(tmp_profile)
        time.sleep(1)
        if conn == 10:
            print("wifi connecting failure")
            iface.disconnect()
            return conn
    # assert iface.status() == const.IFACE_CONNECTED

    resultUrl = "http://192.168.4.1/control?var=framesize&val=7"
    resultOpen = urllib.request.urlopen(resultUrl)
    readdata = resultOpen.read()
    print("[3] wifi connecting.. :".format(readdata))
    resultOpen.close()

    if wifi_pw == "":
        return "192.168.4.1"

    resultUrl = "http://192.168.4.1/control?var=pw&val=" + wifi_pw

    try:
        resultOpen = urllib.request.urlopen(resultUrl)
    except urllib.error.URLError as e:
        print("ERROR : ", e)
        return 10

    readdata=resultOpen.read()
    print("[1] wifi connecting.. :".format(readdata))
    resultOpen.close()
    resultUrl ="http://192.168.4.1/control?var=ssid&val="+ wifi_ssid
    resultOpen = urllib.request.urlopen(resultUrl)
    readdata=resultOpen.read()
    print("[2] wifi connecting.. :".format(readdata))
    resultOpen.close()



    conn = 0
    while True:
        resultUrl ="http://192.168.4.1/control?var=gip&val=RUNCODING"
        resultOpen = urllib.request.urlopen(resultUrl)
        readdata=resultOpen.read()
        readdata=readdata.decode('utf-8')
        print("[3] wifi connecting.. : " + readdata)
        resultOpen.close()
        if readdata == 'NOK':
            conn = conn + 1
            time.sleep(1)
            if conn == 10:
                print("wifi connecting control failure")
                iface.disconnect()
                return conn
            continue
        break

    iface.disconnect()

    profile = pywifi.Profile()

    profile.ssid = wifi_ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = wifi_pw

    tmp_profile = iface.add_network_profile(profile)

    conn = 0
    while True:
        conn = conn + 1
        iface.connect(tmp_profile)
        time.sleep(3)
        if iface.status() == const.IFACE_CONNECTED:
            break


        if conn == 10:
            print("Wifi Connecting Rollback Failure")
            iface.disconnect()
            return conn

    return readdata
