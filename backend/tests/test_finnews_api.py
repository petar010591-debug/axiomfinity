"""
FinNews API Tests - Comprehensive backend testing
Tests: Authentication, Articles, Categories, Homepage sections, Sitemap, Author profiles
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "petar010591@gmail.com"
ADMIN_PASSWORD = "Zvezda2023!"


class TestHealthAndBasicEndpoints:
    """Basic API health and public endpoints"""
    
    def test_market_ticker(self):
        """Test market ticker endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/market/ticker")
        assert response.status_code == 200
        data = response.json()
        assert "tickers" in data
        assert len(data["tickers"]) > 0
        # Verify ticker structure
        ticker = data["tickers"][0]
        assert "symbol" in ticker
        assert "price" in ticker
    
    def test_categories_list(self):
        """Test categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 7  # Expected 7 categories
        # Verify category structure
        cat = data[0]
        assert "id" in cat
        assert "name" in cat
        assert "slug" in cat
    
    def test_tags_list(self):
        """Test tags endpoint"""
        response = requests.get(f"{BASE_URL}/api/tags")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestArticleEndpoints:
    """Article CRUD and public article endpoints"""
    
    def test_articles_list(self):
        """Test articles list endpoint"""
        response = requests.get(f"{BASE_URL}/api/articles?page=1&limit=12")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert "total" in data
        assert "page" in data
        assert len(data["articles"]) > 0
    
    def test_article_by_slug(self):
        """Test get article by slug - CRITICAL: This was the P0 bug"""
        response = requests.get(f"{BASE_URL}/api/articles/by-slug/bitcoin-surges-past-100k-institutional-demand")
        assert response.status_code == 200
        data = response.json()
        
        # Verify article structure
        assert "id" in data
        assert "title" in data
        assert data["title"] == "Bitcoin Surges Past $100K as Institutional Demand Hits New Highs"
        assert "content" in data
        assert len(data["content"]) > 0
        assert "slug" in data
        assert "author_name" in data
        assert "author_id" in data
        
        # Verify OG fields (important for SEO)
        assert "og_title" in data
        assert "og_description" in data
        assert "og_image" in data
        
        # Verify related articles
        assert "related" in data
        assert isinstance(data["related"], list)
    
    def test_article_not_found(self):
        """Test 404 for non-existent article"""
        response = requests.get(f"{BASE_URL}/api/articles/by-slug/non-existent-article-slug-12345")
        assert response.status_code == 404
    
    def test_homepage_sections(self):
        """Test homepage sections endpoint"""
        response = requests.get(f"{BASE_URL}/api/articles/homepage-sections")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all sections present
        assert "latest" in data
        assert "crypto" in data
        assert "press_releases" in data
        assert "sponsored" in data
        assert "others" in data
        
        # Verify latest has articles
        assert len(data["latest"]) > 0
    
    def test_featured_articles(self):
        """Test featured articles endpoint"""
        response = requests.get(f"{BASE_URL}/api/articles/featured")
        assert response.status_code == 200
        data = response.json()
        assert "hero_primary" in data
        assert "hero_secondary" in data
    
    def test_article_search(self):
        """Test article search"""
        response = requests.get(f"{BASE_URL}/api/articles/search?q=bitcoin")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert "total" in data
    
    def test_articles_by_category(self):
        """Test filtering articles by category"""
        response = requests.get(f"{BASE_URL}/api/articles?category=crypto")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data


class TestAuthEndpoints:
    """Authentication endpoints"""
    
    def test_login_success(self):
        """Test successful admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "id" in data
        assert "email" in data
        assert data["email"] == ADMIN_EMAIL.lower()
        assert "role" in data
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_invalid_email(self):
        """Test login with non-existent email"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })
        assert response.status_code == 401
    
    def test_me_without_auth(self):
        """Test /me endpoint without authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401


class TestAuthorProfile:
    """Author profile endpoints"""
    
    def test_author_profile(self):
        """Test author profile endpoint"""
        # First get an article to find author_id
        article_resp = requests.get(f"{BASE_URL}/api/articles/by-slug/bitcoin-surges-past-100k-institutional-demand")
        assert article_resp.status_code == 200
        author_id = article_resp.json().get("author_id")
        
        if author_id:
            response = requests.get(f"{BASE_URL}/api/authors/{author_id}")
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "articles" in data
            assert isinstance(data["articles"], list)
    
    def test_author_not_found(self):
        """Test 404 for non-existent author"""
        response = requests.get(f"{BASE_URL}/api/authors/000000000000000000000000")
        assert response.status_code == 404


class TestSitemap:
    """XML Sitemap endpoint"""
    
    def test_sitemap_xml(self):
        """Test sitemap returns valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        
        content = response.text
        assert '<?xml version="1.0"' in content
        assert '<urlset' in content
        assert '<url>' in content
        assert '<loc>' in content


class TestPages:
    """Static pages endpoints"""
    
    def test_pages_list(self):
        """Test pages list"""
        response = requests.get(f"{BASE_URL}/api/pages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_page_by_slug(self):
        """Test get page by slug"""
        response = requests.get(f"{BASE_URL}/api/pages/about")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data
    
    def test_educational_pages(self):
        """Test educational pages filter"""
        response = requests.get(f"{BASE_URL}/api/pages?page_type=educational")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestContact:
    """Contact form endpoint"""
    
    def test_contact_submission(self):
        """Test contact form submission"""
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAdminEndpoints:
    """Admin endpoints (require authentication)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed")
    
    def test_admin_articles_list(self, auth_token):
        """Test admin articles list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/articles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert "total" in data
    
    def test_admin_stats(self, auth_token):
        """Test admin dashboard stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_articles" in data
        assert "published" in data
        assert "categories" in data
    
    def test_admin_users_list(self, auth_token):
        """Test admin users list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_admin_homepage_config(self, auth_token):
        """Test admin homepage configuration"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/homepage", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "hero_primary" in data or data == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
