# Creating a queuing system on Discord for Labs/Q&A

Date: 25 March 2020

## Overview

This document is a workflow for creating a queueing system on Discord for private 1-on-1 meetings between tutors and students.

We utilise the Python API for Discord, along with manually created roles and private channels in order to have private channels with automated permission assignment.

## Preliminaries

You will need to create a Discord account, if you do not already have one. The permissions for the bot will derive from your account.

## Creating the Bot

### The Experiment Table - Prerequisites

The script (`queuebot.py`) uses the discord.py and pyYAML libraries:

```
pip install -r requirements.txt
```

or similar.

The bot is adapted from [`stroupbslayen`'s `queue-bot`](https://github.com/stroupbslayen/Other-Discord-Bots-async/tree/master/queue-bot).

### The Inanimate Pieces - The Server

You will need to create a server on Discord, by using the "Add a Server" button on the left bar of the Discord application. Ignore the popup on creation that prompts you to add people to the server - this will be taken care of later.

### The Bolt of Lightning - Bot Token

1. Navigate to [`Discord Developer Applications`](https://discordapp.com/developers/applications) 
2. Create a `New Application`.
3. Name the application (canonically Queuebot)
4. Navigate to the `Bot` section on the left
5. Create a bot with `Add Bot` > `Yes, do it`.
6. `Copy` the token
7. Paste it into the final line of the script:
   - `client.run('YOUR_TOKEN_HERE')`
8. Navigate to the `OAuth2` section on the left
9. Enable the `bot` scope
10. Copy and paste the resulting url in the scopes section into a new tab/window of your browser
11. Add the bot to your server.

### It's ALIVE - Running the bot

Invokation from command line
```
python queuebot.py CONFIG_FILE_PATH [--noop]
```

Examples
```
python queuebot.py my_config.yml

> runs Queuebot with config options from my_config.yml

python queuebot my_config --noop

> prints configuration options
```

### Hunting Your Frankenstein - Performing Setup

We have provided automated setup with this bot.

1. Create the bot's role following the [specification](#Role:-Queuebot)
2. Assign the bot with the role
3. Send `!start` in a text channel

## Commands

Commands are used to interact with the bot. Some commands are restricted, and only available to users with the Tutor role (or similar, as specified in the script), and some are only available in specified channels.

| Command Invokation | Restricted | Available Channels | Effect | Notes | 
|:-:|:-:|:-:|:--------|:-|
| `!add` | No | all | Adds the invoking user to the end of the queue. Deletes the invoking message | |
| `!remove` | No | all | Removes the invoking user from the queue. Deletes the invoking message. | |
| `!position` | No | spam | Reports the invoking user's position in the queue. Deletes the invoking message | |
| `!queue` | No | spam | Reports the first five users in the queue. Deletes the invoking message | |
| `!next` | Yes | all | Pops the next person in the queue and sends a message into #queue mentioning them | deprecated, do not use|
| `!pull` | Yes | meeting room | Sends a message into #queue mentioning the next person in the queue and assigns them the role corresponding to the meeting room this command was invoked in | |
| `!bye` | Yes | meeting room | Removes the role corresponding to this meeting room for all users, and moves those users into the Waiting Room | |
| `!toggle` | Yes | all | Turns the queue on or off, and sends a message into #queue as well as the channel this command was invoked in regarding the state of the queue (ON or OFF) | |
| `!clear` | Yes | all | Clears the queue | |


## Info Box: Channels

Channels are sub-areas of Discord that allow for communication between people. There are two types of channels:

- Text channels
- Voice channels

Text channels are typically used for chat-style text communication (ala Slack, MS Teams) which are persistent (history of chat remains). They will also be used for interacting with the bot via text commands (text messages that begin with a particular, specified symbol that the bot parses). 

Voice channels are typically used as small rooms for voice calls. These channels also have the "Go Live" functionality which allow screen sharing.

## Specification

The permission model on Discord revolves around roles. Roles are sets of permissions that can be granted to individual users, that enable or prohibit them from performing certain actions.

### Roles

Roles are managed from `Dropdown next to the server name > Server Settings > Roles`. Roles can be added with the (+) symbol next to `Roles`. 

#### Role: @everyone

This is the baseline permission set. Recommended permissions (all others disabled):

- Change Nickname
- Read Text Channels an& See Voice Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use External Emojis
- Add Reactions
- Connect
- Speak
- Use Voice Activity

This baseline will allow them to communicate in any text or voice channel that does not otherwise restrict their actions.

#### Role: Tutor

Also: Admin, TA, Lecturer

Note: These should be listed in the configuration as `approved_roles`

This role is an admin role, and it is recommended to be granted all permissions, __except__:

- Allow anyone to @mention this role
- Ban Members
- Manage Nicknames

An elevated Admin role can be created to grant the latter two permissions (which can adversely affect student engagement)

#### Role: Queuebot

Also: Name that you gave the bot

Note: This role may be automatically created with the bot. You will need to move this role above any of the roles you create below in the [Meeting Rooms section](#meeting-rooms).

Permissions:

All except

- Allow anyone to @mention this role
- Administrator

This will allow the bot to perform its duties.

### Channels

Channel permissions can be modified via `right-clicking the channel > Edit Channel > Permissions`

#### Text Channels

##### Channel: welcome

Also: rules

Type: text, public

Permissions:

- @everyone: (all others disabled - `X`)
  - Read Messages
  - Read Message History

This will allow only roles with the `Administrator` permission to post in the channel

##### Channel: queue

Type: text, public

`Overview` Settings: Slowmode 15s

Slowmode means that students are encouraged to use it for only queue-related commands

##### Channel: spam

Type: text, public

`Overview` Settings: Slowmode 5s

##### Channel: chatter

Type: text, public

Permissions:

- @everyone: (all others disabled - `X`)
  - Read Messages
  - Send Messages
  - Embed Links
  - Attach Files
  - Read Message History
  - Use External Emojis
  - Add Reactions

Geared as a general text comms channel

##### Channel: admin

Also: test

Type: text, private

Permissions:

- @everyone:
  - Read Messages disabled `X`
- Queuebot:
  - Read Messages
  - Send Messages
  - others on `/`
- Tutor:
  - Read Messages
  - others on `/`

#### Voice Channels

##### Channel: Waiting Room

Type: voice, public

Permissions:

- @everyone:
  - View Channel
  - Connect
  - others disabled `X`

### Meeting Rooms

Each meeting room is a pair of channels that are named identically. It is recommended to separate the meeting room channels in a separate, new Category (right click on channels list > Create Category).

Canonically, we will name them with the Greek alphabet, feel free to choose the names of the channels.

You will also need to create appropriate roles for these meeting rooms (one role per meeting room set).

For this documentation, we will use the name `alpha`.

#### Role: Alpha

Permissions:

- Use Voice Activity
- Go Live

Note: one per meeting room set (this gets tedious).

#### Meeting Room Text Channel: alpha

Type: text, private

Permissions:

- @everyone:
  - Read Messages disabled `X`
- Tutor:
  - Read Messages
- Queuebot:
  - Read Messages
- Alpha:
  - Read Messages
  - Send Messages
  - Embed Links
  - Attach Files
  - Add Reactions
  - __disabled__ (`X)`
    - Read Message History

#### Meeting Room Voice Channel: alpha

Type: voice, private

Overview:

- User Limit: 2

Permissions:

- @everyone: all __disabled__
- Alpha:
  - __enabled__:
    - View Channel
    - Connect
    - Speak
    - Use Voice Activity
    - Go Live
  - __disabled__:
    - Create Invite
    - Manage Channel
    - Manage Permissions
    - Manage Webhooks
    - Mute Members
    - Deafen Members
    - Move Members
- Queuebot
  - View Channel
  - Move Members
- Tutor: all __enabled__