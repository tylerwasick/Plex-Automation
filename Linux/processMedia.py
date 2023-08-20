# /usr/bin/python3
## Script to automate the process of encoding and coping files to Plex Media Server

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
s3Bucket                        = "s3://wasick"
s3ConfigFile                    = "~/.s3cfg"
baseMediaPath                   = s3Bucket + "/PlexMedia/"
s3Media                         = {
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
handBrakeCLIPath                = handBrakeCLIDir + "HandBrakeCLI-1.6.1-x86_64.flatpak"
handBrakeURL                    = "https://github.com/HandBrake/HandBrake/releases/download/1.6.1/HandBrakeCLI-1.6.1-x86_64.flatpak"
handbrakeSHA256                 = "b96fe8b363be2398f62efc1061f08992f93f748540f30262557889008b806009"
handBrakeProfile                = " --preset-import-gui Plex-HD.json --crop-mode none"
regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                      = projectPath + "/config.ini"
config                          = ConfigParser()

## TODO:Guard if already running, exit
## TODO: Extract subtitles
## TODO: Place Movies in folders

## Functions ##
##TODO: Read a config file for locations
def appSetup() -> bool:
    ## Check if required applications are installed
    # Flatpak 
    def flatPakSetup() -> bool:
        # Check to see if S3 is installed
        call = subprocess.call(['which', 'flatpak'])
        if call != 0:
            # If not, install using apt
            print("Flatpak is not installed, installing.")
            subprocess.call(['sudo', 'apt-get', 'install', 'flatpak', '--assume-yes', '-q', '-y'])

            # Verify the install was successful
            call = subprocess.call(['which', 'flatpak'])
            if call == 0:
                # If so, exit
                print("Flatpak is now installed")
                return True
            else:
                # Unable to install, exit
                print("Failed to install Flatpak, Aborting!")
                return False
        else:
            # If so, exit
            print("Flatpak is already installed")
            return True

    # S3 bucket
    def s3Setup() -> bool:
        # Check to see if S3 is installed
        def s3Install() -> bool:
            call = subprocess.call(['which', 's3cmd'])
            if call != 0:
                # If not, install using apt
                print("S3cmd is not installed, installing.")
                subprocess.call(['sudo', 'apt-get', 'install', 's3cmd', '--assume-yes', '-q', '-y'])

                # Verify the install was successful
                call = subprocess.call(['which', 's3cmd'])
                if call == 0:
                    # If so, exit
                    print("S3cmd is now installed")
                    return True
                else:
                    # Unable to install, exit
                    print("Failed to install S3cmd, Aborting!")
                    return False
            else:
                # If so, exit
                print("S3cmd is already installed")
                return True
                
        ## Connect to S3 bucket
        def s3Config() -> bool:
            # See if the S3 configs exist
            call = subprocess.call(['s3cmd', 'ls', s3Bucket])
            if call == 0:
                # If so, exit
                print("S3cmd is already configured")
                return True
            
            # If not, create the config file
            else:
                print("S3cmd is not configured, configuring now.")

                # Expand the s3ConfigFile path
                s3ConfigFileExp = os.path.expanduser(s3ConfigFile)

                # Connect to the S3 bucket
                subprocess.call(['s3cmd', 
                                 '--access_key=DO00F336LZ46BCAXJCLY', 
                                 '--secret_key=2WEOlemCFhz2QFdfSN27aQJDGpWI9miaipaqsVY6RRM',  
                                 '--host=nyc3.digitaloceanspaces.com', 
                                 '--host-bucket="%(bucket)%s.nyc3.digitaloceanspaces.com"',
                                 '--dump-config',
                                 '2>&1',
                                 '|',
                                 'tee',
                                 "\"\"" + s3ConfigFileExp + "\"\""])


                # Verify the config file was created
                if os.path.exists(s3ConfigFileExp):
                    # If so, exit
                    print("S3cmd is now configured")
                    return True
                else:
                    # Unable to create config file, exit
                    print("Failed to configure S3cmd, Aborting!")
                    return False
                
        # Run the functions, if they return True, continue, else exit
        if s3Install() and s3Config():
            return True     # Exit successfully
        else:
            print("Failed to configure s3cmd, Aborting!")
            return False    # Exit with errors
            
    print("Checking for required applications...")

    print("Checking if flatpak is installed")
    setupFlatPak = flatPakSetup()

    print("Checking if s3cmd is installed")
    setupS3cmd = s3Setup()

    if setupFlatPak and setupS3cmd:
        return True     # Exit successfully
    else:
        # Unable to install, exit
        print("Failed to install required applications, Aborting!")
        return False    # Exit with errors
    

## Download HandBrakeCLIDir is n ot already downloaded
def downloadHandbrake() -> bool:
    ## TODO: Verify hash of the download
    ## TODO: Check the version of Linux running, current support is for Ubuntu only

    # Check if "HandBrakeCLI" is already installed, is so exit and return True
    process = subprocess.call('flatpak list | grep "HandBrakeCLI"', shell=True)
    if process == 0:
        return True  # Exit successfully

    # Verify the "Download" path exists, if not, create the folder before proceeding
    elif os.path.exists(handBrakeCLIDir) is False:
        # Check if the download folder is missing, create the downloads folder
        os.makedirs(handBrakeCLIDir)

        # Verify folder was created 
        if os.path.exists(handBrakeCLIDir) is False:
            # Failed to create directory, abort!
            return False  # Exit with errors
 
    # Download HandBrakeCLIDir
    download = requests.get(handBrakeURL)
    open(handBrakeCLIPath, "wb").write(download.content)
    
    # Install Handbrake using Flatpak
    subprocess.call(['flatpak', '--user', 'install', handBrakeCLIPath, '-y'])
    
    # Verify the download exists
    if os.path.exists(handBrakeCLIPath):
        
        return True  # Exit successfully
    else:
        return False  # Exit with errors

   


## Encode media
def encodeMedia():
    # Loop through all media types (3 folders)
    for counter in range(3):
        # Set source and destination dir for relevant content
        if counter == 0:  # Movies
            sourceDirectory = s3Media["movieSource"]
            destinationDirectory = s3Media["movieEncodeDestination"]
            plexDestination = s3Media["moviePlexDestination"]
            movieList = movies

        elif counter == 1:  # TV Shows
            sourceDirectory = s3Media["tvSource"]
            destinationDirectory = s3Media["tvEncodeDestination"]
            plexDestination = s3Media["tvPlexDestination"]
            movieList = shows

        else:  # Other Movies
            sourceDirectory = s3Media["otherSource"]
            destinationDirectory = s3Media["otherEncodeDestination"]
            plexDestination = s3Media["otherPlexDestination"]
            movieList = others

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
            handBrakeCall = (
                handBrakeCLIPath
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

                elif (
                    counter == 1
                ):  # Elif TV Shows, we need to parse where they will be copies to
                    # Use regex to parse the string into groups we can use for coping
                    result = re.match(regularExpPattern, destinationFile)
                    showName = result.group(1)
                    season = "Season " + result.group(2)
                    plexDestination = s3Media["tvPlexDestination"]  # Reset plex destination

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

    # Run the app reqirement setup
    setup       = appSetup()
    if setup:
        print("App requirement setup complete")
    else:
        print("App requirement setup failed")
        sys.exit()

    # Download Handbrake
    download    = downloadHandbrake()
    if download:
        # If successful, encode media
        #encodeMedia()
        print("Encoding media")
    else:
        # Else exit
        print("Failed to download Handbrake. Aborting!")
        sys.exit()
