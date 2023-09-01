# /usr/bin/python3
## Script to automate the process of encoding and coping files

## Imports ##
import os
import re
import shutil
import subprocess
import sys
import requests
from colorama import Back, Fore, Style
from configparser import ConfigParser

## Variables ##
projectPath                     = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
userProfile                     = os.environ["HOME"]
plexMedia                       = {"plexMount": "/Volumes/plex"}
baseMediaPath                   = userProfile + "/Movies/PlexMedia/MKV/"
localMedia                      = {
    "movieSource"                   : baseMediaPath + "Movies/",
    "tvSource"                      : baseMediaPath + "TV/",
    "otherSource"                   : baseMediaPath + "Other/",
    "moviePlexDestination"          : plexMedia["plexMount"] + "/Movies/",
    "tvPlexDestination"             : plexMedia["plexMount"] + "/TV/",
    "otherPlexDestination"          : "",
    "movieEncodeDestination"        : "/Users/tylerwasick/Movies/PlexMedia/Encoded/Movies/",
    "tvEncodeDestination"           : "/Users/tylerwasick/Movies/PlexMedia/Encoded/TV/",
    "otherEncodeDestination"        : "/Users/tylerwasick/Movies/PlexMedia/Encoded/Other/",
}
movies                          = []
shows                           = []
others                          = []
encodingExt                     = (".mkv", ".mp4", ".m4v")
encodingRString                 = ".mp4.mkv.m4v"
encodedExt                      = ".m4v"
handBrakeCLIDir                 = projectPath + "/Downloads/"
handBrakeCLIPath                = handBrakeCLIDir + "HandBrakeCLI-1.6.1.dmg"
handBrakeCLIExtracted           = handBrakeCLIDir + "HandBrakeCLI-1.6.1" + "/" + "HandBrakeCLI"
handBrakeURL                    = "https://github.com/HandBrake/HandBrake/releases/download/1.6.1/HandBrakeCLI-1.6.1.dmg"
handbrakeSHA256                 = "b96fe8b363be2398f62efc1061f08992f93f748540f30262557889008b806009"
handBrakeProfile                = " --preset-import-gui Plex-HD.json --crop-mode none"
regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                      = projectPath + "/config.ini"
config                          = ConfigParser()
sevenZipParams                  = "7zz x " + handBrakeCLIPath + " -o" + handBrakeCLIDir

## TODO:Guard if already running, exit
## TODO: Extract subtitles
## TODO: Place Movies in folders

## Functions ##
##TODO: Read a config file for locations
def loadSettings():
    # Check if 7Zip is installed, if not install it
    def check_7zip_installed():
        try:
            subprocess.check_output(['7zz'])

        except OSError:
            subprocess.call(['brew', 'install', 'sevenzip'])

    check_7zip_installed()

#    # Check for config file
#    print(Fore.GREEN + "Loading settings")
#    # If present load,
#    if os.path.exists(configFile):
#        print("Settings loaded successfully")
#        print(config.read("config.ini"))
#        localMedia.update({"movieSource": config.get("local-media", "movieSource")})
#        # print(movieSource)

#    else:
#        # If not prompt questions to create
#        print(
#            Fore.WHITE
#            + "Settings not found, promptings will follow to create the settings file."
#        )
#        print("Select the base path for MKV files:")
#        # mkvFiles = promptlib.filedialog.askdirectory(title="Select MKV Folder")
#        print("Select the base path for Encoded files:")

#    # Reset style
#    print(Style.RESET_ALL)


## Download HandBrakeCLIDir is n ot already downloaded
def downloadHandbrake() -> bool:
    ## TODO Verify hash of the download
    # Check if "HandBrakeCLIDir" is  downloaded already, if so return true
    if os.path.isfile(handBrakeCLIExtracted):
        return True  # Exit successfully

    # Verify the "Download" path exists, if so proceed to download handbrake
    elif os.path.exists(handBrakeCLIDir):
        ## TODO: Refactor
        # Download HandBrakeCLIDir
        download = requests.get(handBrakeURL)
        open(handBrakeCLIPath, "wb").write(download.content)

        # Verify the download exists
        if os.path.exists(handBrakeCLIPath):
            # Extract download to allow access 
            subprocess.call(sevenZipParams, shell=True)

            if os.path.isfile(handBrakeCLIExtracted):
                return True  # Exit successfully
            else:
                return False
        else:
            return False  # Exit with errors

    # If the path does not exist, create it and verify it does exist.
    else:
        os.makedirs(handBrakeCLIDir)
        # Verify the folder was created, else exit with error
        if os.path.exists(handBrakeCLIDir):
            return False  # Exit with errors

        # Download HandBrakeCLIDir
        else:
            ## TODO: Refactor
            # Download HandBrakeCLIDir
            download = requests.get(handBrakeURL)
            open(handBrakeCLIPath, "wb").write(download.content)

            # Verify the download exists
            if os.path.exists(handBrakeCLIPath):
                # Extract download to allow access 
                subprocess.call(sevenZipParams, shell=True)

                # Verify the dmg was extracted
                if os.path.isfile(handBrakeCLIExtracted):
                    return True  # Exit successfully
                else:
                    return False
                
            else:
                return False  # Exit with errors


## Encode media
def encodeMedia():
    # Loop through all media types (3 folders)
    for counter in range(3):
        # Set source and destination dir for relevant content
        if counter == 0:  # Movies
            sourceDirectory = localMedia["movieSource"]
            destinationDirectory = localMedia["movieEncodeDestination"]
            plexDestination = localMedia["moviePlexDestination"]
            movieList = movies

        elif counter == 1:  # TV Shows
            sourceDirectory = localMedia["tvSource"]
            destinationDirectory = localMedia["tvEncodeDestination"]
            plexDestination = localMedia["tvPlexDestination"]
            movieList = shows

        else:  # Other Movies
            sourceDirectory = localMedia["otherSource"]
            destinationDirectory = localMedia["otherEncodeDestination"]
            plexDestination = localMedia["otherPlexDestination"]
            movieList = others

        ## Process Shows ##
        ## Iterate over the source directory
        for dirContent in os.listdir(sourceDirectory):
            # Join the contents (files and folders) to the original path
            path = os.path.join(sourceDirectory, dirContent)

            # If the file ends with an extension that can be encoded,
            # add to the "movies" list
            if os.path.isfile(path):
                if path.endswith(encodingExt):
                    movieList.append(dirContent)
                    print(f"File found: {dirContent}, file added")

                # Else the file is not supported
                else:
                    print(f"File is not supported {dirContent}")

            # Else the path is a folder, do not proceed with scanning
            else:
                print(f"Folder found: {dirContent}, will not process")

        # Sort through the list alphabetically
        movieList.sort()

        # Loop through the list of movies, encode the movie then copy to the
        # appropriate destination
        for movie in movieList:
            # Remove the file extension before encoding then add the new file
            # extension for the destination
            destinationFile = movie.rstrip(encodingRString)

            # Concatenate the destination file name with the destination path
            destinationFileName = destinationDirectory + destinationFile + encodedExt

            # Set the source file destination by concatenating the source path to the file name
            sourceFileName = sourceDirectory + movie

            # Create the process call
            handBrakeCall = (
                handBrakeCLIExtracted
                + handBrakeProfile
                + " -i "
                + f'"{sourceFileName}"'
                + " -o "
                + f'"{destinationFileName}"'
            )

            # Run the file into HandBrake
            returned_value = subprocess.call(handBrakeCall, shell=True)
            fileExists = os.path.isfile(destinationFileName)

            # Check if the destination file exists, and is not 0k, if so proceed
            if returned_value == 0 and fileExists:
                # Check is SMB connection to plex exists, if not open one
                plexShareExists = os.path.exists(plexMedia["plexMount"])
                if plexShareExists is False:
                    os.system("osascript -e 'mount volume \"smb://10.0.0.202/plex\"'")

                # Verify the share exists, if not exit the program as there is an issue
                # mapping the share
                plexShareExists = os.path.exists(plexMedia["plexMount"])
                if plexShareExists is False:
                    print("Issue mapping share, aborting!")
                    break

                # Copy the encoded file to the destination (Plex Media Server)
                if counter == 0:  # If movies, simply copy
                    copySuccessful = shutil.copy(destinationFileName, plexDestination)
                    print(copySuccessful)

                # Elif TV Shows, we need to parse where they will be copies to
                elif counter == 1:
                    # Use regex to parse the string into groups we can use for coping
                    result = re.match(regularExpPattern, destinationFile)
                    showName = result.group(1)
                    season = "Season " + result.group(2)
                    plexDestination = localMedia["tvPlexDestination"]  # Reset plex destination

                    # Update the path variable with the Show Name
                    plexDestination += showName

                    # Check if the show folder exists, if not create one
                    pathExists = os.path.exists(plexDestination)
                    if not pathExists:
                        # If path does not exist, create folder
                        os.mkdir(plexDestination)

                    # Update the path variable with the Show Name
                    plexDestination += "/" + season

                    # Checks if the season folder exists, if not creates one
                    pathExists = os.path.exists(plexDestination)
                    if not pathExists:
                        # If path does not exist, create folder
                        os.mkdir(plexDestination)

                    # Copy the file the encoded directory to the Plex destination
                    copySuccessful = shutil.copy(destinationFileName, plexDestination)
                    print(copySuccessful)

                # Remove files from source after copy (if all previous steps were successful)
                os.remove(sourceFileName)

            # Else print error and continue to next file
            else:
                print("File was not encoded")
                continue  # Continue to the next


if __name__ == "__main__":
    loadSettings()
    download = downloadHandbrake()
    if download:
        encodeMedia()
else:
    print("Failed to download Handbrake. Aborting!")
