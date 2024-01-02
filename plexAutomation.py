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
Version History     :
09/01/2023          : Initial Release
"""

## Standard library imports
import configparser
import requests
import shutil
import sys
import os
from pid import PidFile

## Third-party library imports


## Custom library imports
import scripts.appSetup as appSetup
import scripts.encodeMedia as encodeMedia

## Variables ##
projectPath                     = BASE_DIR = os.path.dirname(os.path.abspath(__file__))
userProfile                     = os.environ["HOME"]
plexMedia                       = {"plexMount": "/Volumes/plex"}
plexHost                        = "vpn.tylerwasick.com"
s3Bucket                        = "s3://plexutil/"
s3ConfigFile                    = "~/.s3cfg"
s3Media                         = {
    "movieSource"                   : s3Bucket + "Movies/",
    "tvSource"                      : s3Bucket + "TV/",
    "otherSource"                   : s3Bucket + "Other/",
    "moviePlexDestination"          : "/plex/Movies/",
    "tvPlexDestination"             : "/plex/TV/",
    "otherPlexDestination"          : "",
    "movieEncodeDestination"        : "/plextemp/Encoded/Movies/",
    "tvEncodeDestination"           : "/plextemp/Encoded/TV/",
    "otherEncodeDestination"        : "/plextemp/Encoded/Other/",
    "archiveDestination"            : s3Bucket + "Archived/",
    "movieTmpDestination"           : "/plextemp/Temp/Movies/",
    "tvTmpDestination"              : "/plextemp/Temp/TV/",
    "otherTmpDestination"           : "/plextemp/Temp/Other/"
}
movies                          = []
shows                           = []
others                          = []
encodingExt                     = (".mkv", ".mp4", ".m4v")
encodingRString                 = ".mp4.mkv.m4v"
encodedExt                      = ".m4v"
handBrakeCLIDir                 = projectPath + "/downloads/"
handBrakeFlatPakPath            = handBrakeCLIDir + "HandBrakeCLI-1.6.1-x86_64.flatpak"
handBrakeFlatPakGit             = "https://github.com/HandBrake/HandBrake/releases/download/1.6.1/HandBrake-1.6.1-x86_64.flatpak"
handbrakeSHA256                 = "b96fe8b363be2398f62efc1061f08992f93f748540f30262557889008b806009"
handBrakeProfile                = " --preset-import-gui settings/Plex-HD.json --crop-mode none"
regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                      = projectPath + "/settings/config.ini"
configFileGitURL                = "https://raw.githubusercontent.com/tylerwasick/Plex-Automation/main/config.ini"

## Functions
def main():
    # Check if the config file exists
    if os.path.isfile(configFile):
        print("Config file exists")
        print(configFile)
        
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

        # Prompt the user for the information and create the config file
    
    
    
    # Run the app requirements setup
    print("Setting up requirements")
    setup = appSetup.appRequirements(s3Bucket, s3ConfigFile, handBrakeCLIDir)

    if setup:
        print("App requirement setup complete")

    else:
        print("App requirement setup failed")
        sys.exit()

    # Download Handbrake
    download = appSetup.downloadHandbrake(handBrakeCLIDir, handBrakeFlatPakPath, handBrakeFlatPakGit)

    # Verify Handbrake downloads successfully 
    if download:
        # If successful, encode media
        print("Encoding media")
        # encodeMedia.encodeMedia(s3Media, movies, shows, others, plexHost, handBrakeProfile, regularExpPattern, encodingExt, encodingRString, encodedExt)
    else:
        # Else exit
        print("Failed to download Handbrake. Aborting!")
        sys.exit()


## Main entry point
if __name__ == "__main__":
    # Check if the script is already running
    with PidFile(piddir="."):
        try:
            main()

        except Exception as e:
            print(f"An error occurred: {e}")