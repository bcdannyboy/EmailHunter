import base64
import html
import json
import requests
import argparse
import re
import csv
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Constants for the base URL of the GitHub API
BASE_API_URL = "https://api.github.com/"
SEARCHES_PER_MINUTE = 30
GENERAL_EMAIL_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@example.com\b',  # Standard email pattern
    r'[A-Za-z0-9._%+-]+ \[at\] example.com',  # Obfuscated pattern
    r'[A-Za-z0-9._%+-]+ at example.com',  # Another obfuscated pattern
    r'[A-Za-z0-9._%+-]+[ ]?@[ ]?example.com',  # Spaces around @
    r'[A-Za-z0-9._%+-]+\(at\)example.com',  # (at) instead of @
]

def fetch_content(content_url, headers, domain, user_regex_pattern):
    """
    Fetches content from a given URL and extracts emails using multiple regex patterns.
    Then checks these emails against a user-provided regex pattern for the local part of the email.
    Returns a dictionary mapping emails to sets of URLs where they were found.
    """
    print(f"Fetching content from {content_url}...")
    response = requests.get(content_url, headers=headers)

    # Check if the response is successful and is JSON
    if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
        try:
            content_response = response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {content_url}: {e}")
            return {}, {}
    else:
        print(f"Non-JSON response or error from {content_url}: Status code {response.status_code}")
        return {}, {}

    all_emails = {}
    user_matched_emails = {}

    if 'content' in content_response:
        content = content_response['content']

        # Decode from base64 if necessary
        if content_response.get('encoding') == 'base64':
            content = base64.b64decode(content).decode('utf-8')

        # Decode HTML entities
        content = html.unescape(content)

        # Replace 'example.com' with the actual domain in the regex patterns
        domain_specific_patterns = [pattern.replace('example.com', domain) for pattern in GENERAL_EMAIL_PATTERNS]

        # Search for all emails using the domain-specific regex patterns
        for pattern in domain_specific_patterns:
            found_emails = re.findall(pattern, content)
            for email in found_emails:
                all_emails.setdefault(email, set()).add(content_url)

        # Check all found emails against the user-provided regex pattern
        for email in all_emails:
            local_part = email.split('@')[0]
            if re.fullmatch(user_regex_pattern, local_part):
                user_matched_emails[email] = all_emails[email]

    return all_emails, user_matched_emails

def search_github(domain, token, regex_pattern=None):
    """
    Searches GitHub for email addresses associated with a specified domain,
    limiting to 30 searches per minute. It searches both code blobs and repositories.
    """

    print(f"Initiating search for emails with domain '{domain}'" + (f" and pattern '{regex_pattern}'" if regex_pattern else "") + ".")

    emails = {}
    exact_matches = {}
    page = 1
    last_search_time = time.time()

    headers = {'Authorization': f'token {token}'}

    while True:
        # Rate limit to 30 searches per minute
        if time.time() - last_search_time < 60 / SEARCHES_PER_MINUTE:
            time.sleep(60 / SEARCHES_PER_MINUTE)

        query = quote_plus(f"@{domain}")
        # Search in code blobs
        code_search_url = f"{BASE_API_URL}search/code?q={query}&page={page}&per_page=100"
        # Search in repositories
        repo_search_url = f"{BASE_API_URL}search/repositories?q={query}&page={page}&per_page=100"

        # Process code search
        code_response = requests.get(code_search_url, headers=headers).json()
        process_search_response(code_response, headers, domain, regex_pattern, emails, exact_matches, 'git_url')

        # Process repository search
        repo_response = requests.get(repo_search_url, headers=headers).json()
        process_search_response(repo_response, headers, domain, regex_pattern, emails, exact_matches, 'html_url')

        last_search_time = time.time()

        if 'next' not in code_response.get('links', {}) and 'next' not in repo_response.get('links', {}):
            print("No next page link found in response, ending search.")
            break

        page += 1

    return emails, exact_matches

def process_search_response(response, headers, domain, regex_pattern, emails, exact_matches, url_key):
    """
    Processes a search response from GitHub API, extracting emails from content.

    :param response: The response from the GitHub API.
    :param headers: Headers for the API requests.
    :param domain: The domain to search for in email addresses.
    :param regex_pattern: Optional regex pattern to match the local part of email addresses.
    :param emails: Set to store found emails.
    :param exact_matches: Set to store emails matching the regex pattern.
    """
    if 'message' in response:
        print(f"Error from GitHub API: {response['message']}")
        return

    if 'items' not in response:
        print("No more items found.")
        return

    content_urls = [item[url_key] for item in response['items'] if url_key in item]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_content, url, headers, domain, regex_pattern) for url in content_urls]
        for future in as_completed(futures):
            found_emails, found_exact_matches = future.result()
            for email, urls in found_emails.items():
                emails.setdefault(email, set()).update(urls)
            for email, urls in found_exact_matches.items():
                exact_matches.setdefault(email, set()).update(urls)

def write_to_csv(filename, data):
    """
    Writes a set of data to a CSV file.

    :param filename: The name of the file to write to.
    :param data: The data to write into the file.
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        for email, urls in data.items():
            writer.writerow([email, list(urls)])
        print(f"Data successfully written to {filename}")

def main():
    """
    Main function to parse arguments and initiate the email search process.
    """
    parser = argparse.ArgumentParser(description='Search GitHub for email addresses associated with a domain')
    parser.add_argument('-d', '--domain', type=str, required=True, help='The domain to search for')
    parser.add_argument('-r', '--regex', type=str, required=False, help='Regex pattern for matching email local part')
    parser.add_argument('-k', '--token', type=str, required=True, help='GitHub API token')

    args = parser.parse_args()

    emails, exact_matches = search_github(args.domain, args.token, args.regex)

    write_to_csv('git_emails.csv', emails)

    if args.regex:
        write_to_csv('exact_git_emails.csv', exact_matches)

if __name__ == "__main__":
    main()
