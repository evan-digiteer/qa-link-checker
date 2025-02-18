# Link Checker

A Selenium-based Python tool to check for broken links on websites and generate comprehensive HTML reports.

## Features

- Checks all links on a specified website
- Real-time progress tracking
- Generates interactive HTML reports with:
  - Summary statistics
  - Collapsible sections for passed and failed links
  - Base64-encoded screenshots of broken link pages
  - Clickable links for verification
- Headless browser operation
- Configurable timeout settings

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your settings:
   ```properties
   BASE_URL=https://example.com
   REPORTS_DIR=reports
   TIMEOUT=10
   ```

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Start checking all links on the specified website
2. Show real-time progress in the console
3. Generate an HTML report containing:
   - Total links checked
   - Number of passed/failed links
   - Screenshots of pages with broken links
   - Collapsible sections for easy navigation
4. Automatically open the report in your default browser

## Project Structure

```
qa-link-checker/
├── config/
│   └── config.py          # Configuration settings
├── utils/
│   ├── webdriver.py       # Selenium WebDriver setup
│   ├── link_checker.py    # Main link checking logic
│   └── report_template.html # HTML report template
├── reports/               # Generated HTML reports
├── .env                   # Environment variables
├── requirements.txt       # Project dependencies
├── main.py               # Entry point
└── README.md
```

## Configuration Options

- `BASE_URL`: Target website URL to check
- `REPORTS_DIR`: Directory for HTML reports (default: 'reports')
- `TIMEOUT`: Request timeout in seconds (default: 10)

## Requirements

- Python 3.7+
- Chrome/Chromium browser
- Required Python packages (see requirements.txt)

## Report Features

The generated HTML report includes:
- Summary statistics
- Collapsible sections for:
  - Broken links with screenshots
  - Successfully validated links
- Interactive elements
- Responsive design
- Direct links to verify URLs