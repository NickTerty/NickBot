# NickBot - Tainan Lunch & Drink Random Picker
Tainan is the city where I was born and grew up, and it is famous for its food. But with so many choices, it is often hard to decide what to eat for lunch or dinner. NickBot is a Discord bot that makes the decision for you.

## Commands
| Command | Description |
|---|---|
| `/lunch` | Randomly picks a restaurant in the selected district within your budget. |
| `/lunch_list` | Lists all restaurants in the selected district, optionally filtered by budget. |
| `/drink` | Randomly picks a drink shop. |
| `/drink_list` | Lists all drink shops the bot can pick from. |

Supported districts: West Central, East, South, North, and Anping.
Budget levels: under NT$130, NT$130–300, and NT$300+.

## Project Structure
```
NickBot/
├── main.py                    # Entry point: python main.py
├── bot/
│   ├── client.py              # Bot core: auto-loads commands, syncs them, global error handling
│   ├── config.py              # Paths and environment variables (BOT_TOKEN / DEV_GUILD_ID)
│   ├── constants.py           # Shared district/budget choices and cooldown settings
│   ├── data_loader.py         # JSON loading, validation, and caching
│   ├── utils.py               # Markdown/@mention escaping and list truncation
│   └── cogs/                  # One file = one slash command
│       ├── lunch.py
│       ├── lunch_list.py
│       ├── drink.py
│       └── drink_list.py
├── data/                      # restaurants.json, drink.json
├── docs/                      # TOS.txt, privacy-policy.txt
└── scripts/clear_commands.py  # Removes leftover (ghost) slash commands
```

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in `BOT_TOKEN` (or set it as a system environment variable).
3. Run the bot: `python main.py`

> Never commit your bot token. `.env` is already excluded by `.gitignore`.

Optional: set `DEV_GUILD_ID` to a test server ID to sync commands only to that server (changes appear instantly). Leave it empty in production to sync commands globally.

## Adding / Removing Commands
- **Add:** copy an existing file in `bot/cogs/` and modify it. It is loaded and synced automatically on startup.
- **Remove:** delete the file. The command is removed from Discord the next time the bot starts.
- **Ghost commands:** if old commands still appear, run `python -m scripts.clear_commands --guild <SERVER_ID>`.

## Editing Restaurants & Drinks
- `data/restaurants.json`: restaurants grouped by district, each with a `name` and a `price_level` (1–3).
- `data/drink.json`: a list of drink shop names.

Invalid entries are skipped and logged instead of crashing the bot.

## Legal
- [Terms of Service](docs/TOS.txt)
- [Privacy Policy](docs/privacy-policy.txt)

## Changelog

### 11/15/2026
- Added more restaurants and drink shops.
- Restructured the project: one file per command, with data and docs in separate folders.
- Commands are only re-synced when they change, and deleted commands no longer linger as ghost commands.
- Security improvements:
  - Removed the unused privileged Message Content intent.
  - The bot can no longer mention users, roles, or @everyone.
  - Added per-user cooldowns, data validation, and friendly error messages.
- Updated the Terms of Service and Privacy Policy to match the bot's current behavior.

### 7/11/2026
- Added more restaurants and drink shops.

### 7/3/2026
- New command: `/drink_list`
- Added more restaurants and drink shops.
- Removed some ghost commands.

### 7/2/2026 - Initial Release
- Added more restaurants.
- New districts: North District and Anping District.
- Commands are synced globally, so no test server needs to be specified.
- Added Terms of Service and Privacy Policy.
- New commands: `/lunch_list`, `/drink`.
- Restaurants can be filtered by budget to exclude high-priced options.
