# /usr/bin/python3

## Standard library imports
import sys
import os

## Third-party library imports

## Functions
"""
S3
call = subprocess.call(['s3cmd', 'get', sourceFileName, tempDirectory, '--skip-existing'])
subprocess.call(['s3cmd', 'put', destinationFileName, archiveDestination])
subprocess.call(['s3cmd', 'ls', archiveDestination + destinationFile])
subprocess.call(['s3cmd', 'del', sourceFileName])

SCP
# Connect to the Plex server
client.connect(plexHost, username='twasick',password='' ,key_filename='/home/twasick/.ssh/plex_ed25519')
sftp    = client.open_sftp() 
sftp.put(destinationFileName, plexDestination + destinationFile + encodedExt)
# Setup the SCP connection
sftp    = client.open_sftp() 
sftp.listdir(plexDestination)
sftp.mkdir(plexDestination)
sftp.put(destinationFileName, plexDestination + destinationFile + encodedExt)

SMB
os.system("osascript -e 'mount volume \"smb://10.0.0.202/plex\"'")
os.path
shutil.copy(destinationFileName, plexDestination)

Local
os.path
shutil.copy(destinationFileName, plexDestination)

"""

## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")