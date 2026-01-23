# Deployment with Dockge

If Dockge isn't picking up the git repo automatically, you can paste this directly into the **Editor** (Compose) area:

```yaml
services:
  eldric-bot:
    # Build directly from the GitHub URL
    build: https://github.com/raciallyMotivatedApplications/shittyDiscordBot369.git#master
    container_name: eldric-alarm-bot
    restart: unless-stopped
    environment:
      # PASTE YOUR TOKEN HERE
      - DISCORD_TOKEN=your_token_here
```

## Steps
1. Copy the YAML above.
2. Paste it into your Dockge stack editor.
3. Replace `your_token_here` with your actual Bot Token.
4. Click **Deploy**.

Docker will automatically pull the code from GitHub, build the container (installing FFmpeg), and start it.
