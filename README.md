# Transactify Terminal
This project leverages Docker for containerization and automated configuration. 

## Prerequireies
> [!NOTE]
> Make sure you have `sudo`-rights on the system
1. Install [Docker](https://docs.docker.com/engine/install/)  and [docker-compose](https://docs.docker.com/compose/install/)
2. Clone this project
   ```
   git@github.com:agentsmith29/transactify.git
   cd transactify
   ```
### Host Setup
<details close>
  
<summary>Enable a wifi restart script</summary>

If you are running on wifi and the wifi connection drops, you can add a watchdog for it
```bash
sudo cp -r ./wifi_rebooter.sh /usr/local/bin/wifi_rebooter.sh && sudo chmod +x /usr/local/bin/wifi_rebooter.sh
```
add the following to crontab `*/5 *   * * *   root    /usr/local/bin/wifi_rebooter.sh` using `crontab -e`
```bash
crontab -e
# Add: "*/5 *   * * *   root    /usr/local/bin/wifi_rebooter.sh" at the end of the file
```
restart the cron service and check the status of the cron service
```bash
sudo systemctl restart cron.service
sudo systemctl status cron.service  
```
</details>

> [!TIP]
> Enabeling a watchdog automatically restart your host if a crash or a hung is detected.
<details closed>
    
<summary>Enable a watchdog (<b>highly recommended</b>)</summary>

I took it from [Medium: Enabling Watchdog on Raspberry Pi](https://medium.com/@arslion/enabling-watchdog-on-raspberry-pi-b7e574dcba6b)
1. Activating watchdog hardware in pi
```bash
sudo chmod +x ./host_scripts/enable_watchdog.sh && sudo ./host_scripts/enable_watchdog.sh
```

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
</details>  

> [!TIP]
> Enabeling the SysReq keys allow to shutdown and rebbot you system from within docker (using your application)
<details closed>

<summary>Add magic Linux Magic System Request Key Hacks (<b>recommended</b>) </summary>
The magic SysRq key is a key combination understood by the Linux kernel, which allows the user to perform various low-level commands regardless of the system's state. It is often used to recover from freezes, or to reboot a computer without corrupting the filesystem. See also [kernel.org: Linux Magic System Request Key Hacks](https://www.kernel.org/doc/html/v4.11/admin-guide/sysrq.html)


```bash
sudo chmod +x ./host_scripts/sysrq/enable_sysrq.sh && sudo ./host_scripts/sysrq/enable_sysrq.sh
```
Try it using
``` bash
echo h > /proc/sysrq-trigger            # Just prints help message
dmesg | tail -n 1 | grep sysrq
```
</details>

## Running (Docker)
1. Adapt the configutation in the config files (see  [Configuration](#configuration) Section). 
To run the whole project, simply call 
``` bash
docker-compose up --build
```
### Configuration
<details close>
  
  <summary>Configuration Files</summary>
  
  For configuration, the project uses the [ConfigParser](./common/src/ConfigParser)-Class, which allows to configure the djago webserver. All necessary configurations are managed through a configuration file, which can be found here as an example:
  - [Store Config](./transactify_service/configs/store_config.example.yaml).
  - [Terminal Config](./transactify_terminal/configs/terminal_config.example.yaml).
</details>

<details>
  <summary>Global Settings</summary>
Global settings are stored in a (Docker) [`.env`-File](./.env). In the `.env`-File, change the port and the host:
```
.env
PROJECT_HOST=192.168.1.190
PROJECT_PORT=8000

# Database settings and credentials
DB_PORT=5432
DB_USER=USER
DB_PASSWORD=PASSWORD
```
## Running
Create the virtual environment
```bash
python -m venv .venv
. .venv/bin/activate    # on linux
```
</details>

When using docker, use the following example config file
```yaml
version: '3.9'
services:
  # DATABASE
  db:
    image: postgres
    restart: always
    shm_size: 128mb
    environment:
      POSTGRES_USER: ${DB_USER}         # Stored in the .env file
      POSTGRES_PASSWORD: ${DB_PASSWORD} # Stored in the .env file
    ports:
      - 5432:${DB_PORT}                 # Stored in the .env file
  
  terminal1:
    build:
      context: .
      dockerfile: ./transactify_terminal/Dockerfile
    restart: always
    tty: true         # docker run -t, used to have a nice log formatting (rich logging)
    privileged: true  # Grants access to devices and kernel features and hardware
    cap_add:
      - SYS_RAWIO  # Allows raw GPIO access
    security_opt:
      - apparmor:unconfined  # Unrestricted access to hardware
    volumes:
      # Configuration file for the store
      - ./transactify_terminal/configs/terminal1_config.yaml:/app/webapp/configs/config.yaml
      # Needed to retrieve container infos
      - /run/docker.sock:/run/docker.sock:ro
      #
      - nginx_data:/etc/nginx/conf.d
      - static_volume:/app/static
    depends_on:
      - db
    healthcheck:
      test: "curl http://127.0.0.1:${PROJECT_PORT}/terminal1/health"
      start_period: 10s
      interval: 10s
      timeout: 10s
      retries: 10
    deploy:       # limit maximum number of containers to 1
      replicas: 1 # Important for the terminal to work properly (only one terminal can be connected to the hardware)
  
  your_store:
    build:
      context: .
      dockerfile: ./transactify_service/Dockerfile
    restart: always
    depends_on:
      - db
      - terminal1
    volumes:
      # Configuration file for the store
      - .env:/app/.env    # Needed by the config loader
      # Mounts your configuratin file 
      - ./transactify_service/configs/your_store.yaml:/app/webapp/configs/config.yaml 
      # Docker socket for container management
      - /run/docker.sock:/run/docker.sock:ro
      # Data: Nginx configuration and static files
      - nginx_data:/etc/nginx/conf.d
      - static_volume:/app/static
    healthcheck:
      test: "curl http://127.0.0.1:${PROJECT_PORT}/your_store/health"
      start_period: 10s
      interval: 10s
      timeout: 10s
      retries: 10

  # Optional, good for managing you database
  adminer:
    image: adminer
    restart: always
    ports:
      - 8080:8080
    #depends_on:
    #  - django

  # Needed, for serving static files and routing
  nginx:
    image: nginx:latest
    restart: always
    volumes:
      # To serve the startic files
      - static_volume:/static
      # Automatically configures the services
      - ./common/nginx/nginx.conf:/etc/nginx/nginx.conf
      - nginx_data:/etc/nginx/conf.d
      
      - /proc/sysrq-trigger:/sysrq
    ports:
      - 8000:8000
    depends_on:
      donknabberello:
        condition: service_started
      doncaramello:
        condition: service_started
      terminal1:
        condition: service_healthy

volumes:
  nginx_data:
  postgres_data:
  static_volume:

```

### Troubleshooting
If your neginx instance makes problems its often good to start fresh and remove all volumes and containers. The database should not be 
affacted.

## Directly running on the host (not recommended)
> [!NOTE]
> This section is outdated. Do not use it. For now, it should be sufficient to use the `run_on_host.sh`- scripts.

> [!NOTE]
> If you have problems with syntax highlghting in your VS-Code project, check if you have included the following settings for you [VSCode Settings](.vscode/settings.json)
> ```json
> {
>     "python.analysis.extraPaths": ["./common/src"]
> }
> ```
### Create a virtual environment and install the requirements
```bash
python -m venv .venv
pip install -r requirements.txt   # install requirements
```
Enable the `.venv`, change directory and install the requirements
```bash
. .venv/bin/activate              # on linux, if not already activated
cd ./transactify_service      
```
### Run the migrations (creates a user admin with password admin)
<details>
  
  <summary>If you want to delete the database</summary>
  
```bash
export MAIN_DB="cashless_donknabberello_1"
export PGPASSWORD="PASSWORD"     # Change to your db pssword
export PGUSER="USER"             # Change to your db user
export PGHOST="192.168.1.190"    # Change your your db host
psql -h $PGHOST -U $PGUSER -p 5432 -d 'postgres' -c "DROP DATABASE IF EXISTS \"$MAIN_DB\";"
psql -h $PGHOST  -U $PGUSER -p 5432 -d 'postgres' -c "CREATE DATABASE \"$MAIN_DB\" OWNER \"$PGUSER\";"
```
</details>

Run the migrations (creates a user admin with password admin)
```bash
export "RUN_SERVER"="false"
python manage.py makemigrations && python manage.py migrate
export DJANGO_SUPERUSER_PASSWORD="ADMIN"
export DJANGO_SUPERUSER_USERNAME="ADMIN"
export DJANGO_SUPERUSER_EMAIL="$DJANGO_SUPERUSER_PASSWORD@$DJANGO_SUPERUSER_USERNAME.com"
python manage.py createsuperuser --noinput
export "RUN_SERVER"="true"
```
### Enable the reboot- and shutdown script
If you are running on the host, you must enable the following scripts to be run without a sudo password.
> [!IMPORTANT]
> Add the full path to the script `./transactify_service/scripts/shutdown.sh` Also make sure the user (pi) mathces the user, running the server.

Add the shutdown script to the `visudo` file
```txt
pi ALL=(ALL) NOPASSWD: <fullpath>/transactify_service/scripts/shutdown.sh´ to be able to run without sudo
pi ALL=(ALL) NOPASSWD: <fullpath>/transactify_service/scripts/reboot.sh´ to be able to run without sudo
```
using
```bash
sudo visudo
```
Run the server on the host
```bash
export "RUN_SERVER"="true"
daphne -b 0.0.0.0 -p 8880 transactify_service.asgi:application
```
### The all-in-in Script
```bash
./run_on_host.sh
```

## Running the tests
```bash
docker-compose -f docker-compose.tests.yaml up --build
```


```bash
sudo /home/pi/workspace/cashless/.venv/bin/python neopixel_test.py
```

# Development


I managed to debug the issue using the following command:

```gdb --args python manage.py migrate```

Inside gdb, I ran the program to trace the error:

```(gdb) run```

The root cause turned out to be related to conda dependencies. I resolved the problem by updating all packages with this command:

```conda update --all```
