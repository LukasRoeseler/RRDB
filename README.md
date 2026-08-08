# RRDB
Dataset version of the Registered Reports Database for the Open Research Extension

## Zotero Registered Reports Tracker

This repository automatically tracks and extracts the ["Registered Reports" Zotero Library](https://www.zotero.org/groups/5937153/registered_reports/library) (Group ID `5937153`) into a clean, easy-to-read CSV format.

### Automated Updates

The dataset is updated automatically every Monday at midnight via GitHub Actions. You can also trigger an update manually from the **Actions** tab.

### Accessing the Data

The latest version of the dataset is always available in this repository:
[`zotero_registered_reports.csv`](./zotero_registered_reports.csv)

### Local Development

If you want to run the extraction script locally:

1. Clone the repository
2. Install the requirements: `pip install -r requirements.txt`
3. Run the script: `python fetch_zotero.py`

