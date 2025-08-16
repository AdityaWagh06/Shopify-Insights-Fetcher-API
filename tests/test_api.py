import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from app.models.insights import BrandContext, Product
from app.core.exceptions import WebsiteNotFoundException, InvalidShopifyStoreError

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.services.scraper.ShopifyScraper")
def test_insights_success(mock_scraper):
    """Test insights endpoint with successful response"""
    # Mock the scraper instance and its get_brand_context method
    mock_instance = MagicMock()
    mock_scraper.return_value = mock_instance
    
    # Create a sample brand context
    sample_product = Product(
        id="1",
        title="Test Product",
        handle="test-product",
        description="Test description",
        price="19.99",
        image="https://example.com/image.jpg",
        url="https://example.com/products/test-product",
        tags=["test", "sample"]
    )
    
    sample_brand_context = BrandContext(
        brand="example.com",
        products=[sample_product],
        hero_products=[sample_product]
    )
    
    # Set the return value for get_brand_context
    mock_instance.get_brand_context.return_value = sample_brand_context
    
    # Make the request
    response = client.post(
        "/api/v1/insights",
        json={"website_url": "https://example.com"}
    )
    
    # Assert the response
    assert response.status_code == 200
    assert response.json()["brand"] == "example.com"
    assert len(response.json()["products"]) == 1
    assert response.json()["products"][0]["title"] == "Test Product"


@patch("app.services.scraper.ShopifyScraper")
def test_insights_website_not_found(mock_scraper):
    """Test insights endpoint with website not found error"""
    # Mock the scraper instance to raise WebsiteNotFoundException
    mock_instance = MagicMock()
    mock_scraper.return_value = mock_instance
    mock_instance.get_brand_context.side_effect = WebsiteNotFoundException()
    
    # Make the request
    response = client.post(
        "/api/v1/insights",
        json={"website_url": "https://nonexistent-website.com"}
    )
    
    # Assert the response
    assert response.status_code == 401
    assert "Website not found" in response.json()["detail"]


@patch("app.services.scraper.ShopifyScraper")
def test_insights_invalid_shopify_store(mock_scraper):
    """Test insights endpoint with invalid Shopify store error"""
    # Mock the scraper instance to raise InvalidShopifyStoreError
    mock_instance = MagicMock()
    mock_scraper.return_value = mock_instance
    mock_instance.get_brand_context.side_effect = InvalidShopifyStoreError()
    
    # Make the request
    response = client.post(
        "/api/v1/insights",
        json={"website_url": "https://not-a-shopify-store.com"}
    )
    
    # Assert the response
    assert response.status_code == 400
    assert "not a valid Shopify store" in response.json()["detail"]


@patch("app.services.scraper.ShopifyScraper")
def test_insights_internal_error(mock_scraper):
    """Test insights endpoint with internal server error"""
    # Mock the scraper instance to raise a generic Exception
    mock_instance = MagicMock()
    mock_scraper.return_value = mock_instance
    mock_instance.get_brand_context.side_effect = Exception("Something went wrong")
    
    # Make the request
    response = client.post(
        "/api/v1/insights",
        json={"website_url": "https://example.com"}
    )
    
    # Assert the response
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]