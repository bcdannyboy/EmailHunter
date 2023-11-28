# EmailHunter

## Overview

EmailHunter is a toolkit for scraping email addresses from the web. It leverages GitHub's API and Google search to find emails associated with a particular domain. Useful for research, recruitment, networking and more. Requires a GitHub token and SerpAPI key.

## Features

- Domain-focused email scraping
- GitHub code and repo search
- Google dork search queries
- Regex filtering
- Multithreading for faster processing
- CSV export

## Installation

```
$ git clone https://github.com/bcdannyboy/EmailHunter.git
$ cd EmailHunter
$ pip install -r requirements.txt
```

Python 3.6 or higher required.

## Usage

There are now two separate scripts:

### GitHub Search

`python git_hunter.py -d DOMAIN -r "REGEX" -k GITHUB_TOKEN`

Example:

`python git_hunter.py -d example.com -r "^[a-zA-Z0-9]+[._-]?[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" -k GITHUB_TOKEN`

This will search for all GitHub emails associated with the domain `example.com` and filter them using the regex provided. The GitHub token is required for authentication. You can generate one [here](https://github.com/settings/tokens?type=beta)

### Google Search

`python google_hunter.py -d DOMAIN -r "REGEX" -k SERPAPI_KEY -m MAX_RESULTS`

Example:

`python google_hunter.py -d example.com -r "^[a-zA-Z0-9]+[._-]?[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" -k SERPAPI_KEY -m 100`

This will search for all Google results associated with the domain `example.com` and filter them using the regex provided. The SerpAPI key is required for authentication. You can generate one [here](https://serpapi.com/)

### Both

Both scripts share the same arguments:

- `-d`: Target domain
- `-r`: Regex filter
- `-k`: API key

Google Search also has:

- `-m`: Max results

## Output

The scripts output the following files:

### Git Hunter Output

- `git_emails.csv`: All GitHub emails found
- `exact_git_emails.csv`: Matches regex filter

### Google Hunter Output

- `exact_matches.csv`: Google results matching regex
- `found_emails.csv`: All Google results