# Transactify Terminal

## Usage
All settings are store in the [`.env`-File](./.env) and in the [`docker-compose.yaml`](./docker-compose.yaml) File. In the `.env`-File, change
the port and the host.
```
.env
PROJECT_HOST=192.168.1.190
PROJECT_PORT=8000

```
## First time running the project
In each django application [`transactify_service`](./transactify_service/) and  [`transactify_terminal`](./transactify_terminal/) a entrypoint file is placed. Uncomment the following lines
```bash
#chmod +x make_migrations.sh
chmod +x make_store_db_migration.sh
# run make migrations
./make_store_db_migration.sh
```
which triggers the migration of the PostgreSQL Database. Please note, that a run of this script, also removes the whole database, thus make sure it is only run when using a fresh installation.

## Running the project
To run this project, use the docker-compose file. All other things are setup automatically.
```bash
docker-compose up --build
```

## Running the tests
```bash
docker-compose -f docker-compose.tests.yaml up --build
```


```bash
sudo /home/pi/workspace/cashless/.venv/bin/python neopixel_test.py
```

# Host Sysstem Setuo
We want to setup the host to allow certain things.

## Enable magic SysRq
```bash
# See
bitmask_2 	= 2		    # 0x2 - enable control of console logging level
bitmask_4 	= 4		    # 0x4 - enable control of keyboard (SAK, unraw)
bitmask_8 	= 8		    # 0x8 - enable debugging dumps of processes etc.
bitmask_16 	= 16		# 0x10 - enable sync command
bitmask_32 	= 32		# 0x20 - enable remount read-only
bitmask_64 	= 64		# 0x40 - enable signalling of processes (term, kill, oom-kill)
bitmask_128 = 128		# 0x80 - allow reboot/poweroff
bitmask_256 = 256       # 0x100 - allow nicing of all RT tasks  allow nicing of all RT tasks
bitmask=$bitmask_256

echo $bitmask >/proc/sys/kernel/sysrq


```

## Enable a watchdog
See https://medium.com/@arslion/enabling-watchdog-on-raspberry-pi-b7e574dcba6b
```
sudo apt-get install watchdog
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