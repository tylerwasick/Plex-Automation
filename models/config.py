# /usr/bin/python3

"""
Script Name         : config.py
Description         : Manages the configuration of the Plex Automation scripts.
Author              : Tyler Wasick (github.com/tylerwasick)
Date                : 09/03/2023
=======================================================================================
Version History     :
09/01/2023          : Initial Release
"""

## Standard library imports
import configparser
import requests
import sys
import os

## Third-party library imports


## Custom library imports
import connectionInfo

## Variables
config                          = configparser.ConfigParser()
connectionType                  = ["local", "smb", "s3", "scp"]
mediaSettings                   = {
    "movieMKVSource"                : "",
    "movieEncodedDestination"       : "",
    "movieTempDestination"          : "",
    "otherEncodedDestination"       : "",
    "otherSource"                   : "",
    "otherTempLocation"             : "",
    "plexMovies"                    : "",
    "plexTv"                        : "",
    "tvEncodedDestination"          : "",
    "tvSource"                      : "",
    "tvTempLocation"                : "",
    "remoteConnectionType"          : "local",
    "sourceConnectionType"          : "local"
}
handbrakeSettings               = {
    "handBrakeProfile"              : "--preset-import-gui Plex-HD.json --crop-mode none"
}


## Classes
## TODO: Add the following logic for verification
##          - Verify the source locations for each folder are unique
##          - Verify the destination locations for each folder are unique
##          - 
# Class to hold the Plex Media Server configuration
class PlexMediaConfig:
    def __init__(self, 
                 plexMovies, 
                 plexTV):
        self.plexMovies             = plexMovies
        self.plexTV                 = plexTV

# Class to hold the media settings config
class MediaSettingsConfig:
    def __init__(self,
                 movieSource, 
                 tvSource, 
                 otherSource, 
                 moviesDestination, 
                 tvDestination, 
                 otherDestination,
                 remoteConnectionType: connectionInfo.ConnectionTypes,
                 sourceConnectionType: connectionInfo.ConnectionTypes,
                 sourceMount,
                 plexMount):
        self.movieSource            = movieSource
        self.tvSource               = tvSource
        self.otherSource            = otherSource
        self.moviesDestination      = moviesDestination
        self.tvDestination          = tvDestination
        self.otherDestination       = otherDestination
        self.remoteConnectionType   = remoteConnectionType
        self.sourceConnectionType   = sourceConnectionType
        self.sourceMount            = sourceMount
        self.plexMount              = plexMount
          
class handbrake:
    def __init__(self,
                 handBrakeProfile):
          self.handBrakeProfile         = handBrakeProfile

## Functions
def loadConfig(configFile) -> bool:

    # Local variables
    validConfig                 = True
    
    # Check if the config file exists
    if os.path.isfile(configFile):
        print("Config file exists: " + configFile)
        
    else:
        # If file does not exist, create the config file
        print("Config file does not exist. Creating config file.")
        config["media-settings"]    = mediaSettings
        config["handbrake"]         = handbrakeSettings

        # Save file to the project directory
        with open(configFile, "w") as file:
            config.write(file)

        # Verify the file was created
        if os.path.isfile(configFile):
            print("Config file created successfully")
        else:
            print("Failed to create config file. Aborting!")
            sys.exit()


    # Read the config file
    config.read(configFile)

    # Verify media-settings in config file
    for key in config["media-settings"]:
        # If the value is empty, set the config validation variable to False 
        if not config["media-settings"][key]:
            validConfig = False

    # If there are values missing in the config file, initiate the setup process
    if not validConfig:
        
        # Prompt the user for Plex connection information
        inputMessage        = "Please select the method of which the script will be using to upload files your Plex server:\n"
        userInput           = ""

        for index, item in enumerate(connectionType):
            inputMessage += f'{index+1}) {item}\n'

        inputMessage += 'Please select: '

        while (userInput not in "1"):
            userInput = input(inputMessage)
            if userInput.isdigit():
                print('Plex connection set to: ' + connectionType[int(userInput) - 1]) #dev
            
            else:
                print('Plex connection set to: ' + userInput) #dev
        
        # Prompt the user for the source type for media that is to be encoded

        # If the source is "local", set temp locations to "local"

        # Else if source is "SMB", prompt the user for the SMB connection information

        # Else if source is "S3", prompt the user for the S3 connection information

        # Else if source is "SCP", prompt the user for the SCP connection information

        # TODO: Validate the connection

        # Write the changes to the config file

    # Verify handbrake in config file
    if config["handbrake"]["handBrakeProfile"] == "":
        # Prompt user if they wish to use the default options, or set a profile
        result = input("Handbrake profile not set. Would you like to use the default profile? (Y/n)")
        
        # If the user responded with "y", "Y", or a return value, use the default profile
        if result == "" or result == "Y" or result == "y":
            print("Using default profile")
            config["handbrake"]["handBrakeProfile"] = "--preset-import-gui Plex-HD.json --crop-mode none"
        
        # Else, prompt the user to enter a profile
        else:
            print("Please enter a handbrake profile")
            config["handbrake"]["handBrakeProfile"] = input("Handbrake profile: ")

        # Write the changes to the config file
        with open(configFile, "w") as file:
            config.write(file)

        # Verify the changes were written successfully
        if os.path.isfile(configFile):
            print("Config file updated successfully")
        else:
            print("Failed to update config file. Aborting!")
            sys.exit()

## Main entry point
if __name__ == "__main__":
    loadConfig("settings/config.ini")