# /usr/bin/python3

"""
Script Name         : appSetup.py
Description         : Python script to handle the requirements for the main automation
                        script (plexAutomation.py). In addition, this script also handles
                        the configuration setup for the automation script.
Author              : Tyler Wasick (github.com/tylerwasick)
Date                : 09/01/2023
=======================================================================================
Version History     :
09/01/2023          : Initial Release
"""

## Standard library imports
import os
import shutil
import subprocess
import sys

## Third-party library imports
from configparser import ConfigParser
import requests

## Variables
config                          = ConfigParser()

## Functions
def appRequirements(s3Bucket, s3ConfigFile, handBrakeCLIDir) -> bool:
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
                with open(s3ConfigFileExp, 'w') as configFile:
                    config.write(configFile)

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
def downloadHandbrake(handBrakeCLIDir, handBrakeFlatPakPath, handBrakeFlatPakGit) -> bool:
    # Check if "HandBrakeCLI" is already installed, is so exit and return True
    process = subprocess.call('flatpak list | grep "HandBrakeCLI"', shell=True)
    if process == 0:
        return True  # Exit successfully
    
    # Check if the HandBrakeCLI directory exists, if not create it
    if not os.path.exists(handBrakeCLIDir):
        os.makedirs(handBrakeCLIDir)

    # Check if the HandBrakeCLI file exists, if not download it
    if not os.path.isfile(handBrakeFlatPakPath):
        print("Downloading HandBrakeCLI")
        r = requests.get(handBrakeFlatPakGit, allow_redirects=True)
        open(handBrakeFlatPakPath, 'wb').write(r.content)

    # Install Handbrake using Flatpak
    subprocess.call(['flatpak', '--user', 'install', handBrakeFlatPakPath, '-y'])
    
    # Verify the install was successful
    process = subprocess.call('flatpak list | grep "HandBrakeCLI"', shell=True)
    if process == 0:
        return True  # Exit successfully
    else:
        return False # Exit with errors

## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")