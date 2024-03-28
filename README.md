# MooseSMPVerify

## Setup

Check `setup/` for more info.

### Development/Manual

*If you're on Windows, replace `python3` with either `python` or `py -3`. In some cases, `py -3` might install the libs in global environment. Test it out before installing dependencies.*

To install dependencies, do the following:

```sh
mkdir venv
python3 -m venv venv
source ./venv/bin/activate
python3 -m pip install hikari hikari-lightbulb hikari-miru
```

*If you're on Windows, find and execute `Activate.ps1` instead of doing `source`. Or use vscode to select the correct interpreter.*

To run the bot:

```sh
python3 main.py
```

Or if you want some optimizations (although it doesn't really matter):

```sh
python3 -O main.py
```

That's an "old", not "zero".

### Deployment/Docker

*The instruction will be geared towards Linux because I don't have Docker on Windows. Also, use `sudo` if you encounter something like "permission denied".*

If you have Docker on your machine, you can build a container for this thing.

```sh
docker build -t rlsmpverify .
docker run -d rlsmpverify
docker ps

# To delete the container and the image
docker stop <container_id>
docker rm <container_id>
docker images
docker images rm <image_id>
```

Or use `quickdocker.sh` if you're on Linux.

```sh
chmod +x quickdocker.sh
./quickdocker.sh --build .    # If there's no image of rlsmpverify, this dot is required.
./quickdocker.sh --build      # Run the container, no dot is required.
./quickdocker.sh --stop       # Stop container. Can start it again using --build
./quickdocker.sh --remove     # Stop and remove container.
./quickdocker.sh --remove-all # Stop and remove both container and the rlsmpverify image.
```

Or use `docker compose` if you have it installed. This has the benefit that if your Docker installation starts on reboot, the bot will also starts on reboot.

```sh
docker build -t rlsmpverify .
docker compose up -d

docker compose stop # Shut the container down.
docker compose down # Shut the container down and delete it.
```

## Contribute

- `git init` then `git pull` or just extract the code with zip.
- Pull request. Don't push to `main`.
- Make sure to change the channel ID in `main.py` to suit your need. By default, the values are NOT production-ready.
