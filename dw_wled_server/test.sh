
#Setting new values
#Sending a POST request to /json or /json/state with (parts of) the state object 
#will update the respective values. Example: {"on":true,"bri":255} sets the brightness to maximum. 
#{"seg":[{"col":[[0,255,200]]}]} sets the color of the first segment to teal. 
#{"seg":[{"id":X,"on":"t"}]} and replacing X with the desired segment ID will toggle on or off that segment.
DATA="{\"seg\":[{\"id\":0,\"start\":0,\"stop\":50,\"len\":50,\"grp\":1,\"spc\":0,\"on\":true,\"bri\":$BRI,\"col\":[$COLOR_SIDES,[0,0,0],[0,0,0]],\"fx\":$FX,\"sx\":9,\"ix\":51,\"pal\":$PAL,\"sel\":false,\"rev\":false,\"mi\":false},{\"id\":1,\"start\":50,\"stop\":98,\"len\":48,\"grp\":1,\"spc\":0,\"on\":true,\"bri\":$BRI,\"col\":[$COLOR_TOP,[0,0,0],[0,0,0]],\"fx\":100,\"sx\":150,\"ix\":128,\"pal\":0,\"sel\":true,\"rev\":false,\"mi\":false},{\"id\":2,\"start\":98,\"stop\":150,\"len\":52,\"grp\":1,\"spc\":0,\"on\":true,\"bri\":$BRI,\"col\":[$COLOR_SIDES,[0,0,0],[0,0,0]],\"fx\":$FX,\"sx\":9,\"ix\":51,\"pal\":$PAL,\"sel\":false,\"rev\":false,\"mi\":false}]}}}"

export IP_ADDRESS=192.168.50.117

export IP_ADDRESS=$1
export BRIGHTNESS_VALUE=$2

#echo "curl --header \"Content-Type: application/json\" --request POST --data \"$DATA\" http://$IP_ADDRESS/json\n\n"
#curl --header "Content-Type: application/json" --request POST --data "$DATA" http://$IP_ADDRESS/json
#echo "curl -H "Accept: application/json" http://$IP_ADDRESS/json\n\n"
#curl -H "Accept: application/json" http://$IP_ADDRESS/json
echo "Turning on"
curl -X POST "http://$IP_ADDRESS/json/state" -d '{"on":"t","v":true}' -H "Content-Type: application/json"
sleep 2
echo "Turning off"
curl -X POST "http://$IP_ADDRESS/json/state" -d '{"on":"f","v":true}' -H "Content-Type: application/json"
sleep 2
echo "Back on - setting brightness to 40"
curl -X POST "http://$IP_ADDRESS/json/state" -d '{"on":"t","v":true}' -H "Content-Type: application/json"
curl -X POST -H "Content-Type: application/json" -d '{"bri": 40}' http://$IP_ADDRESS/json/state
sleep 2
echo "brightness to 128"

sleep 5
echo "Set "green"
curl -X POST http://$IP_ADDRESS/json/state   -H "Content-Type: application/json"   -d '{"seg":[{"col":[[0, 255,0]]}]}'
sleep 5
echo "Set "blue"
curl -X POST http://$IP_ADDRESS/json/state   -H "Content-Type: application/json"   -d '{"seg":[{"col":[[0, 0, 255]]}]}'

curl -X POST -H "Content-Type: application/json" -d '{"bri": 128}' http://$IP_ADDRESS/json/state
echo "Set red"
curl -X POST http://$IP_ADDRESS/json/state   -H "Content-Type: application/json"   -d '{"seg":[{"col":[[255, 0,0]]}]}'

