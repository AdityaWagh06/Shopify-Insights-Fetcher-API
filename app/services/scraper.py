import re
import json
from typing import Dict, List, Optional, Any, Tuple
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.models.insights import BrandContext, Product, FAQ, Socials, Contact, Policies, Links
from app.core.exceptions import WebsiteNotFoundException, InvalidShopifyStoreError

class ShopifyScraper:
    """Service for scraping data from Shopify websites"""
    
    def __init__(self, website_url: str):
        # Normalize URL
        self.base_url = self._normalize_url(website_url)
        self.session = None
        self.soup = None
        self.is_shopify = False
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to ensure it has a scheme and no trailing slash"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash if present
        parsed = urlparse(url)
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        
        return url
    
    async def _init_session(self):
        """Initialize aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session is not None:
            await self.session.close()
            self.session = None
    
    async def _fetch_url(self, url: str) -> Tuple[str, int]:
        """Fetch URL and return content and status code"""
        await self._init_session()
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                content = await response.text()
                return content, response.status
        except aiohttp.ClientError as e:
            raise WebsiteNotFoundException(f"Failed to fetch {url}: {str(e)}")
    
    async def _check_is_shopify(self) -> bool:
        """Check if the website is a Shopify store"""
        content, status = await self._fetch_url(self.base_url)
        
        if status != 200:
            raise WebsiteNotFoundException(f"Website returned status code {status}")
        
        # Parse HTML
        self.soup = BeautifulSoup(content, 'html.parser')
        
        # Check for Shopify indicators
        shopify_indicators = [
            'Shopify.theme' in content,
            'cdn.shopify.com' in content,
            'myshopify.com' in content,
            self.soup.find('link', {'href': re.compile(r'cdn\.shopify\.com')}),
            self.soup.find('script', {'src': re.compile(r'cdn\.shopify\.com')})
        ]
        
        self.is_shopify = any(shopify_indicators)
        return self.is_shopify
    
    async def _fetch_products(self) -> List[Product]:
        """Fetch products from Shopify store"""
        products = []
        
        # Try different product endpoints
        product_endpoints = [
            '/products.json?limit=250',
            '/collections/all/products.json?limit=250'
        ]
        
        for endpoint in product_endpoints:
            try:
                content, status = await self._fetch_url(urljoin(self.base_url, endpoint))
                
                if status == 200:
                    data = json.loads(content)
                    
                    if 'products' in data:
                        for product_data in data['products']:
                            product = Product(
                                id=str(product_data.get('id')),
                                title=product_data.get('title', ''),
                                handle=product_data.get('handle', ''),
                                description=product_data.get('body_html', ''),
                                price=self._get_product_price(product_data),
                                image=self._get_product_image(product_data),
                                url=urljoin(self.base_url, f"/products/{product_data.get('handle')}"),
                                tags=product_data.get('tags', []) if isinstance(product_data.get('tags'), list) else product_data.get('tags', '').split(', '),
                                variants=product_data.get('variants', [])
                            )
                            products.append(product)
                        
                        # If we found products, no need to try other endpoints
                        break
            except Exception as e:
                # Continue to next endpoint if this one fails
                continue
        
        return products
    
    def _get_product_price(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Extract product price from product data"""
        if 'variants' in product_data and product_data['variants']:
            variant = product_data['variants'][0]
            if 'price' in variant:
                return variant['price']
        return None
    
    def _get_product_image(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Extract product image from product data"""
        if 'images' in product_data and product_data['images']:
            image = product_data['images'][0]
            if 'src' in image:
                return image['src']
        return None
    
    async def _fetch_hero_products(self, all_products: List[Product]) -> List[Product]:
        """Fetch hero products (products featured on homepage)"""
        if not self.soup:
            content, _ = await self._fetch_url(self.base_url)
            self.soup = BeautifulSoup(content, 'html.parser')
        
        hero_products = []
        product_handles = set()
        
        # Look for product links on homepage
        product_links = self.soup.find_all('a', href=re.compile(r'/products/'))
        
        for link in product_links:
            href = link.get('href', '')
            handle = href.split('/')[-1].split('?')[0]
            
            if handle and handle not in product_handles:
                product_handles.add(handle)
                
                # Find matching product from all products
                matching_product = next((p for p in all_products if p.handle == handle), None)
                
                if matching_product:
                    hero_products.append(matching_product)
        
        return hero_products[:10]  # Limit to 10 hero products
    
    async def _fetch_policies(self) -> Policies:
        """Fetch store policies"""
        policies = Policies()
        
        # Common policy paths
        policy_paths = {
            'privacy': ['/policies/privacy-policy', '/pages/privacy-policy', '/pages/privacy'],
            'return_policy': ['/policies/refund-policy', '/pages/refund-policy', '/pages/returns', '/pages/return-policy'],
            'refund': ['/policies/refund-policy', '/pages/refund-policy', '/pages/refunds'],
            'terms': ['/policies/terms-of-service', '/pages/terms-of-service', '/pages/terms', '/pages/terms-conditions']
        }
        
        for policy_type, paths in policy_paths.items():
            for path in paths:
                try:
                    content, status = await self._fetch_url(urljoin(self.base_url, path))
                    
                    if status == 200:
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Look for main content
                        main_content = soup.find('main')
                        if not main_content:
                            main_content = soup.find('div', {'class': re.compile(r'(content|main|page).*')})
                        
                        if main_content:
                            # Extract text and clean it up
                            policy_text = main_content.get_text(separator='\n', strip=True)
                            
                            # Set the policy text
                            setattr(policies, policy_type, policy_text)
                            
                            # Break the inner loop once we found a policy
                            break
                except Exception:
                    # Continue to next path if this one fails
                    continue
        
        return policies
    
    async def _fetch_faqs(self) -> List[FAQ]:
        """Fetch FAQs from the website"""
        faqs = []
        
        # Common FAQ paths
        faq_paths = ['/faq', '/pages/faq', '/pages/faqs', '/pages/frequently-asked-questions']
        
        for path in faq_paths:
            try:
                content, status = await self._fetch_url(urljoin(self.base_url, path))
                
                if status == 200:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for FAQ sections
                    # Method 1: Look for accordion-style FAQs
                    accordion_items = soup.find_all(['details', 'div'], {'class': re.compile(r'(accordion|faq-item|collapse).*')})
                    
                    if accordion_items:
                        for item in accordion_items:
                            question_elem = item.find(['summary', 'h3', 'h4', 'button', 'div'], {'class': re.compile(r'(question|header|title).*')})
                            answer_elem = item.find(['div', 'p'], {'class': re.compile(r'(answer|content|body).*')})
                            
                            if question_elem and answer_elem:
                                question = question_elem.get_text(strip=True)
                                answer = answer_elem.get_text(strip=True)
                                
                                if question and answer:
                                    faqs.append(FAQ(question=question, answer=answer))
                    
                    # Method 2: Look for question-answer pairs
                    if not faqs:
                        questions = soup.find_all(['h3', 'h4', 'strong'], {'class': re.compile(r'(question|faq-question).*')})
                        
                        for q in questions:
                            question = q.get_text(strip=True)
                            answer_elem = q.find_next(['p', 'div'])
                            
                            if answer_elem:
                                answer = answer_elem.get_text(strip=True)
                                
                                if question and answer:
                                    faqs.append(FAQ(question=question, answer=answer))
                    
                    # If we found FAQs, no need to try other paths
                    if faqs:
                        break
            except Exception:
                # Continue to next path if this one fails
                continue
        
        return faqs
    
    async def _fetch_social_handles(self) -> Socials:
        """Fetch social media handles"""
        if not self.soup:
            content, _ = await self._fetch_url(self.base_url)
            self.soup = BeautifulSoup(content, 'html.parser')
        
        socials = Socials()
        
        # Look for social media links in footer or header
        social_patterns = {
            'instagram': r'(instagram\.com|instagram)',
            'facebook': r'(facebook\.com|facebook)',
            'tiktok': r'(tiktok\.com|tiktok)',
            'twitter': r'(twitter\.com|x\.com)',
            'youtube': r'(youtube\.com|youtube)',
            'linkedin': r'(linkedin\.com|linkedin)',
            'pinterest': r'(pinterest\.com|pinterest)'
        }
        
        # Find all links
        links = self.soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '').lower()
            
            for social, pattern in social_patterns.items():
                if re.search(pattern, href):
                    # Extract username from URL if possible
                    username = self._extract_social_username(social, href)
                    setattr(socials, social, username or href)
        
        return socials
    
    def _extract_social_username(self, platform: str, url: str) -> Optional[str]:
        """Extract username from social media URL"""
        patterns = {
            'instagram': r'instagram\.com/([\w\._]+)',
            'facebook': r'facebook\.com/([\w\.]+)',
            'tiktok': r'tiktok\.com/@?([\w\.]+)',
            'twitter': r'(twitter|x)\.com/([\w]+)',
            'youtube': r'youtube\.com/(user|channel)/([\w]+)',
            'linkedin': r'linkedin\.com/(company|in)/([\w\-]+)',
            'pinterest': r'pinterest\.com/([\w]+)'
        }
        
        if platform in patterns:
            match = re.search(patterns[platform], url)
            if match:
                # For Twitter/X, use the second group
                if platform == 'twitter' and match.group(2):
                    return '@' + match.group(2)
                # For YouTube, use the second group
                elif platform == 'youtube' and match.group(2):
                    return match.group(2)
                # For others, use the first group
                elif match.group(1):
                    return '@' + match.group(1)
        
        return None
    
    async def _fetch_contact_info(self) -> Contact:
        """Fetch contact information (emails and phone numbers)"""
        if not self.soup:
            content, _ = await self._fetch_url(self.base_url)
            self.soup = BeautifulSoup(content, 'html.parser')
        
        contact = Contact()
        
        # Try to fetch contact page
        contact_paths = ['/contact', '/pages/contact', '/pages/contact-us']
        contact_soup = None
        
        for path in contact_paths:
            try:
                content, status = await self._fetch_url(urljoin(self.base_url, path))
                
                if status == 200:
                    contact_soup = BeautifulSoup(content, 'html.parser')
                    break
            except Exception:
                continue
        
        # If contact page not found, use main page
        if not contact_soup:
            contact_soup = self.soup
        
        # Extract emails
        email_pattern = r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'
        emails = set()
        
        # Look in text
        text = contact_soup.get_text()
        found_emails = re.findall(email_pattern, text)
        emails.update(found_emails)
        
        # Look in mailto links
        mailto_links = contact_soup.find_all('a', href=re.compile(r'mailto:'))
        for link in mailto_links:
            href = link.get('href', '')
            email = href.replace('mailto:', '').split('?')[0].strip()
            if re.match(email_pattern, email):
                emails.add(email)
        
        # Extract phone numbers
        phone_pattern = r'\+?[\d\s\(\)\-]{10,20}'
        phones = set()
        
        # Look in text
        found_phones = re.findall(phone_pattern, text)
        for phone in found_phones:
            # Clean up phone number
            clean_phone = re.sub(r'[\s\(\)\-]+', '', phone)
            if len(clean_phone) >= 10:
                phones.add(phone.strip())
        
        # Look in tel links
        tel_links = contact_soup.find_all('a', href=re.compile(r'tel:'))
        for link in tel_links:
            href = link.get('href', '')
            phone = href.replace('tel:', '').strip()
            phones.add(phone)
        
        contact.emails = list(emails)
        contact.phones = list(phones)
        
        return contact
    
    async def _fetch_about(self) -> Optional[str]:
        """Fetch about the brand information"""
        about_text = None
        
        # Common about page paths
        about_paths = ['/about', '/pages/about', '/pages/about-us', '/pages/our-story', '/pages/story']
        
        for path in about_paths:
            try:
                content, status = await self._fetch_url(urljoin(self.base_url, path))
                
                if status == 200:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for main content
                    main_content = soup.find('main')
                    if not main_content:
                        main_content = soup.find('div', {'class': re.compile(r'(content|main|page).*')})
                    
                    if main_content:
                        # Extract text and clean it up
                        about_text = main_content.get_text(separator='\n', strip=True)
                        
                        # Break the loop once we found about text
                        break
            except Exception:
                # Continue to next path if this one fails
                continue
        
        return about_text
    
    async def _fetch_important_links(self) -> Links:
        """Fetch important links"""
        if not self.soup:
            content, _ = await self._fetch_url(self.base_url)
            self.soup = BeautifulSoup(content, 'html.parser')
        
        links = Links()
        
        # Define patterns for important links
        link_patterns = {
            'order_tracking': r'(order.?tracking|track.?order|track.?package)',
            'contact_us': r'(contact|contact.?us)',
            'blogs': r'(blog|news|articles)',
            'shipping': r'(shipping|delivery)',
            'careers': r'(careers|jobs|join.?us|work.?with.?us)'
        }
        
        # Find all links
        all_links = self.soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            for link_type, pattern in link_patterns.items():
                if re.search(pattern, href) or re.search(pattern, text):
                    full_url = urljoin(self.base_url, href)
                    setattr(links, link_type, full_url)
        
        return links
    
    async def get_brand_context(self) -> BrandContext:
        """Get brand context from Shopify website"""
        try:
            # Check if the website is a Shopify store
            is_shopify = await self._check_is_shopify()
            
            if not is_shopify:
                raise InvalidShopifyStoreError()
            
            # Extract domain name for brand
            parsed_url = urlparse(self.base_url)
            brand = parsed_url.netloc
            
            # Fetch all data concurrently
            products = await self._fetch_products()
            hero_products = await self._fetch_hero_products(products)
            policies = await self._fetch_policies()
            faqs = await self._fetch_faqs()
            socials = await self._fetch_social_handles()
            contact = await self._fetch_contact_info()
            about = await self._fetch_about()
            links = await self._fetch_important_links()
            
            # Create brand context
            brand_context = BrandContext(
                brand=brand,
                products=products,
                hero_products=hero_products,
                policies=policies,
                faqs=faqs,
                socials=socials,
                contact=contact,
                about=about,
                links=links
            )
            
            return brand_context
        finally:
            # Ensure session is closed
            await self._close_session()