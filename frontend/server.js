const express = require('express');
const path = require('path');
const http = require('https');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND = process.env.REACT_APP_BACKEND_URL || '';

// Proxy sitemap requests to backend
function proxyToBackend(backendPath, res) {
  if (!BACKEND) {
    return res.status(503).send('Backend not configured');
  }
  const url = `${BACKEND}${backendPath}`;
  http.get(url, (upstream) => {
    res.set('Content-Type', 'application/xml');
    upstream.pipe(res);
  }).on('error', (err) => {
    console.error('Sitemap proxy error:', err.message);
    res.status(502).send('Sitemap unavailable');
  });
}

app.get('/sitemap.xml', (req, res) => proxyToBackend('/api/sitemap.xml', res));
app.get('/news-sitemap.xml', (req, res) => proxyToBackend('/api/news-sitemap.xml', res));

// Serve static files
app.use(express.static(path.join(__dirname, 'build'), { maxAge: '1y' }));

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}, backend: ${BACKEND}`);
});
