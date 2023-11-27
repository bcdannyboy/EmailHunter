# EmailHunter

## Overview

EmailHunter is a powerful and efficient tool designed to scrape email addresses from web pages. It leverages regular expressions (regex) and Google dorks (search queries) to find emails associated with a specific domain. This tool is particularly useful for gathering email addresses for business, research, or networking purposes. *It requires a SerpAPI API key to function.*

## Features
- Domain-Specific Email Hunting: Focuses on a specified domain to gather relevant email addresses.
- Regex-Based Filtering: Uses regular expressions to match and filter email addresses and local parts.
- Google Dorks Integration: Employs Google dorks for efficient and targeted web scraping.
- Concurrent Processing: Utilizes multi-threading for faster processing of multiple web pages.
- CSV Output: Outputs the gathered emails into a CSV file for easy use and analysis.

## Installation
To use EmailHunter, you need Python installed on your system. Clone the repository and install the required packages:

```
$ git clone https://github.com/bcdannyboy/EmailHunter.git
$ cd EmailHunter
$ pip install -r requirements.txt
```

## Basic Usage

`python hunter.py -k YOUR_SERPAPI_KEY -d TARGET_DOMAIN -r regex.ini`

- `-k` or `--api_key`: Your SerpAPI key.
- `-d` or `--domain`: The target domain to search for email addresses.
- `-r` or `--regex_config`: Path to the regex configuration file.

### Example

`python hunter.py -k abc123xyz -d bcdefense.com -r regex.ini`

This command will search for email addresses that belong to the bcdefense.com domain, using the regex patterns defined in regex.ini.

## regex.ini File

The regex.ini file is a crucial component of EmailHunter. It contains two regular expressions:

- `email`: Defines the pattern for matching email addresses. Example: `[^@]+@bcdefense.com` matches any string followed by @bcdefense.com.
- `local`: Specifies the pattern for the local part (before the @ symbol) of the email address. Example: `[A-Za-z0-9]{6}` matches any alphanumeric string of exactly 6 characters.

### Customizing regex.ini

You can modify regex.ini to suit your specific needs. For instance, to hunt for emails from a different domain, change the email pattern accordingly. Similarly, adjust the local pattern to match different criteria for the local part of the email addresses.

## Output

EmailHunter outputs the results in a CSV file named emails.csv, containing two columns: 'Email' and 'Domains'. Each row represents a unique email address and the domain(s) where it was found.