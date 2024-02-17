# /usr/bin/python3

## Standard library imports
import re
import subprocess
import sys
import os

## Third-party library imports
import paramiko

## Variables
movies                          = []
shows                           = []
others                          = []
encodingExt                     = (".mkv", ".mp4", ".m4v")
encodingRString                 = ".mp4.mkv.m4v"
encodedExt                      = ".m4v"
regularExpPattern               = r"^([\w\s]+)\s-\sS(\d+)E"


## Functions
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
                    print("Added: " + parsedResult.group(0) + " to the list")

        # Loop through the list of movies, encode the movie then copy to the
        # appropriate destination
        for movie in movieList:
            
            # Separate the file name from the path
            movieFileName = movie.split("/")[-1]

            # Remove the file extension before encoding then add the new file
            # extension for the destination
            destinationFile = movieFileName.rstrip(encodingRString)

            # Concatenate the destination file name with the destination path
            destinationFileName = destinationDirectory + destinationFile + encodedExt

            # Set the source file destination by concatenating the source path to the file name
            sourceFileName = sourceDirectory + movieFileName

            print("Source file: " + tempDirectory + movieFileName)
            print("Destination file: " + destinationFileName)

            # Copy the files locally before encoding
            call = subprocess.call(['s3cmd', 'get', sourceFileName, tempDirectory, '--skip-existing'])

            # Create the process call
            if call == 0:
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

            # Verify the file was encoded successfully
            else:
                # If not, exit
                print("Failed to copy file, aborting!")
                break

            # Check if the destination file exists, and is not 0k, if so proceed
            if returned_value == 0 and fileExists:
                ## Connect to the Plex share using SCP
                # Create a connection
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
                # Connect to the Plex server
                client.connect(plexHost, username='twasick',password='' ,key_filename='/home/twasick/.ssh/plex_ed25519')

                # Copy the file to the Plex server
                if counter == 0:
                    # Setup sftp connection and transmit this script 
                    sftp    = client.open_sftp() 
                    sftp.put(destinationFileName, plexDestination + destinationFile + encodedExt)
                 
                # Elif TV Shows, we need to parse where they will be copies to       
                elif counter == 1:
                    # Use regex to parse the string into groups we can use for coping
                    result          = re.match(regularExpPattern, destinationFile)
                    showName        = result.group(1)
                    season          = "Season " + result.group(2)
                    plexDestination = s3Media["tvPlexDestination"]  # Reset plex destination

                    # Update the path variable with the Show Name
                    plexDestination += showName

                    # Setup the SCP connection
                    sftp    = client.open_sftp() 

                    # Check if the SCP path exists, if not create it
                    try:
                        sftp.listdir(plexDestination)
                    except IOError:
                        sftp.mkdir(plexDestination)
                    
                    # Update the path variable with the Show Name
                    plexDestination += "/" + season + "/"

                    # Checks if the season folder exists, if not creates one
                    try:
                        sftp.listdir(plexDestination)
                    except IOError:
                        sftp.mkdir(plexDestination)
                    
                    # Copy the file the encoded directory to the Plex destination using SCP
                    # Use SCP to copy data to the Plex server
                    sftp.put(destinationFileName, plexDestination + destinationFile + encodedExt)

                # Close the sftp connection
                sftp.close()

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

## Main entry point
if __name__ == "__main__":
    print("Placeholder Text")