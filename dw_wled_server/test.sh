#!/bin/bash
export WLED_IP=192.168.50.117
export WLED_PORT=80
export SLEEP_TIME=1
export test_id=all

# Initialize variables
verbose=false


# Parse options
while getopts "vp:s:t:" opt; do
  case $opt in
    v)
      verbose=true
      ;;
    s)
      SLEEP_TIME="$OPTARG"
      ;;
    t)
        test_id="$OPTARG"
        ;;
    p)
      WLED_PORT="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

echo "Remaining arguments: $@"



# Remove parsed options from argument list
shift $((OPTIND - 1))
# Check if the argument is provided
if [ -z "$1" ]; then
    echo "Error: WLED IP address is required."
    echo "Usage: $0 <WLED_IP> [-v] [-p <WLED_PORT>]"
    exit 1
fi

WLED_IP=$1

#web tests
echo -e ">>>>>Pallets:\n\n"
curl -X GET "http://${WLED_IP}/json/pallets"  -H "Content-Type: application/json"
echo -e "\n>>>>>fxdata"
curl -X GET "http://${WLED_IP}/json/fxdata" -H "Content-Type: application/json"
echo -e "\n>>>>>palx"
curl -X GET "http://${WLED_IP}/json/palx" -H "Content-Type: application/json"
echo -e "\n>>>>effects\n\n"
curl -X GET "http://${WLED_IP}/json/effects" -H "Content-Type: application/json"
echo -e "\n>>>>si\n\n"
curl -X GET "http://${WLED_IP}/json/si" -H "Content-Type: application/json"
echo -e "\n>>>>presets"
curl -X GET "http://${WLED_IP}/presets.json" -H "Content-Type: application/json"
echo -e "\n>>>>presets"
curl -X GET "http://${WLED_IP}/ws" -H "Content-Type: application/json"

exit 0

test_1() {
    echo "Turning on"
    #Start effect number 1
    curl -X GET "http://${WLED_IP}/json/state" -d '{"effect": 1}' -H "Content-Type: application/json"
}

test_2() {
    response=$(curl -X POST "http://${WLED_IP}/json/eff"  -H "Content-Type: application/json")

    if [ -n "$response" ]; then
    echo "$response"
    else
    echo "Failed to retrieve effects list from WLED server."
    fi
}
test_3() {
    response=$(curl -X POST "http://${WLED_IP}/json/state" -d '{"on":false}' -H "Content-Type: application/json")

    if [ -n "$response" ]; then
        echo "$response"
    else
         "Failed to turn off the lights."
    fi
}
test_4() {
    response=$(curl -X POST "http://${WLED_IP}/json/state" -d '{"on":true, "v":true}' -H "Content-Type: application/json")

    if [ -n "$response" ]; then
    echo "$response"
    else
    echo "Failed to turn on the lights."
    fi
    echo "Back on - setting brightness to 40"
    curl -X POST http://$WLED_IP/json/state   -d '{"bri": 40}' -H "Content-Type: application/json"
        
    response=$(curl -X POST "http://${WLED_IP}/json/state" -d '{"v":true}' -H "Content-Type: application/json")

    if [ -n "$response" ]; then
    echo "$response"
    else
    echo "Failed to turn on the lights."
    fi
    sleep $SLEEP_TIME
    echo "brightness to 128"
    curl -X POST http://$WLED_IP/json/state  -d '{"bri": 128}' -H "Content-Type: application/json"
}

test_5()  { 
  
    sleep $SLEEP_TIME
    echo "Set red"
    curl -X POST http://$WLED_IP/json/state   -d '{"seg":[{"col":[[255, 0,0]]}]}' -H "Content-Type: application/json"  
    sleep $SLEEP_TIME
    echo "Set green"
    curl -X POST http://$WLED_IP/json/state  -d '{"seg":[{"col":[[0, 255,0]]}]}'  -H "Content-Type: application/json"
    sleep $SLEEP_TIME
    echo "Set blue"
    curl -X POST http://$WLED_IP/json/state  -d '{"seg":[{"col":[[0, 0, 255]]}]}' -H "Content-Type: application/json" 
    sleep $SLEEP_TIME
}


# Effect Parameters (example)
EFFECT_ID=3        # Effect ID (e.g., 0 for "Solid", 1 for "Blink")
COLOR="0,255,0"   # Color in RGB (e.g., "255,0,0" for Red)
BRIGHTNESS=180    # Brightness (0 to 255)
SPEED=5           # Speed (optional for certain effects)
INTENSITY=4       # Intensity (optional for certain effects

#
test_6() {  
 
# Send cURL request to set the effect by ID with parameters

    curl -X POST "http://${WLED_IP}/json" -d '{"effect": '"$EFFECT_ID"',"effectSpeed": '"$SPEED"',"color": [255, 0, 0], "brightness": 128      
    }'  -H "Content-Type: application/json" 
    sleep $SLEEP_TIME
}

test_7() {
    echo "Playing playlist 2"
    curl -X POST "http://${WLED_IP}/json/state" -d '{"pl": 2}'  -H "Content-Type: application/json" 
    sleep $SLEEP_TIME
}

test_8() {
    echo "Playing playlist 1"
    curl -X POST "http://${WLED_IP}/json/state" -d '{"pl": 1}'  -H "Content-Type: application/json" 
    sleep $SLEEP_TIME
}



# Array of test functions
tests=(
  test_1
  test_2
  test_3
  test_4
  test_5
  test_6
  test_7
  test_8
)

if [ "$test_id" = "all" ]; then
    # Command to execute if $test_id is "all"
    echo "Executing command for all tests"
  # Loop through the array and run each test function
  for test in "${tests[@]}"; do
      eval "$test"
  done
  exit 0
fi

# Function to run a specific test
run_test() {
    echo "Running test" $test_id
  test_number="$test_id"
  if [[ "$test_number" -ge 1 && "$test_number" -le "${#tests[@]}" ]]; then
    test_name="${tests[test_number-1]}"
    echo "Running $test_name..."
    "$test_name"
  else
    echo "Invalid test number: $test_number"
  fi
}

# Main script logic
if [[ "$#" -eq 0 ]]; then
  # Run all tests if no arguments are provided
  echo "Running all tests..."
  for i in "${!tests[@]}"; do
    run_test "$((i + 1))"
  done
elif [[ "$1" == "-a" || "$1" == "--all" ]]; then
    echo "Running all tests..."
  for i in "${!tests[@]}"; do
    run_test "$((i + 1))"
  done
else
  # Run specific tests based on provided numbers
  for arg in "$@"; do
    run_test "$arg"
  done
fi



