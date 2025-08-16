from typing import Any, Dict, Optional

class AppException(Exception):
    """Base exception class for application exceptions"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.data = data
        
        super().__init__(self.detail)

class WebsiteNotFoundException(AppException):
    """Exception raised when a website is not found or not accessible"""
    
    def __init__(self, detail: str = "Website not found or not accessible"):
        super().__init__(status_code=401, detail=detail)

class InternalServerError(AppException):
    """Exception raised for internal server errors"""
    
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)

class InvalidShopifyStoreError(AppException):
    """Exception raised when a website is not a valid Shopify store"""
    
    def __init__(self, detail: str = "The provided URL is not a valid Shopify store"):
        super().__init__(status_code=400, detail=detail)