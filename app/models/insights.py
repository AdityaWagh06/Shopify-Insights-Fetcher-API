from typing import Dict, List, Optional, Any
from pydantic import BaseModel, HttpUrl, EmailStr, validator
import re

class InsightsRequest(BaseModel):
    """Request model for insights endpoint"""
    website_url: str
    
    @validator('website_url')
    def validate_website_url(cls, v):
        # Basic URL validation
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class FAQ(BaseModel):
    """Model for FAQ items"""
    question: str
    answer: str

class Socials(BaseModel):
    """Model for social media handles"""
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    tiktok: Optional[str] = None
    twitter: Optional[str] = None  # X/Twitter
    youtube: Optional[str] = None
    linkedin: Optional[str] = None
    pinterest: Optional[str] = None

class Contact(BaseModel):
    """Model for contact information"""
    emails: List[str] = []
    phones: List[str] = []

class Policies(BaseModel):
    """Model for store policies"""
    privacy: Optional[str] = None
    return_policy: Optional[str] = None
    refund: Optional[str] = None
    terms: Optional[str] = None

class Links(BaseModel):
    """Model for important links"""
    order_tracking: Optional[str] = None
    contact_us: Optional[str] = None
    blogs: Optional[str] = None
    shipping: Optional[str] = None
    careers: Optional[str] = None

class Product(BaseModel):
    """Model for product information"""
    id: Optional[str] = None
    title: str
    handle: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    image: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = []
    variants: Optional[List[Dict[str, Any]]] = None

class BrandContext(BaseModel):
    """Response model for brand context"""
    brand: str
    products: List[Product] = []
    hero_products: List[Product] = []
    policies: Policies = Policies()
    faqs: List[FAQ] = []
    socials: Socials = Socials()
    contact: Contact = Contact()
    about: Optional[str] = None
    links: Links = Links()