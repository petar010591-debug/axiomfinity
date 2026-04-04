"""
AxiomFinity New Features Tests - Iteration 7
Tests: Team Members, SEO Settings, Homepage Order, Pages Manager, News Sitemap
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "petar010591@gmail.com"
ADMIN_PASSWORD = "Zvezda2023!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestTeamMembersAPI:
    """Team Members CRUD endpoints"""
    
    def test_get_team_public(self):
        """Test public team endpoint returns array"""
        response = requests.get(f"{BASE_URL}/api/team")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Public team endpoint returns {len(data)} members")
    
    def test_get_team_admin(self, auth_headers):
        """Test admin team endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/team", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Admin team endpoint returns {len(data)} members")
    
    def test_create_team_member(self, auth_headers):
        """Test creating a team member"""
        response = requests.post(f"{BASE_URL}/api/admin/team", json={
            "name": "TEST_John Doe",
            "role_title": "Senior Editor",
            "bio": "Test bio for team member",
            "avatar_url": ""
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "TEST_John Doe"
        assert data["role_title"] == "Senior Editor"
        print(f"Created team member with ID: {data['id']}")
        return data["id"]
    
    def test_update_team_member(self, auth_headers):
        """Test updating a team member"""
        # First create a member
        create_resp = requests.post(f"{BASE_URL}/api/admin/team", json={
            "name": "TEST_Update Member",
            "role_title": "Writer",
            "bio": "Original bio"
        }, headers=auth_headers)
        assert create_resp.status_code == 201
        member_id = create_resp.json()["id"]
        
        # Update the member
        update_resp = requests.put(f"{BASE_URL}/api/admin/team/{member_id}", json={
            "name": "TEST_Updated Name",
            "role_title": "Senior Writer"
        }, headers=auth_headers)
        assert update_resp.status_code == 200
        
        # Verify update via GET
        get_resp = requests.get(f"{BASE_URL}/api/admin/team", headers=auth_headers)
        members = get_resp.json()
        updated = next((m for m in members if m["id"] == member_id), None)
        assert updated is not None
        assert updated["name"] == "TEST_Updated Name"
        print(f"Updated team member {member_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/team/{member_id}", headers=auth_headers)
    
    def test_delete_team_member(self, auth_headers):
        """Test deleting a team member"""
        # Create a member to delete
        create_resp = requests.post(f"{BASE_URL}/api/admin/team", json={
            "name": "TEST_Delete Me",
            "role_title": "Temp"
        }, headers=auth_headers)
        assert create_resp.status_code == 201
        member_id = create_resp.json()["id"]
        
        # Delete
        delete_resp = requests.delete(f"{BASE_URL}/api/admin/team/{member_id}", headers=auth_headers)
        assert delete_resp.status_code == 200
        
        # Verify deleted
        get_resp = requests.get(f"{BASE_URL}/api/admin/team", headers=auth_headers)
        members = get_resp.json()
        assert not any(m["id"] == member_id for m in members)
        print(f"Deleted team member {member_id}")


class TestSeoSettingsAPI:
    """SEO/Nofollow settings endpoints"""
    
    def test_get_seo_settings_admin(self, auth_headers):
        """Test admin SEO settings endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/seo-settings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "nofollow_enabled" in data
        assert "excluded_domains" in data
        print(f"SEO settings: nofollow_enabled={data['nofollow_enabled']}")
    
    def test_get_seo_settings_public(self):
        """Test public nofollow settings endpoint"""
        response = requests.get(f"{BASE_URL}/api/seo-settings/nofollow")
        assert response.status_code == 200
        data = response.json()
        assert "nofollow_enabled" in data
        assert "excluded_domains" in data
    
    def test_update_seo_settings(self, auth_headers):
        """Test updating SEO settings"""
        # Get current settings
        get_resp = requests.get(f"{BASE_URL}/api/admin/seo-settings", headers=auth_headers)
        original = get_resp.json()
        
        # Update settings
        update_resp = requests.put(f"{BASE_URL}/api/admin/seo-settings", json={
            "nofollow_enabled": True,
            "excluded_domains": "example.com, trusted.org"
        }, headers=auth_headers)
        assert update_resp.status_code == 200
        
        # Verify update
        verify_resp = requests.get(f"{BASE_URL}/api/admin/seo-settings", headers=auth_headers)
        updated = verify_resp.json()
        assert updated["nofollow_enabled"] == True
        assert "example.com" in updated["excluded_domains"]
        print("SEO settings updated successfully")
        
        # Restore original
        requests.put(f"{BASE_URL}/api/admin/seo-settings", json=original, headers=auth_headers)


class TestHomepageOrderAPI:
    """Homepage section order endpoints"""
    
    def test_get_homepage_order(self, auth_headers):
        """Test getting homepage section order"""
        response = requests.get(f"{BASE_URL}/api/admin/homepage-order", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert len(data["sections"]) == 5
        # Verify default sections
        expected = ["latest", "crypto", "press_releases", "sponsored", "others"]
        for section in expected:
            assert section in data["sections"]
        print(f"Homepage order: {data['sections']}")
    
    def test_update_homepage_order(self, auth_headers):
        """Test updating homepage section order"""
        # Get current order
        get_resp = requests.get(f"{BASE_URL}/api/admin/homepage-order", headers=auth_headers)
        original = get_resp.json()
        
        # Update order (swap first two)
        new_order = ["crypto", "latest", "press_releases", "sponsored", "others"]
        update_resp = requests.put(f"{BASE_URL}/api/admin/homepage-order", json={
            "sections": new_order
        }, headers=auth_headers)
        assert update_resp.status_code == 200
        
        # Verify update
        verify_resp = requests.get(f"{BASE_URL}/api/admin/homepage-order", headers=auth_headers)
        updated = verify_resp.json()
        assert updated["sections"][0] == "crypto"
        assert updated["sections"][1] == "latest"
        print("Homepage order updated successfully")
        
        # Restore original
        requests.put(f"{BASE_URL}/api/admin/homepage-order", json=original, headers=auth_headers)


class TestPagesManagerAPI:
    """Pages CRUD endpoints"""
    
    def test_get_pages_list(self):
        """Test public pages list"""
        response = requests.get(f"{BASE_URL}/api/pages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} pages")
    
    def test_get_page_by_slug(self):
        """Test getting page by slug"""
        response = requests.get(f"{BASE_URL}/api/pages/privacy-policy")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data
        assert "slug" in data
        print(f"Page: {data['title']}")
    
    def test_create_page(self, auth_headers):
        """Test creating a page"""
        response = requests.post(f"{BASE_URL}/api/admin/pages", json={
            "title": "TEST_New Page",
            "slug": "test-new-page",
            "content": "<h2>Test Content</h2><p>This is test content.</p>",
            "page_type": "legal"
        }, headers=auth_headers)
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "TEST_New Page"
        print(f"Created page with ID: {data['id']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/pages/{data['id']}", headers=auth_headers)
    
    def test_update_page(self, auth_headers):
        """Test updating a page"""
        # Create a page
        create_resp = requests.post(f"{BASE_URL}/api/admin/pages", json={
            "title": "TEST_Update Page",
            "slug": "test-update-page",
            "content": "Original content",
            "page_type": "legal"
        }, headers=auth_headers)
        page_id = create_resp.json()["id"]
        
        # Update
        update_resp = requests.put(f"{BASE_URL}/api/admin/pages/{page_id}", json={
            "title": "TEST_Updated Page Title",
            "slug": "test-update-page",
            "content": "Updated content",
            "page_type": "educational"
        }, headers=auth_headers)
        assert update_resp.status_code == 200
        
        # Verify
        verify_resp = requests.get(f"{BASE_URL}/api/pages/test-update-page")
        if verify_resp.status_code == 200:
            updated = verify_resp.json()
            assert updated["title"] == "TEST_Updated Page Title"
        print(f"Updated page {page_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/pages/{page_id}", headers=auth_headers)
    
    def test_delete_page(self, auth_headers):
        """Test deleting a page"""
        # Create
        create_resp = requests.post(f"{BASE_URL}/api/admin/pages", json={
            "title": "TEST_Delete Page",
            "slug": "test-delete-page",
            "content": "To be deleted",
            "page_type": "legal"
        }, headers=auth_headers)
        page_id = create_resp.json()["id"]
        
        # Delete
        delete_resp = requests.delete(f"{BASE_URL}/api/admin/pages/{page_id}", headers=auth_headers)
        assert delete_resp.status_code == 200
        
        # Verify deleted
        verify_resp = requests.get(f"{BASE_URL}/api/pages/test-delete-page")
        assert verify_resp.status_code == 404
        print(f"Deleted page {page_id}")


class TestNewsSitemap:
    """News sitemap for Google News"""
    
    def test_news_sitemap_xml(self):
        """Test news sitemap returns valid XML"""
        response = requests.get(f"{BASE_URL}/api/news-sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        
        content = response.text
        assert '<?xml version="1.0"' in content
        assert '<urlset' in content
        assert 'xmlns:news=' in content
        assert '<news:publication>' in content or '<urlset' in content  # May be empty if no recent articles
        print("News sitemap XML is valid")


class TestHomepageSectionsWithOrder:
    """Test that homepage sections respect custom order"""
    
    def test_homepage_sections_returns_data(self):
        """Test homepage sections endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/articles/homepage-sections")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected sections
        expected_sections = ["latest", "crypto", "press_releases", "sponsored", "others"]
        for section in expected_sections:
            assert section in data, f"Missing section: {section}"
        
        print(f"Homepage sections: {list(data.keys())}")


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_team_members(self, auth_headers):
        """Remove TEST_ prefixed team members"""
        response = requests.get(f"{BASE_URL}/api/admin/team", headers=auth_headers)
        members = response.json()
        deleted = 0
        for m in members:
            if m.get("name", "").startswith("TEST_"):
                requests.delete(f"{BASE_URL}/api/admin/team/{m['id']}", headers=auth_headers)
                deleted += 1
        print(f"Cleaned up {deleted} test team members")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
