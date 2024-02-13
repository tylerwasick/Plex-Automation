# /usr/bin/python3

"""
Script Name         : plexAutomation.py
Version             : 0.1.0
Description         : Python scripts to help automate the process of
                      encoding media files and transferring to your Plex Media Server.
Author              : Tyler Wasick (github.com/tylerwasick)
Date                : 09/01/2023
License             : GNU General Public License v3.0
Site                : https://github.com/tylerwasick/Plex-Automation
=======================================================================================
"""

## Standard library imports
import configparser
import sys
import os

## Third-party library imports


## Custom library imports
import scripts.appSetup as appSetup
# import scripts.encodeMedia as encodeMedia

## Variables
debugLevel                      = 5
projectPath                     = BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# movies                          = []
# shows                           = []
# others                          = []
# encodingExt                     = (".mkv", ".mp4", ".m4v")
# encodingRString                 = ".mp4.mkv.m4v"
# encodedExt                      = ".m4v"
handBrakeCLIDir                 = projectPath + "/downloads/"
# regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                      = "settings/config.ini"
missingItems                    = []

## Functions
def main():
   # Load the config file and parse the values 
    configLoader()
    
    # Setup the requirements
    print("Setting up requirements") if debugLevel >= 3 else None

    handbrakeInstalled = appSetup.appRequirements.handbrakeInstalled()
    
    # Verify Handbrake downloads successfully 
    if handbrakeInstalled:
        # If successful, encode media
        print("App requirements setup complete") if debugLevel >= 3 else None
        print("Encoding media")
        # encodeMedia.encodeMedia(s3Media, movies, shows, others, plexHost, handBrakeProfile, regularExpPattern, encodingExt, encodingRString, encodedExt)
    else:
        # Else exit
        print("Failed to download Handbrake. Aborting!")
        sys.exit(20)

# Load the config file and parse the values
def configLoader():
    # This tells Python that we want to use the global variable, not a new local variable
    global missingItems

    # Check if the config file exists
    if os.path.isfile(configFile):
        print("Config file exists") if debugLevel >= 3 else None
    
    # If file does not exist, exit the script
    else:
        print("Config file does not exist, please create and update the config.ini file. Exiting!")
        sys.exit(1)
    
    # Load the config file and parse the values
    config = configparser.ConfigParser()

    # Verify the config file is loaded and all values are present 
    config.read(configFile)
    print("Config file loaded") if debugLevel >= 3 else None

    # Verify all required values are present
    required_items = {
        "plex-media" : ["plexMount", "plexMovies", "plexTV", "plexOther"],
        "source-media" : ["movieSource", "tvSource", "otherSource"],
        "encoding-settings" : ["handbrakeProfile"]
    }
    
    # Check that all required items are present
    # Loop over all of the required fields
    for item in required_items:
        # Loop over each section
        for section in required_items[item]:
            # Check if the item is present
            print(f"Checking for {section}") if debugLevel >= 4 else None

            # Get the value for the section and item
            returnedItem = (config.get(item, section)).replace('"','')
            print(returnedItem) if debugLevel >= 4 else None
            
            # If the item is empty, add to the missing items list
            if returnedItem == "":
                # Add missing item to the list
                missingItems.append(section)

    if len(missingItems) == 0:
        print("All required items are present") if debugLevel >= 3 else None
    
    else:
        # Print missing items
        print("The following items are missing from the config file:")
        
        for item in missingItems:
            print(item)

        # Exit the script
        print("Exiting!")
        sys.exit(2)
    
## Main entry point
if __name__ == "__main__":
    
    print("Starting Plex Automation")
    main()
    