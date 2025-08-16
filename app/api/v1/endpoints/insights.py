from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from app.models.insights import InsightsRequest, BrandContext
from app.services.scraper import ShopifyScraper
from app.core.exceptions import WebsiteNotFoundException, InternalServerError, InvalidShopifyStoreError

router = APIRouter()

@router.post("/insights", response_model=BrandContext)
async def get_insights(request: InsightsRequest) -> Any:
    """Get insights from a Shopify website"""
    try:
        scraper = ShopifyScraper(request.website_url)
        return await scraper.get_brand_context()
    except WebsiteNotFoundException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except InvalidShopifyStoreError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")