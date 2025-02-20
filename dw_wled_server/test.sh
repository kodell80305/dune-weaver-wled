#!/bin/bash
export WLED_IP=192.168.50.117

# Check if the argument is provided
if [ -z "$1" ]; then
    echo "Error: WLED IP address is required."
    echo "Usage: $0 <WLED_IP>"
    exit 1
fi

# Assign the argument to a variable
WLED_IP=$1

# Now you can use the $WLED_IP variable in your script
echo "WLED IP Address: $WLED_IP"

#Setting new values
#Sending a POST request to /json or /json/state with (parts of) the state object 
#will update the respective values. Example: {"on":true,"bri":255} sets the brightness to maximum. 
#{"seg":[{"col":[[0,255,200]]}]} sets the color of the first segment to teal. 
#{"seg":[{"id":X,"on":"t"}]} and replacing X with the desired segment ID will toggle on or off that segment.
DATA="{\"seg\":[{\"id\":0,\"start\":0,\"stop\":50,\"len\":50,\"grp\":1,\"spc\":0,\"on\":true,\"bri\":$BRI,\"col\":[$COLOR_SIDES,[0,0,0],[0,0,0]],\"fx\":$FX,\"sx\":9,\"ix\":51,\"pal\":$PAL,\"sel\":false,\"rev\":false,\"mi\":false},{\"id\":1,\"start\":50,\"stop\":98,\"len\":48,\"grp\":1,\"spc\":0,\"on\":true,\"bri\":$BRI,\"col\":[$COLOR_TOP,[0,0,0],[0,0,0]],\"fx\":100,\"sx\":150,\"ix\":128,\"pal\":0,\"sel\":true,\"rev\":false,\"mi\":false},{\"id\":2,\"start\":98,\"stop\":150,\"len\":52,\"grp\":1,\"spc\":0,\"on\":true,\"bri\":$BRI,\"col\":[$COLOR_SIDES,[0,0,0],[0,0,0]],\"fx\":$FX,\"sx\":9,\"ix\":51,\"pal\":$PAL,\"sel\":false,\"rev\":false,\"mi\":false}]}}}"


export SLEEP_TIME=5


#Start effect number 1
curl -X GET "http://${WLED_IP}/json/state" -d '{"effect": 1}' -H "Content-Type: application/json"


response=$(curl -X POST "http://${WLED_IP}/json/eff"  -H "Content-Type: application/json")

if [ -n "$response" ]; then
  echo "$response"
else
  echo "Failed to retrieve effects list from WLED server."
fi

#echo "curl --header \"Content-Type: application/json\" --request POST --data \"$DATA\" http://$WLED_IP/json\n\n"
#curl --header "Content-Type: application/json" --request POST --data "$DATA" http://$WLED_IP/json
#echo "curl -H "Accept: application/json" http://$WLED_IP/json\n\n"
#curl -H "Accept: application/json" http://$WLED_IP/json
#echo "Turning on"
#curl -X POST "http://$WLED_IP/json/state" -d '{"on":"t","v":true}' -H "Content-Type: application/json"

echo "Turning off"
curl -X POST "http://$WLED_IP/json/state" -d '{"on":"f","v":true}' -H "Content-Type: application/json"
sleep 2
echo "Back on - setting brightness to 40"
curl -X POST "http://$WLED_IP/json/state" -d '{"on":"t","v":true}' -H "Content-Type: application/json"
curl -X POST http://$WLED_IP/json/state   -d '{"bri": 40}' -H "Content-Type: application/json"


sleep $SLEEP_TIME
echo "brightness to 128"
curl -X POST http://$WLED_IP/json/state  -d '{"bri": 128}' -H "Content-Type: application/json"

sleep 2
echo "Set red"
curl -X POST http://$WLED_IP/json/state   -d '{"seg":[{"col":[[255, 0,0]]}]}' -H "Content-Type: application/json"  
sleep 2
echo "Set green"
curl -X POST http://$WLED_IP/json/state  -d '{"seg":[{"col":[[0, 255,0]]}]}'  -H "Content-Type: application/json"
sleep 2
echo "Set blue"
curl -X POST http://$WLED_IP/json/state  -d '{"seg":[{"col":[[0, 0, 255]]}]}' -H "Content-Type: application/json" 
sleep 2
echo "Set effect 2" 
#Start effect number 2
curl -X GET "http://${WLED_IP}/json/state" -d '{"effect": 2}' -H "Content-Type: application/json"


