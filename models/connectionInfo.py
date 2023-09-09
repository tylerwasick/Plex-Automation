# /usr/bin/python3

"""
Script Name         : connectionTypes.py
Description         : Manages the different connection types (SMB, S3, SCP, and Local)
Author              : Tyler Wasick (github.com/tylerwasick)
Date                : 09/01/2023
=======================================================================================
Version History     :
09/03/2023          : Initial Release
"""

## Standard library imports
from enum import Enum
import sys
import os

## Third-party library imports


## Variables

## Classes
# Media types
class MediaTypes(Enum):
    movie              = 1
    tv                 = 2
    other              = 3

# Connection types
class ConnectionTypes(Enum):
    smb                = 1
    s3                 = 2
    scp                = 3
    local              = 4

## Functions


## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")