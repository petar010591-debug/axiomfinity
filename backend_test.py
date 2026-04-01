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
        """Test market ticker API"""
        self.log("=== TESTING MARKET TICKER ===")
        success, response = self.run_test(
            "Market Ticker",
            "GET",
            "market/ticker",
            200
        )
        if success:
            tickers = response.get('tickers', [])
            self.log(f"✅ Market ticker returned {len(tickers)} tickers")
            if tickers:
                self.log(f"Sample ticker: {tickers[0].get('symbol', 'N/A')} - ${tickers[0].get('price', 'N/A')}")
        return success

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
        
        return success and success2

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
        """Test admin stats API"""
        self.log("=== TESTING ADMIN STATS ===")
        success, response = self.run_test(
            "Admin Stats",
            "GET",
            "admin/stats",
            200
        )
        if success:
            stats = response
            self.log(f"✅ Admin stats: {stats.get('total_articles', 0)} articles, {stats.get('categories', 0)} categories")
        return success

    def test_admin_articles_crud(self):
        """Test admin articles CRUD operations"""
        self.log("=== TESTING ADMIN ARTICLES CRUD ===")
        
        # List articles
        success1, response1 = self.run_test(
            "Admin List Articles",
            "GET",
            "admin/articles",
            200
        )
        
        # Create article
        article_data = {
            "title": "Test Article " + datetime.now().strftime("%H%M%S"),
            "excerpt": "Test excerpt for automated testing",
            "content": "<p>This is a test article created by automated testing.</p>",
            "status": "draft",
            "tags": ["test", "automation"]
        }
        
        success2, response2 = self.run_test(
            "Admin Create Article",
            "POST",
            "admin/articles",
            201,
            data=article_data
        )
        
        article_id = None
        if success2:
            article_id = response2.get('id')
            self.log(f"✅ Created article with ID: {article_id}")
        
        # Get specific article
        success3 = True
        if article_id:
            success3, response3 = self.run_test(
                "Admin Get Article",
                "GET",
                f"admin/articles/{article_id}",
                200
            )
        
        # Update article
        success4 = True
        if article_id:
            update_data = article_data.copy()
            update_data["title"] = "Updated " + update_data["title"]
            success4, response4 = self.run_test(
                "Admin Update Article",
                "PUT",
                f"admin/articles/{article_id}",
                200,
                data=update_data
            )
        
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