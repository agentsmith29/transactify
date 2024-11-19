# cashless

source .venv/bin/activate
i2cdetect -y 1
atch -n1 i2cdetect -y 1



sudo apt remove python3-rpi.gpio
sudo apt update
sudo apt install python3-rpi-lgpio


# Run the webserver
python manage.py makemigrations store &&  python manage.py migrate store &&  python manage.py migrate
python manage.py runserver 192.168.137.34:8000 