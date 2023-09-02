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
import sys
import os

## Third-party library imports


## Custom library imports
import appSetup
import encodeMedia

## Variables ##
projectPath                     = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
handBrakeCLIDir                 = projectPath + "/Downloads/"
handBrakeFlatPakPath            = handBrakeCLIDir + "HandBrakeCLI-1.6.1-x86_64.flatpak"
handBrakeFlatPakGit             = "https://github.com/HandBrake/HandBrake/releases/download/1.6.1/HandBrake-1.6.1-x86_64.flatpak"
handbrakeSHA256                 = "b96fe8b363be2398f62efc1061f08992f93f748540f30262557889008b806009"
handBrakeProfile                = " --preset-import-gui Plex-HD.json --crop-mode none"
regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                      = projectPath + "/config.ini"

## Functions
def main():
    # Run the app requirements setup
    print("Setting up requirements")
    setup       = appSetup.appRequirements(s3Bucket, s3ConfigFile, handBrakeCLIDir)

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
        encodeMedia.encodeMedia(s3Media, movies, shows, others, plexHost, handBrakeProfile, regularExpPattern, encodingExt, encodingRString, encodedExt)
    else:
        # Else exit
        print("Failed to download Handbrake. Aborting!")
        sys.exit()


## Main entry point
if __name__ == "__main__":
    main()