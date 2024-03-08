import hashlib
import os
import shutil
import sys
from threading import Thread

# Function to count files in a directory and its subdirectories
def count_files(path):
    """Calculates the total number of files in a directory and its subdirectories."""
    total_files = sum(len(files) for _, _, files in os.walk(path))
    return total_files

# Function to copy a file from source to replica, optionally logging the operation
def copy_file(source_file, replica_file, log_file=None):
    """Copies a file from the source to the replica, creating the replica directory if needed.
    Optionally logs the copied file information."""
    replica_dir = os.path.dirname(replica_file)
    if not os.path.exists(replica_dir):
        os.makedirs(replica_dir)

    if not os.path.exists(replica_file) or os.path.getsize(source_file) != os.path.getsize(replica_file):
        try:
            # Check if file already exists using MD5 hash
            if not file_exists(source_file, replica_file):
                shutil.copy2(source_file, replica_file)
                if log_file:  # Check if it has a 'write' method
                    with open(log_file, "a") as log:
                        # Write to the file
                        log.write(f"Copied: {source_file} -> {replica_file}\n")        
        except Exception as e:
            print(f"Error copying file: {source_file} - {e}")

# Function to get a valid folder path from user input
def get_folder_path(prompt):
    while True:
        path = input(prompt)
        if not path or not os.path.isdir(path):
            print("Invalid path. Please try again.")
            continue
        return path

# Function to synchronize files from source to replica folder with progress updates
def sync_and_update_progress(source_folder, replica_folder, log_file=None):
    """Synchronizes files from the source folder to the replica folder, providing progress updates.
    Optionally logs copied file information."""
    total_files = count_files(source_folder)

    for root, _, files in os.walk(source_folder):
        for file in files:
            source_file = os.path.join(root, file).replace("\\", "/")
            replica_file = os.path.join(replica_folder, os.path.relpath(source_file, source_folder)).replace("\\", "/")
            copy_file(source_file, replica_file, log_file)

            # Print progress (replace with your preferred progress reporting mechanism)
            print(f"Progress: {source_file} -> {replica_file}")

    print("Synchronization completed.")

# Function to delete the replica folder
def delete_replica(replica_folder):
    """Deletes the replica folder if it exists."""
    if os.path.exists(replica_folder):
        shutil.rmtree(replica_folder)
        print(f"Replica folder deleted: {replica_folder}")
    else:
        print(f"Replica folder not found: {replica_folder}")

# Function to open the replica folder in the system's default file explorer
def open_replica(replica_folder):
    """Opens the replica folder in the system's default file explorer."""
    if os.path.exists(replica_folder):
        os.startfile(replica_folder)
    else:
        print(f"Replica folder not found: {replica_folder}")

# Function to check if the file exists in the replica folder by comparing MD5 hashes
def file_exists(source_file, replica_file):
    """Check if the file exists in the replica folder by comparing MD5 hashes."""
    if not os.path.exists(replica_file):
        return False

    with open(source_file, "rb") as sf, open(replica_file, "rb") as rf:
        source_md5 = hashlib.md5(sf.read()).hexdigest()
        replica_md5 = hashlib.md5(rf.read()).hexdigest()
        return source_md5 == replica_md5

if __name__ == "__main__":
    # If command-line arguments are provided, use them as source and replica folder paths
    if len(sys.argv) > 2:
        source_folder, replica_folder = sys.argv[1:3]
    else:
        # Otherwise, prompt user to enter folder paths
        source_folder = get_folder_path("Enter the path to the source folder: ")
        replica_folder = get_folder_path("Enter the path to the replica folder: ")

    # Optional log file argument
    log_file = None
    if len(sys.argv) > 3:
        log_file = sys.argv[3]

    # Synchronize files
    sync_and_update_progress(source_folder, replica_folder, log_file)

    # Optional actions based on command-line arguments
    if len(sys.argv) > 4 and sys.argv[4] == "-delete":
        delete_replica(replica_folder)
    elif len(sys.argv) > 4 and sys.argv[4] == "-open":
        open_replica(replica_folder)
