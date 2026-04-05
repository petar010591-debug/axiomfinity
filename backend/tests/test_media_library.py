"""
Test Media Library API endpoints for AxiomFinity CMS
Tests: GET /api/media, POST /api/media/sync-cloudinary
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://article-stream-8.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "petar010591@gmail.com"
ADMIN_PASSWORD = "Zvezda2023!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "token" in data, "No token in login response"
    return data["token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestMediaLibraryAPI:
    """Tests for Media Library endpoints"""
    
    def test_get_media_list_authenticated(self, auth_headers):
        """GET /api/media - should return list of media items"""
        response = requests.get(f"{BASE_URL}/api/media", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "items" in data, "Response should have 'items' key"
        assert "total" in data, "Response should have 'total' key"
        assert "pages" in data, "Response should have 'pages' key"
        
        # Verify items structure
        if data["items"]:
            item = data["items"][0]
            assert "url" in item, "Media item should have 'url'"
            assert "filename" in item, "Media item should have 'filename'"
        
        print(f"Media library has {data['total']} items across {data['pages']} pages")
        return data
    
    def test_get_media_list_unauthenticated(self):
        """GET /api/media without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/media")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_get_media_with_search(self, auth_headers):
        """GET /api/media?q=test - should filter by filename"""
        response = requests.get(f"{BASE_URL}/api/media", headers=auth_headers, params={"q": "test"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "items" in data
        print(f"Search 'test' returned {len(data['items'])} items")
    
    def test_get_media_pagination(self, auth_headers):
        """GET /api/media with pagination params"""
        response = requests.get(f"{BASE_URL}/api/media", headers=auth_headers, params={"page": 1, "limit": 5})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) <= 5, "Should respect limit parameter"
        print(f"Page 1 with limit 5: {len(data['items'])} items")


class TestAdminArticlesAPI:
    """Tests for Admin Articles endpoints - verify date format in response"""
    
    def test_get_admin_articles(self, auth_headers):
        """GET /api/admin/articles - verify articles have timestamps"""
        response = requests.get(f"{BASE_URL}/api/admin/articles", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "articles" in data
        
        if data["articles"]:
            article = data["articles"][0]
            # Verify timestamp fields exist
            assert "created_at" in article, "Article should have created_at"
            print(f"First article: {article['title']}")
            print(f"  created_at: {article.get('created_at')}")
            print(f"  published_at: {article.get('published_at')}")
    
    def test_get_single_article(self, auth_headers):
        """GET /api/admin/articles/:id - get single article for editing"""
        # First get list to get an ID
        list_response = requests.get(f"{BASE_URL}/api/admin/articles", headers=auth_headers)
        assert list_response.status_code == 200
        
        articles = list_response.json().get("articles", [])
        if not articles:
            pytest.skip("No articles to test")
        
        article_id = articles[0]["id"]
        response = requests.get(f"{BASE_URL}/api/admin/articles/{article_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "title" in data
        assert "content" in data
        print(f"Retrieved article: {data['title']}")


class TestAuthAPI:
    """Tests for authentication endpoints"""
    
    def test_login_success(self):
        """POST /api/auth/login - successful login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert "email" in data
        assert data["email"] == ADMIN_EMAIL.lower()
        print(f"Login successful for {data['email']} with role {data.get('role')}")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_get_me_authenticated(self, auth_headers):
        """GET /api/auth/me - get current user"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert data["email"] == ADMIN_EMAIL.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
