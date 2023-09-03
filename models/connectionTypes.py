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
import sys
import os

## Third-party library imports


## Variables

## Classes
# Media types
class MediaTypes:
    def __init__(self,
                 movie,
                 tv,
                 other):
        self.movie              = movie
        self.tv                 = tv
        self.other              = other

# Connection types
class ConnectionTypes:
    def __init__(self,
                 smb,
                 s3,
                 scp,
                 local):
        self.smb                = smb
        self.s3                 = s3
        self.scp                = scp
        self.local              = local

## Functions


## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")