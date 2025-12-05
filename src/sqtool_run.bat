@echo off
echo sqtool was run on %DATE% at %TIME% >> "PathToLogFile"
REM Change the directory to the path containing the virtual environment
cd "Path to Project"
REM Activate virtual environment
call .venv\Scripts\activate.bat
REM move to folder that contains file, set environmental variables, and run script
cd src
SET ZENDESK_SUBDOMAIN=SubDomain
SET ZENDESK_EMAIL=Email Associated With Token
SET ZENDESK_TOKEN=Zendesk Token
python sqtool.py
REM deactivate environment
cd ..
call .venv\Scripts\deactivate.bat
