import requests
import re     
import sys
import argparse
from serpapi import GoogleSearch   
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import configparser

# Arguments  
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--api_key", required=True, help="API key for SerpAPI")
parser.add_argument("-d", "--domain", required=True, help="Domain for email addresses")  
parser.add_argument("-m", "--max_results", default=100, type=int, help="Max search results")
parser.add_argument("-r", "--regex_config", required=True, help="Regex config file")  
args = parser.parse_args()   

# Settings
DOMAIN = args.domain      
MAX_RESULTS = args.max_results     
API_KEY = args.api_key   

# Regex  
config = configparser.ConfigParser()
config.read(args.regex_config)
EMAIL_REGEX = config['REGEX']['email']
LOCAL_REGEX = config['REGEX']['local']  

# Search term   
search_term = f"site:*.com @{DOMAIN}"       

# Email storage  
emails = {} 

def main():

    # Main function  
    print("Searching...")
    
    search = GoogleSearch({"api_key": API_KEY, 
                           "engine": "google",
                           "q": search_term,
                           "num": MAX_RESULTS
                          })
                           
    results = search.get_dict()
    links = [link['link'] for link in results['organic_results']]  
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_emails, link) for link in links]
        for future in futures:  
            future.result()
            
    # Write emails dict                
    with open('emails.csv', 'w') as f:
        writer = csv.writer(f) 
        writer.writerow(['Email', 'Domains'])
        for email, domains in emails.items():
            writer.writerow([email, ', '.join(domains)])
            
    print("Done!")

    
def fetch_emails(link):
    
    # Extract domain  
    domain = re.search(r"https?://([^/]+)/", link).group(1) 
    
    # Fetch page  
    page = requests.get(link)
    
    # Find emails
    found = re.findall(EMAIL_REGEX, page.text) 
    
    # Filter     
    emails = {}
    for email in found:
        local = email.split("@")[0]
        if re.match(LOCAL_REGEX, local):
            if email not in emails:
                emails[email] = []  
            emails[email].append(domain)

    return emails

    
if __name__ == "__main__":
    main()