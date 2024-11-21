import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

# Constants
GITHUB_BASE = os.getenv('GITHUB_BASE')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Not directly used in this script but loaded for private repos if needed.
TIMESTAMP = datetime.now().strftime("%d-%b-%y").lower()
OUTPUT_CSV = f"repo-index_{TIMESTAMP}.csv"

def get_remote_url(repo_path):
    """
    Get the remote URL of a Git repository using the 'git config' command.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()
        # Remove '.git' from the end of the URL if present
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]
        return remote_url
    except subprocess.CalledProcessError:
        return None

def main():
    """
    Main function to index all GitHub repositories under GITHUB_BASE and write them to a CSV.
    """
    if not GITHUB_BASE:
        print("Error: GITHUB_BASE is not set in the .env file.")
        return

    repo_data = []

    # Walk through the directories in GITHUB_BASE
    for root, dirs, files in os.walk(GITHUB_BASE):
        # Check if the directory is a Git repository by looking for a '.git' folder
        if '.git' in dirs:
            relative_path = os.path.relpath(root, GITHUB_BASE)
            remote_url = get_remote_url(root)
            if remote_url:
                repo_data.append((relative_path, remote_url))
                print(f"Indexed repository: {relative_path} -> {remote_url}")
            else:
                print(f"Warning: No remote URL found for repository at {relative_path}")

    # Sort the data alphabetically by path
    repo_data.sort(key=lambda x: x[0])

    # Write data to CSV
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['path (relative to base)', 'remote repo url'])
        writer.writerows(repo_data)

    # Confirmation message
    print(f"{len(repo_data)} repositories written to index: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()