# Transactify Terminal

## Usage
All settings are store in the [`.env`-File](./.env) and in the [`docker-compose.yaml`](./docker-compose.yaml) File. In the `.env`-File, change
the port and the host.
```
.env
PROJECT_HOST=192.168.1.190
PROJECT_PORT=8000

```
## Running
Create the virtual environment
```bash
python -m venv .venv
. .venv/bin/activate    # on linux
```

### First time running the project
In each django application [`transactify_service`](./transactify_service/) and  [`transactify_terminal`](./transactify_terminal/) a entrypoint file is placed. Uncomment the following lines
```bash
#chmod +x make_migrations.sh
chmod +x make_store_db_migration.sh
# run make migrations
./make_store_db_migration.sh
```
which triggers the migration of the PostgreSQL Database. Please note, that a run of this script, also removes the whole database, thus make sure it is only run when using a fresh installation.

### Running the project
To run this project, use the docker-compose file. All other things are setup automatically.
```bash
docker-compose up --build
```
### Debugging: Directly running on the host (not recommended)
Enable the venv and change directory
```bash
. .venv/bin/activate    # on linux, if not already activated
cd ./transactify_service
```
Run the migrations
```bash
python manage.py makemigrations && python manage.py migrate
```
Add the shutdown script ´:/transactify_service/scripts/shutdown.sh´ to be able to run without sudo
```bash
sudo visudo
```
and add
```txt
www-data ALL=(ALL) NOPASSWD: /home/pi/workspace/cashless/transactify_service/scripts/shutdown.sh
```
Run the server on the host
```bash
daphne -b 0.0.0.0 -p 8880 transactify_service.asgi:application
```

## Running the tests
```bash
docker-compose -f docker-compose.tests.yaml up --build
```


```bash
sudo /home/pi/workspace/cashless/.venv/bin/python neopixel_test.py
```

# Host Setup
## Enable a wifi restart script
If you are running on wifi and the wifi connection drops, you can add a watchdog for it
```bash
sudo cp -r ./wifi_rebooter.sh /usr/local/bin/wifi_rebooter.sh && sudo chmod +x /usr/local/bin/wifi_rebooter.sh
```
add the following to crontab `*/5 *   * * *   root    /usr/local/bin/wifi_rebooter.sh` using `crontab -e`
```bash
crontab -e
# Add: "*/5 *   * * *   root    /usr/local/bin/wifi_rebooter.sh" at the end of the file

# Restart the cron service
sudo systemctl restart cron.service
# Check the status of the cron service
sudo systemctl status cron.service  
```
## Enable a watchdog
I took it from [Medium: Enabling Watchdog on Raspberry Pi](https://medium.com/@arslion/enabling-watchdog-on-raspberry-pi-b7e574dcba6b)
1. Activating watchdog hardware in pi
```bash
sudo chmod +x ./host_scripts/enable_watchdog.sh && sudo ./host_scripts/enable_watchdog.sh
```
2. Installing watchdog
```bash
sudo apt-get install watchdog
```
3. Reboot your raspberry pi. After reboot list devices with the name prefixed by watchdog, to do so run the following command:
```bash
sudo reboot
```
4. Configuring watchdog to respond to events
```bash
sudo chmod +x ./host_scripts/configure_watchdog.sh && sudo ./host_scripts/configure_watchdog.sh
```
Now the watchdog should be running.
5. Restarting/Monitoring watchdog service:
```bash
# Start the watchdog
sudo systemctl restart watchdog
# View the status of the watchdog
sudo systemctl status watchdog
```
Sometimes, when the config has changed, you need to restart it again.

## Add magic Linux Magic System Request Key Hacks
Take from [kernel.org: Linux Magic System Request Key Hacks](https://www.kernel.org/doc/html/v4.11/admin-guide/sysrq.html)
It is a ‘magical’ key combo you can hit which the kernel will respond to regardless of whatever else it is doing, unless it is completely locked up.
1. Enable the magic system keys

```bash
sudo chmod +x ./host_scripts/sysrq/enable_sysrq.sh && sudo ./host_scripts/sysrq/enable_sysrq.sh
```
Try it using
``` bash
echo h > /proc/sysrq-trigger            # Just prints help message
dmesg | tail -n 1 | grep sysrq
```