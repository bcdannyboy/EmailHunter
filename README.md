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

`python git_hunter.py -d DOMAIN -r REGEX -k GITHUB_TOKEN`

### Google Search

`python google_hunter.py -d DOMAIN -r REGEX -k SERPAPI_KEY -m MAX_RESULTS`

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

- `git_emails.csv``: All GitHub emails found
- `exact_git_emails.csv`: Matches regex filter

### Google Hunter Output

- `exact_matches.csv`: Google results matching regex
- `found_emails.csv`: All Google results