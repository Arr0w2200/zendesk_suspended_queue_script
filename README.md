## zendesk_suspended_queue_script
script to help manage suspended queue in zendesk though the deletion or recovery of tickets in the suspended queue


# You can run this project in two ways:
1. Using the provided batch file (easiest)

2. Manually setting environment variables and running the Python script

# Option 1 — Using the Batch File (Recommended)

1. Open the batch file: sqtool_run.bat
2. Locate the fields that need to be customized:
  * "PathToLogFile"
  * "Path to Project"
  * SET ZENDESK_SUBDOMAIN=SubDomain
  * SET ZENDESK_EMAIL=Email Associated With Token
  * SET ZENDESK_TOKEN=Zendesk Token
3. Save the file.
4. Run the batch file: sqtool_run.bat
  * This will: Set the required environment variables, activate the virtual environment, run the application, and log

# Option 2 - Run the Application Manually
1. Set up Environment
  * install python version 3.10.5 or newer
  * you'll need to install requests via command: pip install requests
2. Set up Environmental Variables
3. run projects via command: python sqtool.py
