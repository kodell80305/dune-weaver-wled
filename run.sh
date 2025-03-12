#For development I want to build the web pages every time from scratch ... this isn't really necessary
#if they're not changing.
rm -rf templates
rm -rf static
./build_web.sh
sudo python startup.py
