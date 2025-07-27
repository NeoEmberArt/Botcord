# BOYKISSER.EXE


Setup Instructions
------------------

### 1\. Get your Discord Bot Token

-   Go to the Discord Developer Portal

[Developer portal](https://discord.com/developers/applications)

-   Select your bot application or create a new one

-   Under the **Bot** tab, copy the **Token**

-   Keep it private!

* * * * *

### 2\. Add `ALTOBOT_TOKEN` to Environment Variables

You need to provide your bot token to the bot securely via environment variables.

#### On Windows

Open Command Prompt and run:

cmd

Copy code

`setx ALTOBOT_TOKEN "YOUR_BOT_TOKEN_HERE"`

Then close and reopen your terminal or IDE to make sure the environment variable is loaded.


### RECOMENDED TO SET MANUALLY
[HOW TO SET ENV VARIABLES](https://www.youtube.com/watch?v=Z2k7ZBMZT3Y)

* * * * *

### 3\. Install Python and Required Modules

Make sure you have Python 3.8 or newer installed:


`python --version`

Then, install dependencies using `pip`:



```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, paste this into command prompt


```bash
pip install discord.py yt-dlp psutil
```



* * * * *

### 4\. Running the Bot

Run the main Python file that contains your bot code, e.g.:


```bash
cd c:/users/YOU/DOWNLOADSFOLDER/OR WHERE THE FILE IS

python bot.py
```

Make sure your environment variable `ALTOBOT_TOKEN` is set before running.
