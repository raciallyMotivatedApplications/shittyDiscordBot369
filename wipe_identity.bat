@echo off
echo ==========================================
echo      GIT IDENTITY WIPER
echo ==========================================
echo.
echo This will destroy the .git folder and create a new one
echo with "Anonymous" as the author.
echo.

echo Removing old git history...
rd /s /q .git

echo Initializing new git repo...
git init

echo Configuring Anonymous Identity...
git config user.name "Anonymous"
git config user.email "anonymous@example.com"

echo Adding files...
git add .
git commit -m "Initial commit"

echo Re-connecting to GitHub...
git remote add origin https://github.com/raciallyMotivatedApplications/shittyDiscordBot369.git

echo.
echo Please enter your GitHub Personal Access Token to force push:
set /p token="Token: "

echo Pushing...
git remote set-url origin https://%token%@github.com/raciallyMotivatedApplications/shittyDiscordBot369.git
git push --force -u origin master

echo.
echo Done! Your commit history is now anonymized.
pause
