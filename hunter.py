import requests
import re
import sys
import argparse
from serpapi import GoogleSearch
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import configparser

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Email Hunter: A tool to scrape emails from a given domain.")
parser.add_argument("-k", "--api_key", required=True, help="API key for SerpAPI")
parser.add_argument("-d", "--domain", required=True, help="Domain for email addresses")
parser.add_argument("-m", "--max_results", default=100, type=int, help="Max search results")
parser.add_argument("-r", "--regex_config", required=True, help="Regex config file")
args = parser.parse_args()

# Initialize settings from arguments
DOMAIN = args.domain
MAX_RESULTS = args.max_results
API_KEY = args.api_key

# Load regex patterns from config file
config = configparser.ConfigParser()
config.read(args.regex_config)
EMAIL_REGEX = config['REGEX']['email']
LOCAL_REGEX = config['REGEX']['local']

# Define the search term for the Google search
search_term = f"site:*.com @{DOMAIN}"

# Initialize a dictionary to store found emails
emails = {}

def main():
    """
    Main function to orchestrate the email hunting process.
    """
    print(f"Starting email search for domain {DOMAIN} with maximum results {MAX_RESULTS}...")

    # Set up and perform the Google search
    search = GoogleSearch({"api_key": API_KEY, "engine": "google", "q": search_term, "num": MAX_RESULTS})
    results = search.get_dict()
    links = [link['link'] for link in results['organic_results']]

    # Use ThreadPoolExecutor to fetch emails concurrently
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_emails, link) for link in tqdm(links, desc="Processing links")]
        for future in tqdm(futures, desc="Fetching emails"):
            email_results = future.result()
            for email, domains in email_results.items():
                if email not in emails:
                    emails[email] = set()
                emails[email].update(domains)

    # Write the collected emails to a CSV file
    with open('emails.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Email', 'Domains'])
        for email, domains in emails.items():
            writer.writerow([email, ', '.join(domains)])

    print("Email hunting complete. Results saved to emails.csv")

def fetch_emails(link):
    """
    Fetch and extract emails from a given link.
    """
    # Extract the domain from the link
    domain = re.search(r"https?://([^/]+)/", link).group(1)

    # Fetch the webpage content
    page = requests.get(link)

    # Find all emails on the page using the regex pattern
    found_emails = re.findall(EMAIL_REGEX, page.text)

    # Filter and organize emails
    local_emails = {}
    for email in found_emails:
        local = email.split("@")[0]
        if re.match(LOCAL_REGEX, local):
            if email not in local_emails:
                local_emails[email] = set()
            local_emails[email].add(domain)

    return local_emails

if __name__ == "__main__":
    main()
