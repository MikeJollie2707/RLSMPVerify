# Setup

Create a `config.json` in this directory (setup) with the following format:

```json
{
    "token": "token here",
    "target_msg": "id here"
}
```

`"token"` is your bot token (don't leak). For `"target_msg"`, just target a random message's **ID** (this will result in an error the first time, but the second time it'll correct itself to the proper ID) or the one in the gate channel.
