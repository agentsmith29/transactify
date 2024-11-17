# cashless

source .venv/bin/activate
i2cdetect -y 1
atch -n1 i2cdetect -y 1



sudo apt remove python3-rpi.gpio
sudo apt update
sudo apt install python3-rpi-lgpio