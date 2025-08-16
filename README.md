# Shopify Insights-Fetcher

A Python FastAPI application that scrapes data from Shopify websites without using the official Shopify API and exposes a REST API for retrieving insights.

## Features

- Extracts product catalog from Shopify stores
- Identifies hero products featured on the homepage
- Retrieves store policies (Privacy, Return, Refund, Terms)
- Collects FAQs from the website
- Gathers social media handles
- Extracts contact information (emails, phone numbers)
- Retrieves information about the brand
- Collects important links (Order tracking, Contact, Blog, etc.)

## Tech Stack

- **Language**: Python
- **Framework**: FastAPI
- **Database**: MySQL (optional, for persistence)
- **Libraries**: BeautifulSoup4, aiohttp, requests, pydantic

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── health.py
│   │   │   │   └── insights.py
│   │   │   └── __init__.py
│   │   ├── routes.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── insights.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── scraper.py
│   │   └── __init__.py
│   └── __init__.py
├── main.py
├── requirements.txt
└── README.md
```



## License

MIT
