import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import Header from "./components/Header";
import Footer from "./components/Footer";
import TickerStrip from "./components/TickerStrip";
import HomePage from "./pages/HomePage";
import ArticlePage from "./pages/ArticlePage";
import LatestNewsPage from "./pages/LatestNewsPage";
import EducationPage from "./pages/EducationPage";
import AboutPage, { ContactPage } from "./pages/AboutPage";
import SearchPage from "./pages/SearchPage";
import LegalPage from "./pages/LegalPage";
import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/admin/AdminDashboard";
import ArticlesList from "./pages/admin/ArticlesList";
import ArticleEditor from "./pages/admin/ArticleEditor";
import CategoriesManager from "./pages/admin/CategoriesManager";
import HomepageCuration from "./pages/admin/HomepageCuration";

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
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/latest" element={<LatestNewsPage />} />
            <Route path="/category/:slug" element={<LatestNewsPage />} />
            <Route path="/education" element={<EducationPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/page/:slug" element={<LegalPage />} />
            <Route path="/:category/:slug" element={<ArticlePage />} />

            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={<AdminDashboard />}>
              <Route path="articles" element={<ArticlesList />} />
              <Route path="articles/new" element={<ArticleEditor />} />
              <Route path="articles/edit/:id" element={<ArticleEditor />} />
              <Route path="categories" element={<CategoriesManager />} />
              <Route path="homepage" element={<HomepageCuration />} />
            </Route>
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
