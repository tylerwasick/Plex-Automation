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
connectionType                  = ["smb", "s3", "scp", "local"]
mediaSettings                   = {
    "movieSource"                   : "",
    "moviesDestination"             : "",
    "otherDestination"              : "",
    "otherSource"                   : "",
    "plexMovies"                    : "",
    "plexTV"                        : "",
    "remoteConnectionType"          : "local",
    "sourceConnectionType"          : "local",
    "tvDestination"                 : "",
    "tvSource"                      : ""
}
handbrakeSettings               = {
    "handBrakeProfile"              : " --preset-import-gui Plex-HD.json --crop-mode none"
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

    # Verify the config file has the required values
    

        
        # Write the changes to the config file

        # Verify the changes were written successfully

## Main entry point
if __name__ == "__main__":
    loadConfig("settings/config.ini")