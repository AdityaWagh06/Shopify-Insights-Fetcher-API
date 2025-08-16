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

## Installation

1. Clone the repository

```bash
git clone <repository-url>
cd shopify-insights-fetcher
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the virtual environment

- Windows:
```bash
venv\Scripts\activate
```

- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

1. Start the server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

2. Access the API documentation

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check

```
GET /api/v1/healthz
```

Returns the health status of the API.

### Get Insights

```
POST /api/v1/insights
```

Request body:
```json
{
  "website_url": "https://example.com"
}
```

Returns a JSON object containing the brand context with products, policies, FAQs, social handles, contact information, etc.

## Error Handling

- **401**: Website not found or not accessible
- **400**: Invalid Shopify store
- **500**: Internal server error

## Development

### Adding New Features

1. Create new endpoints in the `app/api/v1/endpoints/` directory
2. Add new models in the `app/models/` directory
3. Implement new services in the `app/services/` directory
4. Update the API router in `app/api/routes.py`

### Running Tests

```bash
python -m pytest
```

## License

MIT