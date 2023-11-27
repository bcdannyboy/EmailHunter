import requests
import re  
import sys
import argparse
from serpapi import GoogleSearch
import csv
from concurrent.futures import ThreadPoolExecutor 
from tqdm import tqdm

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

# Define the search terms for the Google search  
search_terms = [dork.replace('example.com', DOMAIN) for dork in google_dorks]

# Initialize dictionaries to store found emails  
exact_emails = {}
found_emails = {}

def main():

    print(f"Starting email search for domain {DOMAIN}")
    print(f"Using regex pattern {EMAIL_REGEX}") 
    print(f"Pulling a maximum of {MAX_RESULTS} results from Google")
    
    searched = 0
    for term in search_terms:
        searched += 1
        print(f"Searching query {searched}/{len(search_terms)}: {term}")

        # Set up and perform the Google search 
        search = GoogleSearch({"api_key": API_KEY, "engine": "google", "q": term, "num": MAX_RESULTS})
        results = search.get_dict() 
        links = [link['link'] for link in results['organic_results']] 
        
        # Use ThreadPoolExecutor to fetch emails concurrently 
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_emails, link) for link in tqdm(links, desc="Processing links")]
            
            for future in tqdm(futures, desc="Fetching emails"):
                exact, found = future.result()
                
                for email, domains in exact.items():
                    if email not in exact_emails:
                        exact_emails[email] = set()  
                    exact_emails[email].update(domains)

                for email, domains in found.items():
                    if email not in found_emails:
                        found_emails[email] = set()
                    found_emails[email].update(domains)
                    
    # Write the exact match emails to a CSV file 
    write_emails_to_csv('exact_matches.csv', exact_emails)

    # Write all found emails to a CSV file
    write_emails_to_csv('found_emails.csv', found_emails)
            
    print("Email hunting complete. Results saved to exact_matches.csv and found_emails.csv")
        
def fetch_emails(link):
    """ Fetch and extract emails from a given link. """  
    domain = DOMAIN  # Use the domain from the args
    
    # Fetch the webpage content 
    page = requests.get(link)
    
    # Regex pattern for extracting all emails associated with the domain
    domain_regex = rf"\b[A-Za-z0-9._%+-]+@{re.escape(domain)}\b"

    # Find all emails belonging to the domain 
    domain_emails = re.findall(domain_regex, page.text)

    # Pattern for emails that match the provided regex  
    exact_regex = rf"{EMAIL_REGEX}@{re.escape(domain)}"

    # Find emails that exactly match the provided regex
    exact_match_emails = re.findall(exact_regex, page.text)
    
    # Organize emails  
    exact = organize_emails(exact_match_emails, domain)
    found = organize_emails(domain_emails, domain)
    
    return exact, found

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
            
if __name__ == "__main__":
    main()