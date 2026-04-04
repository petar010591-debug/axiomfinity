const express = require('express');
const path = require('path');
const https = require('https');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND = process.env.REACT_APP_BACKEND_URL || '';

function proxyToBackend(backendPath, res) {
  if (!BACKEND) return res.status(503).send('Backend not configured');
  https.get(`${BACKEND}${backendPath}`, (upstream) => {
    res.set('Content-Type', 'application/xml');
    upstream.pipe(res);
  }).on('error', () => res.status(502).send('Sitemap unavailable'));
}

app.get('/sitemap.xml', (req, res) => proxyToBackend('/api/sitemap.xml', res));
app.get('/news-sitemap.xml', (req, res) => proxyToBackend('/api/news-sitemap.xml', res));

app.use(express.static(path.join(__dirname, 'build'), { maxAge: '1y' }));

// SPA fallback - use regex pattern for Express 5 compatibility
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => console.log(`Server on port ${PORT}, backend: ${BACKEND}`));
