(
    {
        TARGET_SSID="YOUR_SSID_HERE"
        echo "$(date): Starting Wi-Fi recovery sequence for SSID: $TARGET_SSID"

        sleep 30

        echo "$(date): Bringing wlan0 up..."
        ifconfig wlan0 up

        echo "$(date): Scanning for Wi-Fi networks..."
        iwlist wlan0 scan > /tmp/scan_results 2>&1

        if grep -q "ESSID:\"$TARGET_SSID\"" /tmp/scan_results; then
            echo "$(date): Found SSID $TARGET_SSID, attempting connection..."

            echo "$(date): Starting wpa_supplicant..."
            wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant.conf -C /var/run/wpa_supplican

            sleep 5

            echo "$(date): Requesting IP with udhcpc..."
            udhcpc -i wlan0 >> /tmp/down_recovery.log 2>&1

            sleep 5

            CURRENT_SSID=$(wpa_cli -i wlan0 status | grep ^ssid= | cut -d= -f2)
        if [ "$CURRENT_SSID" = "$TARGET_SSID" ]; then
                echo "$(date): Successfully connected to $TARGET_SSID"
        else
                echo "$(date): Failed to connect to $TARGET_SSID, disabling Wi-Fi"
                ifconfig wlan0 down
        fi

        else
            echo "$(date): SSID $TARGET_SSID not found, disabling Wi-Fi"
            ifconfig wlan0 down
        fi
    } >> /tmp/down_recovery.log 2>&1
) &


exit 0
