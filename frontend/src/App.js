import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { AuthProvider } from "./contexts/AuthContext";
import Header from "./components/Header";
import Footer from "./components/Footer";
import TickerStrip from "./components/TickerStrip";
import HomePage from "./pages/HomePage";
import ArticlePage from "./pages/ArticlePage";
import LatestNewsPage from "./pages/LatestNewsPage";
import EducationPage from "./pages/EducationPage";
import EducationArticle from "./pages/EducationArticle";
import TagPage from "./pages/TagPage";
import AboutPage, { ContactPage } from "./pages/AboutPage";
import SearchPage from "./pages/SearchPage";
import LegalPage from "./pages/LegalPage";
import AuthorProfile from "./pages/AuthorProfile";
import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/admin/AdminDashboard";
import ArticlesList from "./pages/admin/ArticlesList";
import ArticleEditor from "./pages/admin/ArticleEditor";
import CategoriesManager from "./pages/admin/CategoriesManager";
import HomepageCuration from "./pages/admin/HomepageCuration";
import UsersManager from "./pages/admin/UsersManager";
import AdminProfile from "./pages/admin/AdminProfile";
import PagesManager from "./pages/admin/PagesManager";
import EducationHubManager from "./pages/admin/EducationHubManager";
import SidebarManager from "./pages/admin/SidebarManager";
import LatestPageManager from "./pages/admin/LatestPageManager";
import TeamManager from "./pages/admin/TeamManager";
import SeoSettings from "./pages/admin/SeoSettings";
import HomepageOrder from "./pages/admin/HomepageOrder";

function Layout({ children }) {
  const location = useLocation();
  const isAdmin = location.pathname.startsWith('/admin');

  if (isAdmin) return <>{children}</>;

  return (
    <>
      <Header />
      <div className="pt-16">
        <TickerStrip />
        <main className="min-h-screen">
          {children}
        </main>
      </div>
      <Footer />
    </>
  );
}

function App() {
  return (
    <HelmetProvider>
      <AuthProvider>
        <BrowserRouter>
          <Layout>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/latest" element={<LatestNewsPage />} />
              <Route path="/category/:slug" element={<LatestNewsPage />} />
              <Route path="/crypto" element={<LatestNewsPage />} />
              <Route path="/markets" element={<LatestNewsPage />} />
              <Route path="/defi" element={<LatestNewsPage />} />
              <Route path="/analysis" element={<LatestNewsPage />} />
              <Route path="/educational" element={<LatestNewsPage />} />
              <Route path="/sponsored" element={<LatestNewsPage />} />
              <Route path="/press-releases" element={<LatestNewsPage />} />
              <Route path="/education" element={<EducationPage />} />
              <Route path="/education/:slug" element={<EducationArticle />} />
              <Route path="/tag/:slug" element={<TagPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/page/:slug" element={<LegalPage />} />
              <Route path="/author/:authorSlug" element={<AuthorProfile />} />
              <Route path="/:category/:slug" element={<ArticlePage />} />

              {/* Admin Routes */}
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin" element={<AdminDashboard />}>
                <Route path="articles" element={<ArticlesList />} />
                <Route path="articles/new" element={<ArticleEditor />} />
                <Route path="articles/edit/:id" element={<ArticleEditor />} />
                <Route path="categories" element={<CategoriesManager />} />
                <Route path="pages" element={<PagesManager />} />
                <Route path="education" element={<EducationHubManager />} />
                <Route path="trending" element={<SidebarManager />} />
                <Route path="latest-page" element={<LatestPageManager />} />
                <Route path="homepage" element={<HomepageCuration />} />
                <Route path="homepage/order" element={<HomepageOrder />} />
                <Route path="team" element={<TeamManager />} />
                <Route path="users" element={<UsersManager />} />
                <Route path="seo" element={<SeoSettings />} />
                <Route path="profile" element={<AdminProfile />} />
              </Route>
            </Routes>
          </Layout>
        </BrowserRouter>
      </AuthProvider>
    </HelmetProvider>
  );
}

export default App;
