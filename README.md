Euromonitor Data Engineer Assignment
=======================================

Python implementation of both scraping exercises.

Requirements
------------
- Python 3.10+
- Internet access

Install dependencies:

    python -m pip install -r requirements.txt


Exercise 1: Glossier
--------------------

India:

    python glossier.py --locale in --output data/glossier_india.csv

US:

    python glossier.py --locale us --output data/glossier_us.csv

Variants:

    python glossier.py --locale in --variants --output data/glossier_india_variants.csv

The output contains:

    product_name
    product_id
    image
    url
    price
    scraped_at
    description


Exercise 2: Cellarbrations
--------------------------

Whisky category:

    https://www.cellarbrations.com.au/sm/pickup/rsid/3331/categories/spirits/whisky-id-Whisky_Food

Run:

    python cellarbrations.py --output data/cellarbrations_whisky.csv

The output contains:

    product_name
    product_id
    image
    url
    price
    scraped_at
    description
    measuring_unit
    units


Approach
--------

Glossier uses public Shopify JSON endpoints.

Cellarbrations uses direct HTTP requests with curl_cffi and Chrome
impersonation. The category response is used to discover products and
the storefront API is used to retrieve product details.

Browser automation is not required because the required data can be
obtained through HTTP requests.


Validation
----------

Before submission, check:

- Row counts
- Duplicate product IDs
- Empty descriptions
- Images
- Prices
- Cellarbrations measuring_unit and units
- Product URLs


AI Usage
--------

ChatGPT was used during development for research, Python boilerplate,
scraping approaches, troubleshooting and documentation.

The code was manually reviewed and tested by the candidate.


Submission
----------

- Add Evaldas.Lukasevicius@Euromonitor.com as a repository collaborator.
- Include the GitHub repository URL in the submission email.
- Include README.md, notes.txt and requirements.txt.
- Do not commit .venv/ or temporary files.
- Ensure the final code can be explained during a follow-up discussion.