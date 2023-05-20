# RLSMPVerify

## Setup

Check `setup/` for more info.

*If you're on Windows, replace `python3` with either `python` or `py -3`. In some cases, `py -3` might install the libs in global environment. Test it out before installing dependencies.*

To install dependencies, do the following:

```
mkdir venv
python3 -m venv venv
source ./venv/bin/activate
python3 -m pip install hikari hikari-lightbulb hikari-miru
```

*If you're on Windows, find and execute `Activate.ps1` instead of doing `source`. Or use vscode to select the correct interpreter.*

To run the bot:

```
python3 main.py
```

Or if you want some optimizations (although it doesn't really matter):

```
python3 -O main.py
```

That's an "old", not "zero".

## Contribute

- `git init` then `git pull` or just extract the code with zip.
- Pull request. Don't push to `main`.
- Make sure to change the channel ID in `main.py` to suit your need. By default, the values are NOT production-ready.
