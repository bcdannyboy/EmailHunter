import requests
import re
import sys
import argparse
from serpapi import GoogleSearch
import csv
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

# Array of google dorks
google_dorks = [
    '@example.com',
    '"@example.com"',
    'allintext: @example.com',
    'intext:@example.com email',
    'intitle:"example.com email"',
    'inurl: github.com "@example.com"',
    'site:linkedin.com "@example.com"',
    'site:stackoverflow.com "@example.com"',
    'site:gitlab.com "@example.com"',
    'site:twitter.com "@example.com"',
    'site:facebook.com "@example.com"',
    'site:reddit.com "@example.com"',
    'site:medium.com "@example.com"',
    'site:quora.com "@example.com"',
    'filetype:pdf "@example.com"',
    'filetype:doc "@example.com"',
    'filetype:xls "@example.com"',
    'filetype:txt "@example.com"',
    'inurl:contact "@example.com"',
    'inurl:about "@example.com"',
    'inurl:team "@example.com"',
    'inurl:directory "@example.com"',
    'inurl:profiles "@example.com"',
    'inurl:staff "@example.com"',
    'inurl:members "@example.com"',
    'inurl:users "@example.com"',
    'inurl:people "@example.com"',
    'inurl:alumni "@example.com"',
    'inurl:faculty "@example.com"',
    'inurl:contributors "@example.com"',
    'inurl:emails "@example.com"',
    'inurl:contacts "@example.com"',
    'inurl:directory "@example.com"',
    'site:*.example.com inurl:email',
    'site:*.example.com inurl:contact',
    'site:*.example.com inurl:about',
    'site:*.example.com inurl:staff',
    'site:*.example.com inurl:profile',
    'site:*.example.com inurl:user',
    'site:*.example.com inurl:team',
    'site:*.example.com inurl:member',
    'site:*.example.com inurl:people',
    'site:*.example.com inurl:faculty',
    'site:*.example.com inurl:alumni',
    'site:*.example.com inurl:contributor',
    'site:*.example.com inurl:directory',
    'site:*.example.com inurl:emails',
    'site:*.example.com inurl:contacts',
    'site:*.example.com filetype:pdf',
    'site:*.example.com filetype:doc',
    'site:*.example.com filetype:xls',
    'site:*.example.com filetype:txt',
]

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Email Hunter: A tool to scrape emails from a given domain.")
parser.add_argument("-k", "--api_key", required=True, help="API key for SerpAPI")
parser.add_argument("-d", "--domain", required=True, help="Domain for email addresses") 
parser.add_argument("-m", "--max_results", default=100, type=int, help="Max search results")
parser.add_argument("-r", "--regex", required=True, help="Regex pattern for matching emails")
args = parser.parse_args()

# Initialize settings from arguments
DOMAIN = args.domain  
MAX_RESULTS = args.max_results
API_KEY = args.api_key
EMAIL_REGEX = args.regex

# Compiled regex patterns for efficiency
DOMAIN_REGEX = re.compile(rf"\b[A-Za-z0-9._%+-]+@{re.escape(DOMAIN)}\b")
EXACT_REGEX = re.compile(rf"{EMAIL_REGEX}@{re.escape(DOMAIN)}")

# Define the search terms for the Google search
search_terms = [dork.replace('example.com', DOMAIN) for dork in google_dorks]

# Initialize dictionaries to store found emails
exact_emails = {}
found_emails = {}

async def fetch_emails(session, link):
    try:
        async with session.get(link) as response:
            text = await response.text()

            domain_emails = re.findall(DOMAIN_REGEX, text)
            exact_match_emails = re.findall(EXACT_REGEX, text)

            exact = organize_emails(exact_match_emails, DOMAIN)
            found = organize_emails(domain_emails, DOMAIN)
            return exact, found
    except Exception as e:
        print(f"Error fetching {link}: {e}")
        return {}, {}

def organize_emails(emails, domain):
    """ Organize emails into a dictionary. """
    organized_emails = {}
    for email in emails:
        if email not in organized_emails:
            organized_emails[email] = set()
        organized_emails[email].add(domain)
    return organized_emails

def write_emails_to_csv(filename, email_dict):
    """ Write emails to a CSV file. """
    with open(filename, 'w', newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(['Email', 'Domains'])
        
        for email, domains in email_dict.items():
            writer.writerow([email, ', '.join(domains)])


async def main_async():
    print(f"Starting email search for domain {DOMAIN}")
    print(f"Using regex pattern: {EMAIL_REGEX}")
    print(f"Maximum Google search results per query: {MAX_RESULTS}")
    print("Beginning search queries...")

    async with aiohttp.ClientSession() as session:
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = []

            # Function to run serpapi searches in the executor
            def run_search(term):
                search = GoogleSearch({"api_key": API_KEY, "engine": "google", "q": term, "num": MAX_RESULTS})
                results = search.get_dict()
                links = [link['link'] for link in results.get('organic_results', [])]
                return links

            # Asynchronously schedule all serpapi searches and fetches
            for term in search_terms:
                # Schedule serpapi search
                search_task = loop.run_in_executor(executor, run_search, term)
                links = await search_task  # Wait for the search to complete

                # Schedule email fetches for each link
                for link in links:
                    fetch_task = loop.run_in_executor(executor, fetch_emails, session, link)
                    tasks.append(fetch_task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)

            # Process results
            for exact, found in results:
                for email, domains in exact.items():
                    if email not in exact_emails:
                        exact_emails[email] = set()
                    exact_emails[email].update(domains)

                for email, domains in found.items():
                    if email not in found_emails:
                        found_emails[email] = set()
                    found_emails[email].update(domains)

    # Write results to CSV files
    write_emails_to_csv('exact_matches.csv', exact_emails)
    write_emails_to_csv('found_emails.csv', found_emails)

    print("Email extraction finished. Results saved to CSV files.")

if __name__ == "__main__":
    asyncio.run(main_async())