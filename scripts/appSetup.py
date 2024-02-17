# /usr/bin/python3

## Standard library imports
import subprocess

## Third-party library imports
from configparser import ConfigParser

## Variables
config                          = ConfigParser()

## Functions
def appRequirements() -> bool:
    ## Check if required applications are installed
    print("Checking for required applications...")

    # Download HandBrakeCLIDir is n ot already downloaded
    def handbrakeInstalled() -> bool:
        # Check if "HandBrakeCLI" is already installed, is so exit and return True
        try:
            subprocess.check_output(['dpkg', '-s', 'handbrake-cli'])
            return True  # Exit successfully
        except subprocess.CalledProcessError:
            return False # Exit with errors

## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")