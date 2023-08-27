# /usr/bin/python3
## Script to automate the process of encoding and coping files to Plex Media Server

## Imports ##
import hashlib
import os
import re
import shutil
import subprocess
import sys
import requests
from configparser import ConfigParser
from colorama import Back, Fore, Style
from paramiko import SSHClient
from scp import SCPClient

## Variables ##
projectPath                     = BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
userProfile                     = os.environ["HOME"]
plexMedia                       = {"plexMount": "/Volumes/plex"}
plexHost                        = "twasick@vpn.tylerwasick.com"
s3Bucket                        = "s3://plexutil/"
s3ConfigFile                    = "~/.s3cfg"
s3Media                         = {
    "movieSource"                   : s3Bucket + "Movies/",
    "tvSource"                      : s3Bucket + "TV/",
    "otherSource"                   : s3Bucket + "Other/",
    "moviePlexDestination"          : plexMedia["plexMount"] + "/Movies/",  ## TODO: Update to use scp
    "tvPlexDestination"             : plexMedia["plexMount"] + "/TV/",      ## TODO: Update to use scp
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
handbrakeSHA256                 = "b96fe8b363be2398f62efc1061f08992f93f748540f30262557889008b806009"
handBrakeProfile                = " --preset-import-gui Plex-HD.json --crop-mode none"
regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"
configFile                      = projectPath + "/config.ini"
config                          = ConfigParser()

## TODO:Guard if already running, exit
## TODO: Extract subtitles
## TODO: Place Movies in folders
## TODO: Work on logging
## TODO: Add multi-thread support

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

                # Prompt user for access key and store it to a variable
                accessKey = input("Enter your S3 access key: ")

                # Prompt user for secret key and store it to a variable
                secret = input("Enter your S3 secret key: ")

                # Prompt  user for the S3 bucket name and store it to a variable
                s3BucketBase = input("S3 Endpoint []: ")

                # Prompt user for the URL template to access the bucket and store it to a variable
                s3BucketURL = input("DNS-style bucket+hostname:port template for accessing a bucket []: ")

                # Define the values to be changed in the config file
                print("Access key: " + accessKey)
                print("Secret: " + secret)
                
                # Create the S3 config file
                print("Creating S3 config file")
                shutil.copyfile(handBrakeCLIDir + "s3cmd.cfg", s3ConfigFileExp)

                # Read the config file
                config.read(s3ConfigFileExp)

                # Update the config with unique values
                config['default']['access_key']     = accessKey
                config['default']['secret_key']     = secret
                config['default']['host_base']      = s3BucketBase
                config['default']['host_bucket']    = s3BucketURL

                # Write the config file
                with open(s3ConfigFileExp, 'w') as configfile:
                    config.write(configfile)

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
    
# Download HandBrakeCLIDir is n ot already downloaded
def downloadHandbrake() -> bool:
    ## TODO: Verify hash of the download
    ## TODO: Check the version of Linux running, current support is for Ubuntu only

    # Check if "HandBrakeCLI" is already installed, is so exit and return True
    process = subprocess.call('flatpak list | grep "HandBrakeCLI"', shell=True)
    if process == 0:
        return True  # Exit successfully
    
    # Install Handbrake using Flatpak TODO: Fix this to use the flatpak repo
    subprocess.call(['flatpak', '--user', 'install', 'fr.handbrake.HandBrakeCLI', '-y'])
    
    # Verify the install was successful
    process = subprocess.call('flatpak list | grep "HandBrakeCLI"', shell=True)
    if process == 0:
        return True  # Exit successfully
    else:
        return False # Exit with errors
    
# Compares two files hashes and returns True if they match
def compareHashes(file1, file2) -> bool:
    # Open the files and read the contents
    with open(file1, 'rb') as f1:
        file1Contents = f1.read()

    with open(file2, 'rb') as f2:
        file2Contents = f2.read()

    # Compare the hashes
    if hashlib.sha256(file1Contents).hexdigest() == hashlib.sha256(file2Contents).hexdigest():
        # If the hashes match, exit
        return True
    else:
        # If the hashes do not match, exit
        return False

# Encode media
def encodeMedia():
    # Loop through all media types (3 folders)
    for counter in range(3):
        # Set source and destination dir for relevant content
        if counter == 0:  # Movies
            sourceDirectory         = s3Media["movieSource"]
            destinationDirectory    = s3Media["movieEncodeDestination"]
            plexDestination         = s3Media["moviePlexDestination"]
            tempDirectory           = s3Media["movieTmpDestination"]
            archiveDestination      = s3Media["archiveDestination"] + "Movies/"
            movieList               = movies

        elif counter == 1:  # TV Shows
            sourceDirectory         = s3Media["tvSource"]
            destinationDirectory    = s3Media["tvEncodeDestination"]
            plexDestination         = s3Media["tvPlexDestination"]
            tempDirectory           = s3Media["tvTmpDestination"]
            archiveDestination      = s3Media["archiveDestination"] + "TV/"
            movieList               = shows

        else:  # Other Movies
            sourceDirectory         = s3Media["otherSource"]
            destinationDirectory    = s3Media["otherEncodeDestination"]
            plexDestination         = s3Media["otherPlexDestination"]
            tempDirectory           = s3Media["otherTmpDestination"]
            archiveDestination      = s3Media["archiveDestination"] + "Other/"
            movieList               = others

        ## Process Shows ##
        ## Iterate over the source directory using s3cmd
        results = subprocess.run(['s3cmd', 'ls', sourceDirectory], stdout=subprocess.PIPE)

        # Loop through the files and folders returned by the s3cmd call
        for line in results.stdout.decode('utf-8').split('\n'):
            
            # Check if the line is empty
            if not line:
                # If the line is empty, skip it
                continue
            else:
                # Else, process the line using regex
                parsedResult = re.search('s3:\/\/.*', line)
                
                # Check if the string ends with an extension from the encodingExt list
                if parsedResult.group(0).endswith(encodingExt):

                    # Add the paths to the list
                    movieList.append(parsedResult.group(0))

                    # Print result found
                    print("Added: " + parsedResult.group(0) + "to the list")

        # Loop through the list of movies, encode the movie then copy to the
        # appropriate destination
        for movie in movieList:
            
            # Seperate the file name from the path
            movieFileName = movie.split("/")[-1]

            # Remove the file extension before encoding then add the new file
            # extension for the destination
            destinationFile = movieFileName.rstrip(encodingRString)

            # Concatinate the destination file name with the destination path
            destinationFileName = destinationDirectory + destinationFile + encodedExt

            # Set the source file destination by concatinating the source path to the file name
            sourceFileName = sourceDirectory + movieFileName

            print("Source file: " + sourceFileName)
            print("Destination file: " + destinationFileName)

            # Copy the files locally before encoding
            subprocess.call(['s3cmd', 'get', sourceFileName, tempDirectory, '--skip-existing'])

            # Create the process call
            handBrakeCall = (
                "flatpak run fr.handbrake.HandBrakeCLI"
                + handBrakeProfile
                + " -i "
                + f'"{tempDirectory + movieFileName}"'
                + " -o "
                + f'"{destinationFileName}"'
            )

            # Run the file into HandBrake
            returned_value = subprocess.call(handBrakeCall, shell=True)
            fileExists = os.path.isfile(destinationFileName)

            # Check if the destination file exists, and is not 0k, if so proceed
            if returned_value == 0 and fileExists:
                ## Connect to the Plex share using SCP
                # Create a connection
                sshConnection = SSHClient()

                # Load the host keys
                sshConnection.load_system_host_keys()

                # Connect to the host
                sshConnection.connect(plexHost)

                # Verify the connection was successful
                if sshConnection.get_transport().is_active() is False:
                    print("Failed to connect to Plex host, aborting!")
                    break

                # Create a SCP client
                scp = SCPClient(sshConnection.get_transport())

                # Copy the file to the Plex server
                if counter == 0:
                    result = scp.put(destinationFileName, plexDestination)

                    # Verify the file was copied successfully
                    if result.succeeded:
                        print("File copied successfully")
                    else:
                        print("File copy failed, aborting!")
                        break
                 
                # Elif TV Shows, we need to parse where they will be copies to       
                elif counter == 1:
                    # Use regex to parse the string into groups we can use for coping
                    result          = re.match(regularExpPattern, destinationFile)
                    showName        = result.group(1)
                    season          = "Season " + result.group(2)
                    plexDestination = s3Media["tvPlexDestination"]  # Reset plex destination

                    # Update the path variable with the Show Name
                    plexDestination += showName

                    # Check if the S3 show folder location exists, if not create one
                    showFolder = subprocess.call(['s3cmd', 'ls', plexDestination])

                    # If path does not exist, create folder
                    if showFolder != 0:
                        # Create the folder
                        subprocess.call(['s3cmd', 'mkdir', plexDestination])
                    
                    # Update the path variable with the Show Name
                    plexDestination += "/" + season

                    # Checks if the season folder exists, if not creates one
                    seasonFolder = subprocess.call(['s3cmd', 'ls', plexDestination])

                    if seasonFolder != 0:
                        # Create the folder
                        subprocess.call(['s3cmd', 'mkdir', plexDestination])

                    # Copy the file the encoded directory to the Plex destination using SCP
                    scpCopy = scp.put(destinationFileName, plexDestination)

                    # Verify the file was copied successfully by comparing the filehash
                    if scpCopy.succeeded:
                        print("File copied successfully")
                    else:
                        print("File copy failed, aborting!")
                        break

                # Copy the encoded file to the archive directory
                subprocess.call(['s3cmd', 'put', destinationFileName, archiveDestination])

                # Verify the file was copied successfully in S3
                if subprocess.call(['s3cmd', 'ls', archiveDestination + destinationFile]) == 0:
                    print("File copied successfully")

                    # Remove files from local source and destination encoding directories
                    os.remove(destinationFileName)
                    os.remove(tempDirectory + movieFileName)
                    subprocess.call(['s3cmd', 'del', sourceFileName])
                else:
                    print("File copy failed, aborting!")
                    break

            # Else print error and continue to next file
            else:
                print("File was not encoded")
                break


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
        print("Encoding media")
        encodeMedia()
    else:
        # Else exit
        print("Failed to download Handbrake. Aborting!")
        sys.exit()
