"""
Program : Autonomous Environmental Safety Tiering (Climatic Logic Module)
Purpose : Classifies a human-robot collaborative work-site into one of four
          safety tiers using multi-signal telemetry condensed into a single
          derived quantity, the Heat Stress Index.
Author  : SOHAN SAHA
Date    : 21/08/2026
Course  : Coding for AI - Dr. Prateek, Problem Set 2.1 (Bonus)
"""

UNKNOWN_MESSAGE = "Safety Level: Unknown"

print("=== Autonomous Environmental Safety Tiering ===")

operator_id = input("Operator ID: ").strip() or "Guest_User"
print(f"Telemetry session opened by: {operator_id}")
if not (temp_str := input("Temperature (C): ").strip()):
    print(UNKNOWN_MESSAGE)
elif not (humidity_str := input("Humidity (%): ").strip()):
    print(UNKNOWN_MESSAGE)
elif not (wind_str := input("Wind speed (km/h): ").strip()):
    print(UNKNOWN_MESSAGE)
else:
    try:
        temperature = float(temp_str)
        humidity = float(humidity_str)
        wind_speed = float(wind_str)
    except ValueError:
        print(UNKNOWN_MESSAGE)
    else:
        assert humidity >= 0, "Telemetry Error: Negative Humidity"

        hsi = temperature + (0.5 * humidity)
        risk_label = "Safe" if hsi < 30 else "Unsafe"
        print(f"Derived Heat Stress Index: {hsi:.1f} ({risk_label})")
        if temperature <= 0:
            tier = "FREEZE ALERT"
        elif hsi > 45 or (temperature > 38 and humidity > 70):
            tier = "CRITICAL"
        elif hsi >= 30 and wind_speed < 5:
            tier = "CAUTIONARY"
            battery_str = input("Battery level (%): ").strip() or "50"
            try:
                battery_level = float(battery_str)
            except ValueError:
                battery_level = 50.0

            if battery_level < 20:
                tier = "CRITICAL"
                print("Battery low: robot failure risk in sustained heat.")
            elif battery_level > 80:
                tier = "OPERATIONAL"
                print("Battery ample: robots can sustain high-load cooling.")
            else:
                print("Battery nominal: tier unchanged.")
        else:
            tier = "OPERATIONAL"

        print(f"Safety Level: {tier}")
