#!/usr/bin/env bash
# nef_db_init.sh — Initializes the NEF Emulator for the Vehicle Crash Detection PoC.
#
# Monitoring zone: 37.9975–38.0005°N, 23.8185–23.8215°E
# Creates:
#   - 5 cars           (car-1 to car-5),             speed: HIGH
#   - 1 static camera  (scamera-1),                  speed: STATIONARY
#   - 1 dynamic camera (dcamera-1),                  speed: HIGH
#   - 20 pedestrians   (pedestrian-1 to -20),        speed: LOW

NEF_URL="http://localhost"
NEF_PORT=8888
NEF_USER="admin@my-email.com"
NEF_PASSWORD="pass"

# automatically export all variables
set -a
source .env
set +a

# help
for arg in "$@"; do
  if [ "$arg" == "--help" ]; then
    echo "Usage: $0 [-h NEF_URL] [-p NEF_PORT] [-u NEF_USER] [-s NEF_PASSWORD] [--help]"
    exit 0
  fi
done

# get opts
while getopts ":h:p:u:s:" opt; do
  case ${opt} in
    h ) NEF_URL=$OPTARG ;;
    p ) NEF_PORT=$OPTARG ;;
    u ) NEF_USER=$OPTARG ;;
    s ) NEF_PASSWORD=$OPTARG ;;
    \? )
      echo "Invalid option: -$OPTARG" >&2
      echo "Usage: $0 [-h NEF_URL] [-p NEF_PORT] [-u NEF_USER] [-s NEF_PASSWORD] [--help]"
      exit 1
      ;;
  esac
done

BASE="${NEF_URL}:${NEF_PORT}/api/v1"

printf '\n==================================================\n'
printf 'Obtaining access token...'
printf '\n==================================================\n'

TOKEN=$(curl -s -X POST "${BASE}/login/access-token" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=${NEF_USER}" \
  --data-urlencode "password=${NEF_PASSWORD}" \
  -d 'grant_type=&scope=&client_id=&client_secret=' \
  | jq -r '.access_token')

printf '\n%s\n' "${TOKEN}"

H=(-H 'accept: application/json' -H "Authorization: Bearer ${TOKEN}" -H 'Content-Type: application/json')


# ==================================================
# gNB
# ==================================================

printf '\n==================================================\ngNB\n==================================================\n'

curl -s -X POST "${BASE}/gNBs" "${H[@]}" -d '{
  "gNB_id": "AAAAA1",
  "name": "gNB1",
  "description": "This is a base station",
  "location": "unknown"
}'
printf '\n'


# ==================================================
# Cell: Institute of Informatics and Telecommunications
# ==================================================

printf '\n==================================================\nCell: Institute of Informatics and Telecommunications\n==================================================\n'

curl -s -X POST "${BASE}/Cells" "${H[@]}" -d '{
  "cell_id": "AAAAA1003",
  "name": "cell3",
  "description": "Institute of Informatics and Telecommunications",
  "gNB_id": 1,
  "latitude": 37.996136,
  "longitude": 23.818535,
  "radius": 100
}'
printf '\n'


# ==================================================
# Application
# ==================================================

printf '\n==================================================\nApplication\n==================================================\n'

curl -s -X POST "${BASE}/applications" "${H[@]}" -d '{
  "app_id": "vehicleCrashDetection",
  "ip_address_v4": "10.0.0.100",
  "mac_address": "22-00-00-00-00-64",
  "description": "Vehicle Crash Detection PoC application"
}'
printf '\n'


# ==================================================
# scamera-1
# ==================================================

printf '\n==================================================\nscamera-1\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000006",
  "name": "scamera-1",
  "description": "Static Camera UE",
  "gNB_id": 1,
  "Cell_id": 6,
  "ip_address_v4": "10.0.0.6",
  "ip_address_v6": "0:0:0:0:0:0:0:6",
  "mac_address": "22-00-00-00-00-06",
  "msisdn": "2020100000006",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10006@poc.com",
  "speed": "STATIONARY"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "scamera-1: fixed position at monitoring zone NW corner",
  "points": [{"latitude":"38.0005","longitude":"23.8185"},{"latitude":"38.0005","longitude":"23.8186"}],
  "start_point": {"latitude": 38.0005, "longitude": 23.8185},
  "end_point":   {"latitude": 38.0005, "longitude": 23.8186},
  "color": "#00cc00"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000006", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# dcamera-1
# ==================================================

printf '\n==================================================\ndcamera-1\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000007",
  "name": "dcamera-1",
  "description": "Dynamic Camera UE",
  "gNB_id": 1,
  "Cell_id": 7,
  "ip_address_v4": "10.0.0.7",
  "ip_address_v6": "0:0:0:0:0:0:0:7",
  "mac_address": "22-00-00-00-00-07",
  "msisdn": "2020100000007",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10007@poc.com",
  "speed": "HIGH"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "dcamera-1: patrol along northern edge of monitoring zone",
  "points": [{"latitude":"38.0005","longitude":"23.8185"},{"latitude":"38.0005","longitude":"23.8195"},{"latitude":"38.0005","longitude":"23.8205"},{"latitude":"38.0005","longitude":"23.8215"},{"latitude":"37.9995","longitude":"23.8215"},{"latitude":"37.9985","longitude":"23.8215"},{"latitude":"37.9975","longitude":"23.8215"}],
  "start_point": {"latitude": 38.0005, "longitude": 23.8185},
  "end_point":   {"latitude": 37.9975, "longitude": 23.8215},
  "color": "#0066cc"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000007", "path": '"${PATH_ID}"'}'
printf '\n'



# ==================================================
# car-1
# ==================================================

printf '\n==================================================\ncar-1\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000001",
  "name": "car-1",
  "description": "Car UE",
  "gNB_id": 1,
  "Cell_id": 1,
  "ip_address_v4": "10.0.0.1",
  "ip_address_v6": "0:0:0:0:0:0:0:1",
  "mac_address": "22-00-00-00-00-01",
  "msisdn": "2020100000001",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10001@poc.com",
  "speed": "HIGH"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "car-1: E-W main road through monitoring zone",
  "points": [{"latitude":"37.9990","longitude":"23.8150"},{"latitude":"37.9990","longitude":"23.8170"},{"latitude":"37.9990","longitude":"23.8190"},{"latitude":"37.9990","longitude":"23.8210"},{"latitude":"37.9990","longitude":"23.8230"},{"latitude":"37.9990","longitude":"23.8250"}],
  "start_point": {"latitude": 37.9990, "longitude": 23.8150},
  "end_point":   {"latitude": 37.9990, "longitude": 23.8250},
  "color": "#cc0000"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000001", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# car-2
# ==================================================

printf '\n==================================================\ncar-2\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000002",
  "name": "car-2",
  "description": "Car UE",
  "gNB_id": 1,
  "Cell_id": 2,
  "ip_address_v4": "10.0.0.2",
  "ip_address_v6": "0:0:0:0:0:0:0:2",
  "mac_address": "22-00-00-00-00-02",
  "msisdn": "2020100000002",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10002@poc.com",
  "speed": "HIGH"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "car-2: N-S main road through monitoring zone",
  "points": [{"latitude":"37.9960","longitude":"23.8200"},{"latitude":"37.9975","longitude":"23.8200"},{"latitude":"37.9990","longitude":"23.8200"},{"latitude":"38.0005","longitude":"23.8200"},{"latitude":"38.0020","longitude":"23.8200"},{"latitude":"38.0035","longitude":"23.8200"}],
  "start_point": {"latitude": 37.9960, "longitude": 23.8200},
  "end_point":   {"latitude": 38.0035, "longitude": 23.8200},
  "color": "#cc0000"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000002", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# car-3
# ==================================================

printf '\n==================================================\ncar-3\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000003",
  "name": "car-3",
  "description": "Car UE",
  "gNB_id": 1,
  "Cell_id": 3,
  "ip_address_v4": "10.0.0.3",
  "ip_address_v6": "0:0:0:0:0:0:0:3",
  "mac_address": "22-00-00-00-00-03",
  "msisdn": "2020100000003",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10003@poc.com",
  "speed": "HIGH"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "car-3: E-W southern road through monitoring zone",
  "points": [{"latitude":"37.9975","longitude":"23.8150"},{"latitude":"37.9975","longitude":"23.8170"},{"latitude":"37.9975","longitude":"23.8190"},{"latitude":"37.9975","longitude":"23.8210"},{"latitude":"37.9975","longitude":"23.8230"},{"latitude":"37.9975","longitude":"23.8250"}],
  "start_point": {"latitude": 37.9975, "longitude": 23.8150},
  "end_point":   {"latitude": 37.9975, "longitude": 23.8250},
  "color": "#cc0000"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000003", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# car-4
# ==================================================

printf '\n==================================================\ncar-4\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000004",
  "name": "car-4",
  "description": "Car UE",
  "gNB_id": 1,
  "Cell_id": 4,
  "ip_address_v4": "10.0.0.4",
  "ip_address_v6": "0:0:0:0:0:0:0:4",
  "mac_address": "22-00-00-00-00-04",
  "msisdn": "2020100000004",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10004@poc.com",
  "speed": "HIGH"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "car-4: N-S eastern road through monitoring zone",
  "points": [{"latitude":"37.9960","longitude":"23.8225"},{"latitude":"37.9975","longitude":"23.8225"},{"latitude":"37.9990","longitude":"23.8225"},{"latitude":"38.0005","longitude":"23.8225"},{"latitude":"38.0020","longitude":"23.8225"},{"latitude":"38.0035","longitude":"23.8225"}],
  "start_point": {"latitude": 37.9960, "longitude": 23.8225},
  "end_point":   {"latitude": 38.0035, "longitude": 23.8225},
  "color": "#cc0000"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000004", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# car-5
# ==================================================

printf '\n==================================================\ncar-5\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000005",
  "name": "car-5",
  "description": "Car UE",
  "gNB_id": 1,
  "Cell_id": 5,
  "ip_address_v4": "10.0.0.5",
  "ip_address_v6": "0:0:0:0:0:0:0:5",
  "mac_address": "22-00-00-00-00-05",
  "msisdn": "2020100000005",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10005@poc.com",
  "speed": "HIGH"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "car-5: diagonal NW-SE road through monitoring zone",
  "points": [{"latitude":"37.9965","longitude":"23.8170"},{"latitude":"37.9975","longitude":"23.8180"},{"latitude":"37.9985","longitude":"23.8190"},{"latitude":"37.9995","longitude":"23.8200"},{"latitude":"38.0005","longitude":"23.8210"},{"latitude":"38.0015","longitude":"23.8220"},{"latitude":"38.0025","longitude":"23.8230"}],
  "start_point": {"latitude": 37.9965, "longitude": 23.8170},
  "end_point":   {"latitude": 38.0025, "longitude": 23.8230},
  "color": "#cc0000"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000005", "path": '"${PATH_ID}"'}'
printf '\n'



# ==================================================
# pedestrian-1
# ==================================================

printf '\n==================================================\npedestrian-1\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000008",
  "name": "pedestrian-1",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 8,
  "ip_address_v4": "10.0.0.8",
  "ip_address_v6": "0:0:0:0:0:0:0:8",
  "mac_address": "22-00-00-00-00-08",
  "msisdn": "2020100000008",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10008@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-1: approaching monitoring zone from west",
  "points": [{"latitude":"37.9985","longitude":"23.8155"},{"latitude":"37.9986","longitude":"23.8165"},{"latitude":"37.9987","longitude":"23.8175"},{"latitude":"37.9988","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9985, "longitude": 23.8155},
  "end_point":   {"latitude": 37.9988, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000008", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-2
# ==================================================

printf '\n==================================================\npedestrian-2\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000009",
  "name": "pedestrian-2",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 9,
  "ip_address_v4": "10.0.0.9",
  "ip_address_v6": "0:0:0:0:0:0:0:9",
  "mac_address": "22-00-00-00-00-09",
  "msisdn": "2020100000009",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10009@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-2: approaching monitoring zone from west",
  "points": [{"latitude":"37.9990","longitude":"23.8155"},{"latitude":"37.9990","longitude":"23.8165"},{"latitude":"37.9990","longitude":"23.8175"},{"latitude":"37.9990","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9990, "longitude": 23.8155},
  "end_point":   {"latitude": 37.9990, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000009", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-3
# ==================================================

printf '\n==================================================\npedestrian-3\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000010",
  "name": "pedestrian-3",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 10,
  "ip_address_v4": "10.0.0.10",
  "ip_address_v6": "0:0:0:0:0:0:0:a",
  "mac_address": "22-00-00-00-00-0a",
  "msisdn": "2020100000010",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10010@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-3: approaching monitoring zone from west",
  "points": [{"latitude":"37.9995","longitude":"23.8155"},{"latitude":"37.9995","longitude":"23.8165"},{"latitude":"37.9995","longitude":"23.8175"},{"latitude":"37.9995","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9995, "longitude": 23.8155},
  "end_point":   {"latitude": 37.9995, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000010", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-4
# ==================================================

printf '\n==================================================\npedestrian-4\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000011",
  "name": "pedestrian-4",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 11,
  "ip_address_v4": "10.0.0.11",
  "ip_address_v6": "0:0:0:0:0:0:0:b",
  "mac_address": "22-00-00-00-00-0b",
  "msisdn": "2020100000011",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10011@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-4: approaching monitoring zone from west",
  "points": [{"latitude":"37.9980","longitude":"23.8155"},{"latitude":"37.9981","longitude":"23.8165"},{"latitude":"37.9982","longitude":"23.8175"},{"latitude":"37.9983","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9980, "longitude": 23.8155},
  "end_point":   {"latitude": 37.9983, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000011", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-5
# ==================================================

printf '\n==================================================\npedestrian-5\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000012",
  "name": "pedestrian-5",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 12,
  "ip_address_v4": "10.0.0.12",
  "ip_address_v6": "0:0:0:0:0:0:0:c",
  "mac_address": "22-00-00-00-00-0c",
  "msisdn": "2020100000012",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10012@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-5: approaching monitoring zone from west",
  "points": [{"latitude":"38.0000","longitude":"23.8155"},{"latitude":"38.0000","longitude":"23.8165"},{"latitude":"38.0000","longitude":"23.8175"},{"latitude":"38.0000","longitude":"23.8185"}],
  "start_point": {"latitude": 38.0000, "longitude": 23.8155},
  "end_point":   {"latitude": 38.0000, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000012", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-6
# ==================================================

printf '\n==================================================\npedestrian-6\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000013",
  "name": "pedestrian-6",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 13,
  "ip_address_v4": "10.0.0.13",
  "ip_address_v6": "0:0:0:0:0:0:0:d",
  "mac_address": "22-00-00-00-00-0d",
  "msisdn": "2020100000013",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10013@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-6: approaching monitoring zone from north",
  "points": [{"latitude":"38.0025","longitude":"23.8195"},{"latitude":"38.0018","longitude":"23.8197"},{"latitude":"38.0011","longitude":"23.8199"},{"latitude":"38.0005","longitude":"23.8200"}],
  "start_point": {"latitude": 38.0025, "longitude": 23.8195},
  "end_point":   {"latitude": 38.0005, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000013", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-7
# ==================================================

printf '\n==================================================\npedestrian-7\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000014",
  "name": "pedestrian-7",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 14,
  "ip_address_v4": "10.0.0.14",
  "ip_address_v6": "0:0:0:0:0:0:0:e",
  "mac_address": "22-00-00-00-00-0e",
  "msisdn": "2020100000014",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10014@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-7: approaching monitoring zone from north",
  "points": [{"latitude":"38.0025","longitude":"23.8200"},{"latitude":"38.0018","longitude":"23.8200"},{"latitude":"38.0011","longitude":"23.8200"},{"latitude":"38.0005","longitude":"23.8200"}],
  "start_point": {"latitude": 38.0025, "longitude": 23.8200},
  "end_point":   {"latitude": 38.0005, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000014", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-8
# ==================================================

printf '\n==================================================\npedestrian-8\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000015",
  "name": "pedestrian-8",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 15,
  "ip_address_v4": "10.0.0.15",
  "ip_address_v6": "0:0:0:0:0:0:0:f",
  "mac_address": "22-00-00-00-00-0f",
  "msisdn": "2020100000015",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10015@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-8: approaching monitoring zone from north",
  "points": [{"latitude":"38.0025","longitude":"23.8205"},{"latitude":"38.0018","longitude":"23.8203"},{"latitude":"38.0011","longitude":"23.8201"},{"latitude":"38.0005","longitude":"23.8200"}],
  "start_point": {"latitude": 38.0025, "longitude": 23.8205},
  "end_point":   {"latitude": 38.0005, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000015", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-9
# ==================================================

printf '\n==================================================\npedestrian-9\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000016",
  "name": "pedestrian-9",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 16,
  "ip_address_v4": "10.0.0.16",
  "ip_address_v6": "0:0:0:0:0:0:0:10",
  "mac_address": "22-00-00-00-00-10",
  "msisdn": "2020100000016",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10016@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-9: approaching monitoring zone from north",
  "points": [{"latitude":"38.0025","longitude":"23.8210"},{"latitude":"38.0018","longitude":"23.8208"},{"latitude":"38.0011","longitude":"23.8204"},{"latitude":"38.0005","longitude":"23.8200"}],
  "start_point": {"latitude": 38.0025, "longitude": 23.8210},
  "end_point":   {"latitude": 38.0005, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000016", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-10
# ==================================================

printf '\n==================================================\npedestrian-10\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000017",
  "name": "pedestrian-10",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 17,
  "ip_address_v4": "10.0.0.17",
  "ip_address_v6": "0:0:0:0:0:0:0:11",
  "mac_address": "22-00-00-00-00-11",
  "msisdn": "2020100000017",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10017@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-10: approaching monitoring zone from north",
  "points": [{"latitude":"38.0025","longitude":"23.8190"},{"latitude":"38.0018","longitude":"23.8193"},{"latitude":"38.0011","longitude":"23.8196"},{"latitude":"38.0005","longitude":"23.8200"}],
  "start_point": {"latitude": 38.0025, "longitude": 23.8190},
  "end_point":   {"latitude": 38.0005, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000017", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-11
# ==================================================

printf '\n==================================================\npedestrian-11\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000018",
  "name": "pedestrian-11",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 18,
  "ip_address_v4": "10.0.0.18",
  "ip_address_v6": "0:0:0:0:0:0:0:12",
  "mac_address": "22-00-00-00-00-12",
  "msisdn": "2020100000018",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10018@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-11: approaching monitoring zone from south",
  "points": [{"latitude":"37.9962","longitude":"23.8195"},{"latitude":"37.9969","longitude":"23.8196"},{"latitude":"37.9976","longitude":"23.8198"},{"latitude":"37.9983","longitude":"23.8200"}],
  "start_point": {"latitude": 37.9962, "longitude": 23.8195},
  "end_point":   {"latitude": 37.9983, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000018", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-12
# ==================================================

printf '\n==================================================\npedestrian-12\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000019",
  "name": "pedestrian-12",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 19,
  "ip_address_v4": "10.0.0.19",
  "ip_address_v6": "0:0:0:0:0:0:0:13",
  "mac_address": "22-00-00-00-00-13",
  "msisdn": "2020100000019",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10019@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-12: approaching monitoring zone from south",
  "points": [{"latitude":"37.9962","longitude":"23.8200"},{"latitude":"37.9969","longitude":"23.8200"},{"latitude":"37.9976","longitude":"23.8200"},{"latitude":"37.9983","longitude":"23.8200"}],
  "start_point": {"latitude": 37.9962, "longitude": 23.8200},
  "end_point":   {"latitude": 37.9983, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000019", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-13
# ==================================================

printf '\n==================================================\npedestrian-13\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000020",
  "name": "pedestrian-13",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 20,
  "ip_address_v4": "10.0.0.20",
  "ip_address_v6": "0:0:0:0:0:0:0:14",
  "mac_address": "22-00-00-00-00-14",
  "msisdn": "2020100000020",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10020@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-13: approaching monitoring zone from south",
  "points": [{"latitude":"37.9962","longitude":"23.8205"},{"latitude":"37.9969","longitude":"23.8204"},{"latitude":"37.9976","longitude":"23.8202"},{"latitude":"37.9983","longitude":"23.8200"}],
  "start_point": {"latitude": 37.9962, "longitude": 23.8205},
  "end_point":   {"latitude": 37.9983, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000020", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-14
# ==================================================

printf '\n==================================================\npedestrian-14\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000021",
  "name": "pedestrian-14",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 21,
  "ip_address_v4": "10.0.0.21",
  "ip_address_v6": "0:0:0:0:0:0:0:15",
  "mac_address": "22-00-00-00-00-15",
  "msisdn": "2020100000021",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10021@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-14: approaching monitoring zone from south",
  "points": [{"latitude":"37.9962","longitude":"23.8210"},{"latitude":"37.9969","longitude":"23.8208"},{"latitude":"37.9976","longitude":"23.8204"},{"latitude":"37.9983","longitude":"23.8200"}],
  "start_point": {"latitude": 37.9962, "longitude": 23.8210},
  "end_point":   {"latitude": 37.9983, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000021", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-15
# ==================================================

printf '\n==================================================\npedestrian-15\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000022",
  "name": "pedestrian-15",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 22,
  "ip_address_v4": "10.0.0.22",
  "ip_address_v6": "0:0:0:0:0:0:0:16",
  "mac_address": "22-00-00-00-00-16",
  "msisdn": "2020100000022",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10022@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-15: approaching monitoring zone from south",
  "points": [{"latitude":"37.9962","longitude":"23.8190"},{"latitude":"37.9969","longitude":"23.8193"},{"latitude":"37.9976","longitude":"23.8196"},{"latitude":"37.9983","longitude":"23.8200"}],
  "start_point": {"latitude": 37.9962, "longitude": 23.8190},
  "end_point":   {"latitude": 37.9983, "longitude": 23.8200},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000022", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-16
# ==================================================

printf '\n==================================================\npedestrian-16\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000023",
  "name": "pedestrian-16",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 23,
  "ip_address_v4": "10.0.0.23",
  "ip_address_v6": "0:0:0:0:0:0:0:17",
  "mac_address": "22-00-00-00-00-17",
  "msisdn": "2020100000023",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10023@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-16: traversing monitoring zone east to west",
  "points": [{"latitude":"37.9985","longitude":"23.8215"},{"latitude":"37.9985","longitude":"23.8205"},{"latitude":"37.9985","longitude":"23.8195"},{"latitude":"37.9985","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9985, "longitude": 23.8215},
  "end_point":   {"latitude": 37.9985, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000023", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-17
# ==================================================

printf '\n==================================================\npedestrian-17\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000024",
  "name": "pedestrian-17",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 24,
  "ip_address_v4": "10.0.0.24",
  "ip_address_v6": "0:0:0:0:0:0:0:18",
  "mac_address": "22-00-00-00-00-18",
  "msisdn": "2020100000024",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10024@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-17: traversing monitoring zone east to west",
  "points": [{"latitude":"37.9990","longitude":"23.8215"},{"latitude":"37.9990","longitude":"23.8205"},{"latitude":"37.9990","longitude":"23.8195"},{"latitude":"37.9990","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9990, "longitude": 23.8215},
  "end_point":   {"latitude": 37.9990, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000024", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-18
# ==================================================

printf '\n==================================================\npedestrian-18\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000025",
  "name": "pedestrian-18",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 25,
  "ip_address_v4": "10.0.0.25",
  "ip_address_v6": "0:0:0:0:0:0:0:19",
  "mac_address": "22-00-00-00-00-19",
  "msisdn": "2020100000025",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10025@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-18: traversing monitoring zone east to west",
  "points": [{"latitude":"37.9995","longitude":"23.8215"},{"latitude":"37.9995","longitude":"23.8205"},{"latitude":"37.9995","longitude":"23.8195"},{"latitude":"37.9995","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9995, "longitude": 23.8215},
  "end_point":   {"latitude": 37.9995, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000025", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-19
# ==================================================

printf '\n==================================================\npedestrian-19\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000026",
  "name": "pedestrian-19",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 26,
  "ip_address_v4": "10.0.0.26",
  "ip_address_v6": "0:0:0:0:0:0:0:1a",
  "mac_address": "22-00-00-00-00-1a",
  "msisdn": "2020100000026",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10026@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-19: traversing monitoring zone east to west",
  "points": [{"latitude":"38.0000","longitude":"23.8215"},{"latitude":"38.0000","longitude":"23.8205"},{"latitude":"38.0000","longitude":"23.8195"},{"latitude":"38.0000","longitude":"23.8185"}],
  "start_point": {"latitude": 38.0000, "longitude": 23.8215},
  "end_point":   {"latitude": 38.0000, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000026", "path": '"${PATH_ID}"'}'
printf '\n'


# ==================================================
# pedestrian-20
# ==================================================

printf '\n==================================================\npedestrian-20\n==================================================\n'

curl -s -X POST "${BASE}/UEs" "${H[@]}" -d '{
  "supi": "202010000000027",
  "name": "pedestrian-20",
  "description": "Pedestrian UE",
  "gNB_id": 1,
  "Cell_id": 27,
  "ip_address_v4": "10.0.0.27",
  "ip_address_v6": "0:0:0:0:0:0:0:1b",
  "mac_address": "22-00-00-00-00-1b",
  "msisdn": "2020100000027",
  "dnn": "province1.mnc01.mcc202.gprs",
  "mcc": 202,
  "mnc": 1,
  "external_identifier": "10027@poc.com",
  "speed": "LOW"
}'
printf '\n'

PATH_ID=$(curl -s -X POST "${BASE}/paths" "${H[@]}" -d '{
  "description": "pedestrian-20: traversing monitoring zone east to west",
  "points": [{"latitude":"37.9980","longitude":"23.8215"},{"latitude":"37.9980","longitude":"23.8205"},{"latitude":"37.9980","longitude":"23.8195"},{"latitude":"37.9980","longitude":"23.8185"}],
  "start_point": {"latitude": 37.9980, "longitude": 23.8215},
  "end_point":   {"latitude": 37.9980, "longitude": 23.8185},
  "color": "#cc6600"
}' | jq -r '.id')

curl -s -X POST "${BASE}/UEs/associate/path" "${H[@]}" \
  -d '{"supi": "202010000000027", "path": '"${PATH_ID}"'}'
printf '\n'



# ==================================================
# Pedestrian UE Group
# ==================================================

printf '\n==================================================\nPedestrian UE Group\n==================================================\n'

PEDESTRIAN_GROUP_ID=$(curl -s -X POST "${BASE}/UEGroups/imsiGroup" "${H[@]}" -d '{
  "UEs": [
    "202010000000008", "202010000000009", "202010000000010",
    "202010000000011", "202010000000012", "202010000000013",
    "202010000000014", "202010000000015", "202010000000016",
    "202010000000017", "202010000000018", "202010000000019",
    "202010000000020", "202010000000021", "202010000000022",
    "202010000000023", "202010000000024", "202010000000025",
    "202010000000026", "202010000000027"
  ]
}' | jq -r '.id')
printf '\n'

curl -s -X POST "${BASE}/UEGroups/exterGroup" "${H[@]}" -d '{
  "exterGroupId": "pedestrians@poc.com",
  "imsiGroupId": '"${PEDESTRIAN_GROUP_ID}"'
}'
printf '\n'
