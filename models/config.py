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


## Variables

## Classes
# Class to hold the Plex Media Server configuration
class PlexMediaConfig:
    def __init__(self, 
                 plexMount, 
                 plexMovies, 
                 plexTV):
        self.plexMount              = plexMount
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
                 remoteConnectionType,
                 sourceConnectionType):
        self.movieSource              = movieSource
        self.tvSource                 = tvSource
        self.otherSource              = otherSource
        self.moviesDestination        = moviesDestination
        self.tvDestination            = tvDestination
        self.otherDestination         = otherDestination
        self.remoteConnectionType     = remoteConnectionType
        self.sourceConnectionType     = sourceConnectionType
          
class handbrake:
    def __init__(self,
                 handBrakeProfile):
          self.handBrakeProfile         = handBrakeProfile

## Functions
def loadConfig(configFile, configFileGitURL) -> bool:
    # Check if the config file exists
    if os.path.isfile(configFile):
        print("Config file exists: " + configFile)
        
    else:
        # If file does not exist, create the file with a template from Github
        print("Config file does not exist, creating one")
        request = requests.get(configFileGitURL, allow_redirects=True)

        # Save file to the project directory
        open(configFile, 'wb').write(request.content)

        # Verify the file was created
        if os.path.isfile(configFile):
            print("Config file created successfully")
        else:
            print("Failed to create config file. Aborting!")
            sys.exit()

    # Load the config file and parse the values
    config = configparser.ConfigParser()

    # Read the config file

    # Verify the config file was read successfully

    # Verify the config file has the required values

        # Else, prompt the user for the information and create the config file

        
        # Write the changes to the config file

        # Verify the changes were written successfully

## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")