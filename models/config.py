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
import re
import sys
import os

## Third-party library imports


## Custom library imports
import connectionInfo

## Variables
config                          = configparser.ConfigParser()
configHeaders                   = ["media-settings", "handbrake", "scp-source", "scp-destination"]
connectionType                  = {
    "1"                             :"local", 
    "2"                             :"smb", 
    "3"                             :"s3", 
    "4"                             :"scp"
}
connectionSCPTypes              = {
    "scp-source"                    : "sourceConnectionType",
    "scp-destination"               : "destinationConnectionType"
}
mediaSettings                   = {
    "movieSource"                   : "",
    "movieEncodedDestination"       : "",
    "movieTempLocation"             : "",
    "otherEncodedDestination"       : "",
    "otherSource"                   : "",
    "otherTempLocation"             : "",
    "plexMovies"                    : "",
    "plexTv"                        : "",
    "tvEncodedDestination"          : "",
    "tvSource"                      : "",
    "tvTempLocation"                : "",
    "destinationConnectionType"     : "",
    "sourceConnectionType"          : ""
}
scpSettings                     = { 
    "scpHost"                       : "",
    "scpUsername"                   : "",
    "scpPort"                       : "",
    "scpKeyFile"                    : ""
}
mediaTypes                      = ["movie", "tv", "other"]
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
                 destinationConnectionType: connectionInfo.ConnectionTypes,
                 sourceConnectionType: connectionInfo.ConnectionTypes,
                 sourceMount,
                 plexMount):
        self.movieSource                = movieSource
        self.tvSource                   = tvSource
        self.otherSource                = otherSource
        self.moviesDestination          = moviesDestination
        self.tvDestination              = tvDestination
        self.otherDestination           = otherDestination
        self.destinationConnectionType  = destinationConnectionType
        self.sourceConnectionType       = sourceConnectionType
        self.sourceMount                = sourceMount
        self.plexMount                  = plexMount
          
class handbrake:
    def __init__(self,
                 handBrakeProfile):
          self.handBrakeProfile         = handBrakeProfile

## Functions
# Update the connection types and wrote the changes to the config file
def configUpdater_ConnectionType(configFile):
    # If missing, Prompt the user for Plex connection information
    if config["media-settings"]["destinationConnectionType"] == "":
        inputMessage        = "Please select the method of which the script will be using to upload files your Plex server:\n"
        userInput           = "" 

        for index, item in enumerate(connectionType.values()):
            inputMessage += f'{index+1}) {item}\n'        

        while ((userInput not in connectionType.keys()) and (userInput not in connectionType.values())):

            print(inputMessage)
            userInput = input("Selection: ")

        if userInput.isdigit():
            # Update the config file with the user's selection
            config["media-settings"]["destinationConnectionType"] = connectionType[userInput]
            configUpdater_WriteConfig(configFile)

            print('Plex connection set to: ' + connectionType[userInput]) #dev
        
        else:
            # Update the config file with the user's selection
            config["media-settings"]["destinationConnectionType"] = userInput
            configUpdater_WriteConfig(configFile)

            print('Plex connection set to: ' + userInput) #dev

    # If missing, prompt the user for the source type for media that is to be encoded
    if config["media-settings"]["sourceConnectionType"] == "":
        # Prompt the user for the source type
        inputMessage        = "Where are the source MKV (files to be encoded) located?:\n"
        userInput           = "" 

        for index, item in enumerate(connectionType.values()):
            inputMessage += f'{index+1}) {item}\n'        

        while ((userInput not in connectionType.keys()) and (userInput not in connectionType.values())):

            print(inputMessage)
            userInput = input("Selection: ")

        if userInput.isdigit():
            # Update the config file with the user's selection
            config["media-settings"]["sourceConnectionType"] = connectionType[userInput]
            configUpdater_WriteConfig(configFile)

            print('Source connection set to: ' + connectionType[userInput])
        else:
            # Update the config file with the user's selection
            config["media-settings"]["sourceConnectionType"] = userInput
            configUpdater_WriteConfig(configFile)

            print('Plex connection set to: ' + userInput) #dev

# Write changes from memory to the config file
def configUpdater_WriteConfig(configFile):
    with open(configFile, "w") as file:
        config.write(file)

def loadConfig(configFile) -> bool:
    
    # Local variables
    validConfig                 = True

    # Local functions

    # Print status output
    print("Reviewing config file...")
    # Check if the config file exists
    if os.path.isfile(configFile):
        print("Config file exists: " + configFile)
        
    else:
        # If file does not exist, create the config file
        print("Config file does not exist. Creating config file.")
        config["media-settings"]    = mediaSettings
        config["handbrake"]         = handbrakeSettings

        # Save file to the project directory
        configUpdater_WriteConfig(configFile)

        # Verify the file was created
        if os.path.isfile(configFile):
            print("Config file created successfully")
        else:
            print("Failed to create config file. Aborting!")
            sys.exit()


    # Read the config file
    config.read(configFile)

    # Print status output
    print("Validating config file")

    # Verify the config file is not empty
    # Verify media-settings settings in config file exists
    try:
        config["media-settings"]
    except KeyError:
        config["media-settings"]    = mediaSettings
        configUpdater_WriteConfig(configFile)

    # Verify handbrake settings in config file exists
    try:
        config["handbrake"]
    except KeyError:
        config["handbrake"]         = handbrakeSettings
        configUpdater_WriteConfig(configFile)

    # Verify SCP settings in the config file exist
    try:
        config["scp-source"]
    except KeyError:
        config["scp-source"]        = scpSettings
        configUpdater_WriteConfig(configFile)
    try:
        config["scp-destination"]
    except KeyError:
        config["scp-destination"]   = scpSettings
        configUpdater_WriteConfig(configFile)

    # Verify media-settings in config file
    for key in config["media-settings"]:
        # If the value is empty, set the config validation variable to False 
        if not config["media-settings"][key]:
            validConfig = False

    # If there are values missing in the config file, initiate the setup process
    if not validConfig:
        
        # Verify if the connection types are set, if not prompt the user to set them
        configUpdater_ConnectionType(configFile)

        # If the source is "local", set temp locations to "local"
        if config["media-settings"]["sourceConnectionType"] == connectionType["1"]:
            config["media-settings"]["movieTempDestination"]    = "local"
            config["media-settings"]["tvTempLocation"]          = "local"
            config["media-settings"]["otherTempLocation"]       = "local"

            # Write the changes to the config file
            configUpdater_WriteConfig(configFile)

        #TODO: Refactor the following code to be more efficient
        # Elif source is "SMB", prompt the user for the SMB connection information
        elif config["media-settings"]["sourceConnectionType"] == connectionType["2"]:
            # Loop though the different media types
            for mediaType in mediaTypes:
                if config["media-settings"][f"{mediaType}source"] == "": 
                    # Print information regarding using SMB
                    if mediaType.index == 0:
                        print("Media to be encoded is set to a SMB share, but no share details are found.\n" + 
                        "Please use your OS credential manager to store the SMB share credentials. This script will NOT prompt for credentials.")
                    
                    # Request the SMB path for media to be encoded
                    smbPath = input(f"Please enter the SMB path for {mediaType} media that is to be encoded. (Example: \\\\file-server\\share\\{mediaType}): ")
                    
                    # Check that the path is valid
                    while not re.match(r'^\\\\[^\\]+(\\[^\\]+)+$', smbPath):
                        smbPath = input("SMB string is not properly formatted.\n" + 
                                        "Please enter the path in a \"\\\\server\\share\" format: ")

                    # Update the config file 
                    config["media-settings"][f"{mediaType}Source"] = smbPath
                    
                    # Write changes to the config file
                    configUpdater_WriteConfig(configFile)

        # If source is "S3", prompt the user for the S3 connection information
        elif config["media-settings"]["sourceConnectionType"] == connectionType["3"]:
            # Loop though the different media types
            for mediaType in mediaTypes:
                if config["media-settings"][f"{mediaType}source"] == "": 
                    # Print information regarding using SMB
                    if mediaType.index == 0:
                        print("Media to be encoded is set to a \"S3\" share, but no share details are found.\n" + 
                        "Credentials are stored in s3cmd. If credentials are not set, there will be a prompt later to set them.")
                    
                    # Request the SMB path for media to be encoded
                    smbPath = input(f"Please enter the S3 path for {mediaType} media that is to be encoded. (Example: s3://bucket/{mediaType}): ")
                    
                    # Check that the path is valid
                    while not re.match(r'^s3://[^/]+(/[^/]+)*$', smbPath):
                        smbPath = input(f"S3 string is not properly formatted.\n" + 
                                        "Please enter the path in a \"s3://bucket/{mediaType}\" format: ")

                    # Update the config file 
                    config["media-settings"][f"{mediaType}Source"] = smbPath
                    
                    # Write changes to the config file
                    configUpdater_WriteConfig(configFile)
                    
        # Else if source is "SCP", prompt the user for the SCP connection information
        elif config["media-settings"]["sourceConnectionType"] == connectionType["4"]:

            # Loop through the scp connections
            for connectionSCPType in connectionSCPTypes.items():
                
                # Check if the SCP connection is set, if not prompt the user to set it
                if config[connectionSCPType[0]]["scpHost"] == "" and config["media-settings"][connectionSCPType[1]] != "" and config["media-settings"][connectionSCPType[1]] == "scp":
                    if connectionSCPType[0] == "scp-source":
                        location        = "source"
                    else:
                        location        = "destination"
                    
                    # Prompt the user for the SCP connection information
                    print(f"Please enter the SCP connection information for your {location} location")
                    host        = input(f"Please supply the hostname or IP for the {location} location: ")
                    username    = input(f"Please supply the username for the {location} location: ")
                    port        = input(f"Please supply the port for the {location} location (default: 22): ")
                    scpKeyFile  = input(f"Please supply the path to the key file for the {location} location (direct file path): ")

                    # Validate the port number
                    if port == "":
                        port = "22"

                    # Update the config file
                    config[connectionSCPType[0]]["scpHost"]        = host
                    config[connectionSCPType[0]]["scpUsername"]    = username
                    config[connectionSCPType[0]]["scpPort"]        = port
                    config[connectionSCPType[0]]["scpKeyFile"]     = scpKeyFile

                    # Write changes to the config file
                    configUpdater_WriteConfig(configFile)
                    
                # Loop though the different media types
                for mediaType in mediaTypes:
                    if config["media-settings"][f"{mediaType}source"] == "": 
                        # Print information regarding using SMB
                        if mediaType.index == 0:
                            print("Media to be encoded is set to a \"SCP\" share, but no share details are found.\n" + 
                            "Currently only ssk key's are supported for authentication.")
                        
                        # Request the SMB path for media to be encoded
                        smbPath = input(f"Please enter the SCP path for {mediaType} media that is to be encoded. (Example: /share/{mediaType}): ")
                        
                        # Check that the path is valid
                        while not re.match(r'^/[^/]+(/[^/]+)*$', smbPath):
                            smbPath = input(f"SCP string is not properly formatted.\n" + 
                                            "Please enter the path in a \"/folder/{mediaType}\" format: ")

                        # Update the config file 
                        config["media-settings"][f"{mediaType}Source"] = smbPath
                        
                        # Write changes to the config file
                        configUpdater_WriteConfig(configFile)


                # Loop though the different media types
                for mediaType in mediaTypes:
                    if config["media-settings"][f"{mediaType}source"] == "": 
                        # Print information regarding using SMB
                        if mediaType.index == 0:
                            print("Media to be encoded is set to a \"SCP\" path, but no share details are found.\n" + 
                            "Credentials are stored using a ssh key only at this time. If there are no keys created, please exit and start the script again once generated.")
                        
                        # Request the SMB path for media to be encoded
                        smbPath = input(f"Please enter the SCP path for {mediaType} media that is to be encoded. (Example: /media/{mediaType}): ")
                        
                        # Check that the path is valid
                        while not re.match(r'^\/[^/]+(\/[^/]+)+$', smbPath):
                            smbPath = input(f"S3 string is not properly formatted.\n" + 
                                            "Please enter the path, in a \"/media/{mediaType}\" format: ")

                        # Update the config file 
                        config["media-settings"][f"{mediaType}Source"] = smbPath
                        
                        # Write changes to the config file
                        configUpdater_WriteConfig(configFile)

        # Validate Plex connection information

        # Find the root path for Plex Movies

        # Find the root path for Plex TV
        
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
    # connectionSCPTypes              = {
    #     "scp-source"                    : "sourceConnectionType",
    #     "scp-destination"               : "remoteConnectionType"
    # }
    # for i in connectionSCPTypes.items():
    #     print(f"{i.index}")