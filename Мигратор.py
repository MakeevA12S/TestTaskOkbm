import json
import os
def convert_mac(mac_int_str):
    try:
        mac_int = int(mac_int_str)
        mac_hex = hex(mac_int)[2:].zfill(12).upper()
        return ':'.join(mac_hex[i:i+2] for i in range(0, 12, 2))
    except ValueError:
        return None
def parse_dhcp_dump(filepath):
    kea_config = {"Dhcp4": {"subnet4": []}}
    reserves = {}
    subnets = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except Exception as e:
        return {"error": f"Error reading file: {e}"}
    for line in lines:
        tokens = line.strip().split()
        if tokens.__contains__("reservedip"):
            subnet = tokens[tokens.index("Scope")+1]
            if subnet in reserves:
                reserves[subnet].append((tokens[tokens.index("reservedip")+1], convert_mac(tokens[tokens.index("reservedip")+2])))
            else:
                reserves[subnet] = [(tokens[tokens.index("reservedip")+1], convert_mac(tokens[tokens.index("reservedip")+2]))]
        elif tokens.__contains__("iprange"):
            subnet = tokens[tokens.index("Scope")+1]
            subnets[subnet] = (tokens[tokens.index("iprange")+1], tokens[tokens.index("iprange")+2]) 
    for k in subnets:
        reservsPart = []
        key = k
        key = key[0:-1] + "1"
        if key in reserves:
          llll = reserves[key]
          for r in llll:
              reservsPart.append({"hw-address": r[1], "ip-address" : r[0]})
        poool = {  
            "start": subnets[k][0],
            "end": subnets[k][1]
        }
        kea_config["Dhcp4"]["subnet4"].append({"pools": [{"pool": poool}], "reservations": reservsPart})
    return kea_config
filepath = input("Enter the full path to the DHCP dump file (e.g., C:/DHCP/dump): ")
result = parse_dhcp_dump(filepath)
if "error" in result:
    print(result["error"])
else:
    try:
        with open("res.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Successfully saved to res.json")
    except Exception as e:
        print(f"Error saving to res.json: {e}")