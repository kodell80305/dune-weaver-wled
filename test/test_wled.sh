#!/bin/bash
export WLED_IP=127.0.0.1

# Start the program
./run.sh &
PROGRAM_PID=$!

# Wait for the program to be ready
sleep 5  # Adjust the sleep time as needed
# Load shunit2
. ./test/shunit2/shunit2

# Test functions
testTurningOn() {
  result=$(./test.sh ${WLED_IP} -t 1)
  assertContains "Turning on" "$result"
}

testTurningOff() {
  result=$(./test.sh$ {WLED_IP} -t 3)
  assertContains "Failed to turn off the lights." "$result"
}


# Stop the program
kill $PROGRAM_PID