#/usr/bin/python3
## Script to automate the process of encoding and coping files

## Imports ##
import os
import re
import shutil
import subprocess
import promptlib
import requests
from colorama import Back, Fore, Style
from configparser import ConfigParser


## Variables ##
projectPath                 = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
userProfile                 = (os.environ['HOME'])
localMedia                  = {
    "movieSource":          "",
    "tvSource":             "",
    "otherSource":          "",
    "moviesDestination":    "",
    "tvDestination":        "",
    "otherDestination":     ""
}
plexMedia                   = {
    "plexMount"             : "",
    "plexMovies"            : "",
    "plexTV"                : ""
}
movies                      = []
shows                       = []
others                      = []
encodingExt                 = ('.mkv', '.mp4', '.m4v')
encodingRString             = ".mp4.mkv.m4v"
encodedExt                  = ".mp4"
handBrakeCLI                = projectPath + "/Downloads"
handBrakeURL                = "https://github.com/HandBrake/HandBrake/releases/download/1.6.1/HandBrakeCLI-1.6.1.dmg"
handbrakeSHA256             = "b96fe8b363be2398f62efc1061f08992f93f748540f30262557889008b806009"
handBrakeProfile            = None
regularExpPattern           = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                  = projectPath + "/config.ini"
config                      = ConfigParser()

## TODO:Guard if already running, exit
## TODO: Extract subtitles
## TODO: Place Movies in folders

## Functions ##
##TODO: Read a config file for locations
def loadSettings():
    # Check for config file
    print(Fore.GREEN + "Loading settings")
    # If present load, 
    if os.path.exists(configFile):
        print("Settings loaded successfully")
        print(config.read('config.ini'))
        localMedia.update({"movieSource": config.get('local-media', 'movieSource')})
        #print(movieSource)
        
    else:
        # If not prompt questions to create
        print(Fore.WHITE + "Settings not found, promptings will follow to create the settings file.")
        print("Select the base path for MKV files:")
        #mkvFiles = promptlib.filedialog.askdirectory(title="Select MKV Folder")
        print("Select the base path for Encoded files:")
        
    # Reset style
    print(Style.RESET_ALL)


## Download HandBrakeCLI is not already downloaded
def downloadHandbrake() -> bool:

    ## TODO Verify hash of the download
    # Check if "HandBrakeCLI" is downloaded already, if so return true
    if os.path.isfile(handBrakeCLI):
        return True         # Exit successfully

    # Verify the "Download" path exists, if so proceed to download handbrake
    elif os.path.exists(downloadsPath):
        # Download HandBrakeCLI
        download = requests.get(handBrakeURL)
        open(handBrakeCLI, "wb").write(download.content)
        # Verify the download exists
        if os.path.exists(handBrakeCLI):
            return True     # Exit successfully
        else:
            return False    # Exit with errors
    
    # If the path does not exist, create it and verify it does exist.
    else:
        os.makedirs(downloadsPath)
        # Verify the folder was created, else exit with error
        if os.path.exists(downloadsPath):
            return False    # Exit with errors
        
        # Download HandBrakeCLI
        else:
            download = requests.get(handBrakeURL)
            open(handBrakeCLI, "wb").write(download.content)
            # Verify the download exists
            if os.path.exists(handBrakeCLI):
                return True     # Exit successfully
            else:
                return False    # Exit with errors

## Encode media
def encodeMedia():
    # Loop through all media types (3 folders)
    for counter in range(3): 

        # Set source and destination dir for relevant content
        if counter == 0:    # Movies
            sourceDirectory         = movieSource
            destinationDirectory    = moviesDestination
            plexDestination         = plexMovies
            movieList               = movies

        elif counter == 1:  # TV Shows
            sourceDirectory         = tvSource
            destinationDirectory    = tvDestination
            plexDestination         = plexTV
            movieList               = shows

        else:               # Other Movies
            sourceDirectory         = otherSource
            destinationDirectory    = otherDestination
            plexDestination         = ""
            movieList               = others


        ## Process Shows ##
        ## Iterate over the source directory
        for dirContent in os.listdir(sourceDirectory):

            # Join the contants (files and folders) to the original path
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
            
            # Concatinate the destination file name with the destination path
            destinationFileName = destinationDirectory + destinationFile + encodedExt

            # Set the source file destination by concatinating the source path to the file name
            sourceFileName = sourceDirectory + movie

            # Create the process call
            handBrakeCall = handBrakeCLI + handBrakeProfile + " -i " + f'"{sourceFileName}"' + " -o " + f'"{destinationFileName}"'

            # Run the file into HandBrake
            returned_value = subprocess.call(handBrakeCall, shell=True)
            fileExists = os.path.isfile(destinationFileName)

            # Check if the destination file exists, and is not 0k, if so proceed
            if (returned_value == 0 and fileExists):
                
                # Check is SMB connection to plex exists, if not open one
                plexShareExists = os.path.exists(plexMount)
                if plexShareExists is False:
                    os.system("osascript -e 'mount volume \"smb://10.0.0.202/plex\"'")

                # Verify the share exists, if not exit the program as there is an issue 
                # mapping the share 
                plexShareExists = os.path.exists(plexMount)
                if plexShareExists is False:
                    print("Issue mapping share, aborting!")
                    break

                # Copy the encoded file to the destination (Plex Media Server)
                if counter == 0:        # If movies, simply copy
                    copySuccessful = shutil.copy(destinationFileName, plexDestination)
                    print(copySuccessful)

                elif counter == 1:      # Elif TV Shows, we need to parse where they will be copies to
                    # Use regex to parse the string into groups we can use for coping
                    result              = re.match(regularExpPattern, destinationFile)
                    showName            = result.group(1)
                    season              = "Season " + result.group(2)
                    plexDestination     = plexTV    # Reset plex destination

                    # Update the path variable with the Show Name
                    plexDestination += showName + "/"

                    # Check if the show folder exists, if not create one
                    pathExists = os.path.exists(plexDestination)
                    if not pathExists:

                        # If path does not exist, create folder
                        os.mkdir(plexDestination)

                    # Update the path variable with the Show Name
                    plexDestination += season

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
                continue    # Continue to the next

if __name__ == '__main__':
    
    print(localMedia.get("movieSource"))
    loadSettings()
    print(localMedia.get("movieSource"))
    # download = downloadHandbrake()
    # if download:
    #     encodeMedia()
    # else:
    #     print("Failed to download Handbrake. Aborting!")
    