import os
import requests
import time
from retrying import retry
from dotenv import load_dotenv
from src.core.logger import logger

load_dotenv()

class WikiAPIClient:
    """
    Staff-level OSRS Wiki API Client.
    Features:
    - User-Agent injection
    - Retry logic with exponential backoff
    - Rate limit awareness
    - Session management
    """
    
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout
        self.user_agent = os.getenv("OSRS_USER_AGENT")
        
        if not self.user_agent:
            logger.error("MANDATORY OSRS_USER_AGENT is not set in .env")
            raise ValueError("MANDATORY OSRS_USER_AGENT is not set in .env")
        
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip"  # Recommended by Wiki API for bandwidth
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        logger.debug(f"WikiAPIClient Initialized with Base URL: {base_url}")

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def fetch(self, endpoint: str) -> dict:
        """
        Generic fetch method with retry logic.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Fetching from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            
            # Handle rate limits (429) explicitly before raise_for_status
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                logger.warning(f"Rate limited (429). Sleeping for {retry_after}s")
                time.sleep(retry_after)
                raise requests.exceptions.RequestException("Rate Limit Hit")

            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e.response.status_code} for URL: {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            raise

    def close(self):
        self.session.close()
