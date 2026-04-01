#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class FinancialNewsAPITester:
    def __init__(self, base_url="https://article-stream-8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "PASS")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "FAIL")
                self.log(f"Response: {response.text[:200]}", "DEBUG")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}", "FAIL")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login and get token"""
        self.log("=== TESTING ADMIN AUTHENTICATION ===")
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "petar010591@gmail.com", "password": "Zvezda2023!"}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.log(f"✅ Admin login successful, token acquired")
            return True
        return False

    def test_auth_me(self):
        """Test /auth/me endpoint"""
        success, response = self.run_test(
            "Get Current User",
            "GET", 
            "auth/me",
            200
        )
        if success:
            self.log(f"✅ User info: {response.get('email', 'N/A')} - {response.get('role', 'N/A')}")
        return success

    def test_market_ticker(self):
        """Test market ticker API with caching"""
        self.log("=== TESTING MARKET TICKER (with 2-min cache) ===")
        
        # First call
        import time
        start_time = time.time()
        success, response = self.run_test(
            "Market Ticker (First Call)",
            "GET",
            "market/ticker",
            200
        )
        first_call_time = time.time() - start_time
        
        if success:
            tickers = response.get('tickers', [])
            self.log(f"✅ Market ticker returned {len(tickers)} tickers (took {first_call_time:.2f}s)")
            if tickers:
                self.log(f"Sample ticker: {tickers[0].get('symbol', 'N/A')} - ${tickers[0].get('price', 'N/A')}")
        
        # Second call (should be faster due to cache)
        start_time = time.time()
        success2, response2 = self.run_test(
            "Market Ticker (Second Call - Cached)",
            "GET",
            "market/ticker",
            200
        )
        second_call_time = time.time() - start_time
        
        if success2:
            self.log(f"✅ Cached call took {second_call_time:.2f}s (should be faster than {first_call_time:.2f}s)")
            if second_call_time < first_call_time:
                self.log("✅ Cache is working - second call was faster")
            else:
                self.log("⚠️  Cache may not be working - second call was not faster")
        
        return success and success2

    def test_categories_api(self):
        """Test categories API"""
        self.log("=== TESTING CATEGORIES ===")
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "categories",
            200
        )
        if success:
            categories = response if isinstance(response, list) else []
            self.log(f"✅ Categories API returned {len(categories)} categories")
            if categories:
                self.log(f"Sample category: {categories[0].get('name', 'N/A')}")
                # Check for expected 7 categories
                expected_categories = ["Crypto", "Markets", "DeFi", "Analysis", "Educational", "Sponsored", "Press Releases"]
                category_names = [cat.get('name', '') for cat in categories]
                found_expected = [name for name in expected_categories if name in category_names]
                self.log(f"✅ Found {len(found_expected)}/7 expected categories: {', '.join(found_expected)}")
        return success

    def test_articles_api(self):
        """Test articles API"""
        self.log("=== TESTING ARTICLES ===")
        
        # Test get articles
        success, response = self.run_test(
            "Get Articles",
            "GET",
            "articles",
            200
        )
        if success:
            articles = response.get('articles', [])
            self.log(f"✅ Articles API returned {len(articles)} articles")
        
        # Test featured articles
        success2, response2 = self.run_test(
            "Get Featured Articles",
            "GET",
            "articles/featured",
            200
        )
        if success2:
            hero_primary = response2.get('hero_primary')
            hero_secondary = response2.get('hero_secondary', [])
            self.log(f"✅ Featured articles: 1 primary, {len(hero_secondary)} secondary")
        
        # Test NEW homepage sections endpoint
        success3, response3 = self.run_test(
            "Get Homepage Sections",
            "GET",
            "articles/homepage-sections",
            200
        )
        if success3:
            sections = response3
            latest = sections.get('latest', [])
            crypto = sections.get('crypto', [])
            press_releases = sections.get('press_releases', [])
            sponsored = sections.get('sponsored', [])
            others = sections.get('others', [])
            self.log(f"✅ Homepage sections: {len(latest)} latest, {len(crypto)} crypto, {len(press_releases)} press releases, {len(sponsored)} sponsored, {len(others)} others")
        
        return success and success2 and success3

    def test_article_search(self):
        """Test article search API"""
        self.log("=== TESTING ARTICLE SEARCH ===")
        success, response = self.run_test(
            "Search Articles (bitcoin)",
            "GET",
            "articles/search?q=bitcoin",
            200
        )
        if success:
            articles = response.get('articles', [])
            total = response.get('total', 0)
            self.log(f"✅ Search returned {len(articles)} articles (total: {total})")
        return success

    def test_admin_stats(self):
        """Test admin stats API with V3 features"""
        self.log("=== TESTING ADMIN STATS (V3) ===")
        success, response = self.run_test(
            "Admin Stats",
            "GET",
            "admin/stats",
            200
        )
        if success:
            stats = response
            self.log(f"✅ Admin stats: {stats.get('total_articles', 0)} articles, {stats.get('categories', 0)} categories")
            self.log(f"✅ V3 stats: {stats.get('scheduled', 0)} scheduled, {stats.get('users', 0)} users")
        return success

    def test_admin_articles_crud(self):
        """Test admin articles CRUD operations with multi-category support"""
        self.log("=== TESTING ADMIN ARTICLES CRUD (with multi-category) ===")
        
        # List articles
        success1, response1 = self.run_test(
            "Admin List Articles",
            "GET",
            "admin/articles",
            200
        )
        
        # Get categories for testing multi-category
        categories_success, categories_response = self.run_test(
            "Get Categories for Multi-Category Test",
            "GET",
            "categories",
            200
        )
        
        category_id = None
        secondary_categories = []
        if categories_success and categories_response:
            categories = categories_response if isinstance(categories_response, list) else []
            if len(categories) >= 2:
                category_id = categories[0].get('id')
                secondary_categories = [categories[1].get('slug', '')]
        
        # Create article with multi-category support and scheduling
        article_data = {
            "title": "Test Multi-Category Article " + datetime.now().strftime("%H%M%S"),
            "excerpt": "Test excerpt for automated testing with multiple categories",
            "content": "<p>This is a test article created by automated testing with multi-category support.</p>",
            "status": "scheduled",
            "scheduled_at": "2026-12-31T23:59:59Z",
            "tags": ["test", "automation"],
            "category_id": category_id,
            "secondary_categories": secondary_categories,
            "og_image": "https://example.com/test-og.jpg",
            "meta_title": "Test Meta Title",
            "meta_description": "Test meta description"
        }
        
        success2, response2 = self.run_test(
            "Admin Create Article (Multi-Category + Scheduling)",
            "POST",
            "admin/articles",
            201,
            data=article_data
        )
        
        article_id = None
        if success2:
            article_id = response2.get('id')
            categories_field = response2.get('categories', [])
            scheduled_at = response2.get('scheduled_at')
            og_image = response2.get('og_image')
            self.log(f"✅ Created article with ID: {article_id}")
            self.log(f"✅ Article categories: {categories_field}")
            self.log(f"✅ Article scheduled for: {scheduled_at}")
            self.log(f"✅ Article OG image: {og_image}")
        
        # Get specific article and verify multi-category
        success3 = True
        if article_id:
            success3, response3 = self.run_test(
                "Admin Get Article (Verify Multi-Category)",
                "GET",
                f"admin/articles/{article_id}",
                200
            )
            if success3:
                categories_field = response3.get('categories', [])
                self.log(f"✅ Retrieved article categories: {categories_field}")
        
        # Update article with different secondary categories
        success4 = True
        if article_id and len(secondary_categories) > 0:
            update_data = article_data.copy()
            update_data["title"] = "Updated " + update_data["title"]
            update_data["secondary_categories"] = ["sponsored"]  # Change secondary category
            success4, response4 = self.run_test(
                "Admin Update Article (Change Secondary Categories)",
                "PUT",
                f"admin/articles/{article_id}",
                200,
                data=update_data
            )
            if success4:
                updated_categories = response4.get('categories', [])
                self.log(f"✅ Updated article categories: {updated_categories}")
        
        # Delete article
        success5 = True
        if article_id:
            success5, response5 = self.run_test(
                "Admin Delete Article",
                "DELETE",
                f"admin/articles/{article_id}",
                200
            )
        
        return all([success1, success2, success3, success4, success5])

    def test_admin_categories_crud(self):
        """Test admin categories CRUD operations"""
        self.log("=== TESTING ADMIN CATEGORIES CRUD ===")
        
        # Create category
        category_data = {
            "name": "Test Category " + datetime.now().strftime("%H%M%S"),
            "description": "Test category for automated testing"
        }
        
        success1, response1 = self.run_test(
            "Admin Create Category",
            "POST",
            "admin/categories",
            201,
            data=category_data
        )
        
        category_id = None
        if success1:
            category_id = response1.get('id')
            self.log(f"✅ Created category with ID: {category_id}")
        
        # Update category
        success2 = True
        if category_id:
            update_data = {
                "name": "Updated " + category_data["name"],
                "description": category_data["description"]
            }
            success2, response2 = self.run_test(
                "Admin Update Category",
                "PUT",
                f"admin/categories/{category_id}",
                200,
                data=update_data
            )
        
        # Delete category
        success3 = True
        if category_id:
            success3, response3 = self.run_test(
                "Admin Delete Category",
                "DELETE",
                f"admin/categories/{category_id}",
                200
            )
        
        return all([success1, success2, success3])

    def test_admin_homepage_curation(self):
        """Test admin homepage curation"""
        self.log("=== TESTING ADMIN HOMEPAGE CURATION ===")
        
        # Get homepage config
        success1, response1 = self.run_test(
            "Admin Get Homepage Config",
            "GET",
            "admin/homepage",
            200
        )
        
        # Update homepage config (with empty data to avoid breaking existing setup)
        success2, response2 = self.run_test(
            "Admin Update Homepage Config",
            "PUT",
            "admin/homepage",
            200,
            data={"hero_primary": None, "hero_secondary": []}
        )
        
        return success1 and success2

    def test_contact_form(self):
        """Test contact form submission"""
        self.log("=== TESTING CONTACT FORM ===")
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Contact",
            "message": "This is a test message from automated testing."
        }
        
        success, response = self.run_test(
            "Contact Form Submission",
            "POST",
            "contact",
            200,
            data=contact_data
        )
        return success

    def test_pages_api(self):
        """Test pages API"""
        self.log("=== TESTING PAGES ===")
        
        # Get all pages
        success1, response1 = self.run_test(
            "Get All Pages",
            "GET",
            "pages",
            200
        )
        
        # Get educational pages
        success2, response2 = self.run_test(
            "Get Educational Pages",
            "GET",
            "pages?page_type=educational",
            200
        )
        
    def test_v3_features(self):
        """Test V3 specific features: upload, users, author profiles, sitemap"""
        self.log("=== TESTING V3 FEATURES ===")
        
        # Test XML sitemap
        success1, response1 = self.run_test(
            "XML Sitemap",
            "GET",
            "sitemap.xml",
            200
        )
        if success1:
            # Check if response contains XML
            sitemap_content = str(response1) if response1 else ""
            if "urlset" in sitemap_content or "<?xml" in sitemap_content:
                self.log("✅ Sitemap contains XML content")
            else:
                self.log("⚠️  Sitemap may not be valid XML")
        
        # Test user management (requires super_admin)
        success2, response2 = self.run_test(
            "Admin List Users",
            "GET",
            "admin/users",
            200
        )
        if success2:
            users = response2 if isinstance(response2, list) else []
            self.log(f"✅ User management: {len(users)} users found")
        
        # Test create user
        user_data = {
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "TestPass123!",
            "name": "Test User",
            "role": "author",
            "bio": "Test user bio"
        }
        
        success3, response3 = self.run_test(
            "Admin Create User",
            "POST",
            "admin/users",
            201,
            data=user_data
        )
        
        test_user_id = None
        if success3:
            test_user_id = response3.get('id')
            self.log(f"✅ Created test user with ID: {test_user_id}")
        
        # Test author profile endpoint
        success4 = True
        if test_user_id:
            success4, response4 = self.run_test(
                "Get Author Profile",
                "GET",
                f"authors/{test_user_id}",
                200
            )
            if success4:
                author_name = response4.get('name', 'N/A')
                author_articles = response4.get('articles', [])
                self.log(f"✅ Author profile: {author_name}, {len(author_articles)} articles")
        
        # Test admin profile update
        profile_data = {
            "name": "Updated Admin Name",
            "bio": "Updated admin bio for testing",
            "social_twitter": "@testadmin",
            "social_linkedin": "https://linkedin.com/in/testadmin",
            "website": "https://testadmin.com"
        }
        
        success5, response5 = self.run_test(
            "Update Admin Profile",
            "PUT",
            "admin/profile",
            200,
            data=profile_data
        )
        if success5:
            updated_name = response5.get('name', 'N/A')
            self.log(f"✅ Admin profile updated: {updated_name}")
        
        # Test role change (super_admin only)
        success6 = True
        if test_user_id:
            success6, response6 = self.run_test(
                "Change User Role",
                "PUT",
                f"admin/users/{test_user_id}/role?role=editor",
                200
            )
            if success6:
                self.log("✅ User role changed successfully")
        
        # Cleanup: delete test user
        success7 = True
        if test_user_id:
            success7, response7 = self.run_test(
                "Delete Test User",
                "DELETE",
                f"admin/users/{test_user_id}",
                200
            )
            if success7:
                self.log("✅ Test user deleted successfully")
        
        return all([success1, success2, success3, success4, success5, success6, success7])

    def test_upload_endpoint(self):
        """Test file upload endpoint (simulated)"""
        self.log("=== TESTING UPLOAD ENDPOINT ===")
        
        # Note: We can't easily test actual file upload in this script
        # But we can test the endpoint exists and requires auth
        success, response = self.run_test(
            "Upload Endpoint (No File)",
            "POST",
            "upload",
            400  # Should return 400 for missing file
        )
        
        if success or response:  # 400 is expected, so this is actually success
            self.log("✅ Upload endpoint exists and requires proper file data")
            return True
        else:
            self.log("❌ Upload endpoint may not be working")
            return False
        # Get specific page by slug
        success3, response3 = self.run_test(
            "Get Privacy Policy Page",
            "GET",
            "pages/privacy-policy",
            200
        )
        
        return all([success1, success2, success3])

    def test_logout(self):
        """Test logout"""
        self.log("=== TESTING LOGOUT ===")
        success, response = self.run_test(
            "Admin Logout",
            "POST",
            "auth/logout",
            200
        )
        if success:
            self.token = None
        return success

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting Financial News API Tests")
        self.log(f"Testing against: {self.base_url}")
        
        # Authentication tests
        if not self.test_admin_login():
            self.log("❌ Admin login failed - stopping tests", "ERROR")
            return False
        
        self.test_auth_me()
        
        # Public API tests
        self.test_market_ticker()
        self.test_categories_api()
        self.test_articles_api()
        self.test_article_search()
        self.test_pages_api()
        self.test_contact_form()
        
        # Admin API tests (require authentication)
        self.test_admin_stats()
        self.test_admin_articles_crud()
        self.test_admin_categories_crud()
        self.test_admin_homepage_curation()
        
        # V3 specific features
        self.test_v3_features()
        self.test_upload_endpoint()
        
        # Cleanup
        self.test_logout()
        
        return True

    def print_summary(self):
        """Print test summary"""
        self.log("=" * 50)
        self.log("📊 TEST SUMMARY")
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Tests Failed: {self.tests_run - self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                self.log(f"  - {failure}")
        
        self.log("=" * 50)
        return self.tests_passed == self.tests_run

def main():
    tester = FinancialNewsAPITester()
    
    try:
        tester.run_all_tests()
        success = tester.print_summary()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("\n⚠️  Tests interrupted by user", "WARN")
        return 1
    except Exception as e:
        tester.log(f"💥 Unexpected error: {str(e)}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())