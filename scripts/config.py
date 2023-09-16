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
    "destinationConnectionType"     : "",
    "movieDestination"              : "",
    "movieSource"                   : "",
    "movieTemp"                     : "",
    "otherDestination"              : "",
    "otherSource"                   : "",
    "otherTemp"                     : "",
    "plexMovies"                    : "",
    "plexTv"                        : "",
    "sourceConnectionType"          : "",
    "tvDestination"                 : "",
    "tvSource"                      : "",
    "tvTemp"                        : ""
}
locationTypes                   = ["source", "destination", "temp"]
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
        inputMessage        = "Please choose how you want to upload files to your Plex server:\n"
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
        inputMessage        = "Please choose how you want to upload source MKV files:\n"
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
    print("Validating config file\n")

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
        # Function to set the locations for media files to be encoded, a temp location for encoding,
        # and the destination (Plex server?) location.
        # locationType is a string that is either "source", "destination", or "temp"
        # connectionType is a string that is either "local", "smb", "s3", or "scp
        def configUpdater_SetMediaLocations(locationType, connectionType):        
            # Local variables
            mediaAction             = ""
            counter                 = 0

            # Set message properties based on the input location
            if locationType == "source":
                mediaAction = "encoded,"
            elif locationType == "destination":
                mediaAction = "copied to the Plex server,"
            
            # Loop though the different media types based on the inputs (tv, movie, other)
            for mediaType in mediaTypes:
                
                # Set the messages based on the connection type
                if locationType == "temp":
                    message1        = f"Media to be encoded is set to a remote path. Please enter a local path for the temp location."
                    message2        = f"Please enter the path for {mediaType} media to be encoded. (Example: /plexTemp/{mediaType}): "
                    message3        = f"Local path is not properly formatted.\nPlease enter the path in a \"/plexTemp/{mediaType}\" format: "
                    regEx           = r'^/[^/]+(/[^/]+)*$'

                elif connectionType == "local":
                    message1        = f"Media to be {mediaAction} is set to a local path."
                    message2        = f"Please enter the path for {mediaType} media to be encoded. (Example: /folder/{mediaType}): "
                    message3        = f"Local path is not properly formatted.\nPlease enter the path in a \"/folder/{mediaType}\" format: "
                    regEx           = r'^/[^/]+(/[^/]+)*$'

                elif connectionType == "smb":
                    message1        = f"Media to be {mediaAction} is set to a SMB share, but no share details are found.\nPlease use your OS credential manager to store the SMB share credentials. This script will NOT prompt for credentials."
                    message2        = f"Please enter the {connectionType} path for {mediaType} media to be encoded. (Example: \\\\file-server\\share\\{mediaType}): "
                    message3        = f"SMB string is not properly formatted.\nPlease enter the path in a \"\\\\file-server\\share\\{mediaType}\" format: "
                    regEx           = r'^\\\\[^\\]+(\\[^\\]+)+$'

                elif connectionType == "s3":
                    message1        = f"Media to be {mediaAction} is set to a \"S3\" share, but no share details are found.\nCredentials are stored in s3cmd. If credentials are not set, there will be a prompt later to set them."
                    message2        = f"Please enter the {connectionType} path for {mediaType} media to be encoded. (Example: s3://bucket/share/{mediaType}): "
                    message3        = f"S3 string is not properly formatted.\nPlease enter the path in a \"s3://bucket/share/{mediaType}\" format: "
                    regEx           = r'^s3://[^/]+(/[^/]+)*$'
                    
                elif connectionType == "scp":
                    message1        = f"Media to be {mediaAction} is set to a \"SCP\" share, but no share details are found.\nCurrently only ssk key's are supported for authentication."
                    message2        = f"Please enter the {connectionType} path for {mediaType} media to be encoded. (Example: /folder/{mediaType}): "
                    message3        = f"SCP string is not properly formatted.\nPlease enter the path in a \"/folder/{mediaType}\" format: "
                    regEx           = r'^/[^/]+(/[^/]+)*$'
                
                else:
                    # Invalid connection type, abort!
                    print("Invalid connection type. Aborting!")
                    sys.exit()
                
                if config["media-settings"][f"{mediaType}{locationType}"] == "": 
                    # Print information regarding using SMB
                    # Using if statement to limit the amount of times the message is printed
                    if counter == 0:
                        # Print a blank line for formatting and ease of reading
                        print("")
                        print(message1)
                    
                    # Request the SMB path for media to be encoded
                    smbPath = input(message2)
                    
                    # Check that the path is valid
                    while not re.match(regEx, smbPath):
                        smbPath = input(message3)

                    # Update the config file 
                    config["media-settings"][f"{mediaType}{locationType}"] = smbPath
                    
                    # Write changes to the config file
                    configUpdater_WriteConfig(configFile)

                    # Increment the counter
                    counter += 1

                else:
                    # Increment the counter
                    counter += 1

                    # If the source location is not local, also prompt for the temp location
                    # if locationType == "source" and connectionType != "local":
                    #     # Set the temp locations for media to be encoded
                    #     print("Temp location is set to local")
                        


        # Set the source locations for media to be encoded
        configUpdater_SetMediaLocations("source", config["media-settings"]["sourceConnectionType"])

        # If the source location is not local, also prompt for the temp location
        if config["media-settings"]["sourceConnectionType"] != connectionType["1"]:
            # Set the temp locations for media to be encoded
            configUpdater_SetMediaLocations("temp", config["media-settings"]["sourceConnectionType"])

        # Set the destination locations for media after it has been encoded
        configUpdater_SetMediaLocations("destination", config["media-settings"]["destinationConnectionType"])

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