requires an events channel

![events](events.png)

Intended to be called from events channel (the message will be automatically cleaned up)
```
?event
```

Follow DM prompts

![Animated GIF](preview.gif)

React on the automatically generated :one: and :two: reactions to join / quit a team. Team members generated and inserted on the roster in the message dynamically.

![Animated GIF](readme.gif)

## Running with windows 

Windows: Make a directory EventBot and within it clone the repo:

```sh
mkdir EventBot
cd EventBot
git clone https://github.com/sockheadrps/EventBot.git
```

Go back up a directory and intialize the startup batch file

```sh
cd ..
echo. > run.bat
```

Paste the following code into run.bat, filling in the "TOKEN=" and "EVENT_CHANNEL="
```sh
@echo off
setlocal

set "TOKEN=YOUR_TOKEM"
set "EVENT_CHANNEL=YOUR_EVENT_CHANNEL_ID"


echo Checking for updates
cd EventBot
call git pull
call entrypoint.bat
pause
endlocal
```

Double click run.bat or 
```sh
run.bat
```


