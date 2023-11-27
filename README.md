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
- `-m` or `--max_presults`: The maximum number of results to pull from.
- `-r` or `--regex`: Regex patterns to match local email address parts.

### Example

`python hunter.py -k abc123xyz -d bcdefense.com -r [A-Za-z09]{6}`

This command will search for email addresses that belong to the bcdefense.com domain and that have a local part of 6 characters in length. The results will be saved in a CSV file named emails.csv.

## Output

EmailHunter outputs the results in a CSV file named emails.csv, containing two columns: 'Email' and 'Domains'. Each row represents a unique email address and the domain(s) where it was found.