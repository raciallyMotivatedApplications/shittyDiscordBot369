# Deployment with Dockge

1.  **Git URL**: Use your repository URL in Dockge:
    `https://github.com/raciallyMotivatedApplications/shittyDiscordBot369`

2.  **Compose File**: Dockge should automatically detect the `compose.yaml`.

3.  **Environment Variables**:
    - In Dockge, find the `environment` section or the `.env` editor.
    - Add your Token:
      ```
      DISCORD_TOKEN=your_token_here
      ```

4.  **Deploy**: Click "Deploy" or "Start". 
    - Dockge will build the Docker image (installing FFmpeg and Python packages) and start the bot.
