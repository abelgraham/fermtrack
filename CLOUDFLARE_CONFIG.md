# Cloudflare Configuration for FermTrack

## DNS Records Setup
```
# Main domain
A     fermtrack.com        -> YOUR_SERVER_IP
AAAA  fermtrack.com        -> YOUR_SERVER_IPv6 (if available)

# Test subdomain  
A     test.fermtrack.com   -> YOUR_SERVER_IP
AAAA  test.fermtrack.com   -> YOUR_SERVER_IPv6 (if available)

# API subdomain (optional)
A     api.fermtrack.com    -> YOUR_SERVER_IP
AAAA  api.fermtrack.com    -> YOUR_SERVER_IPv6 (if available)
```

## SSL/TLS Settings
- **SSL/TLS encryption mode**: Full (strict)
- **Minimum TLS Version**: 1.2
- **Opportunistic Encryption**: On
- **TLS 1.3**: Enabled
- **Automatic HTTPS Rewrites**: On
- **Always Use HTTPS**: On

## Security Settings
- **Security Level**: Medium
- **Bot Fight Mode**: On
- **Challenge Passage**: 30 minutes
- **Browser Integrity Check**: On
- **Privacy Pass**: On
- **Security Events**: Monitor

## Speed & Performance
- **Auto Minify**: 
  - JavaScript: Off (to avoid integrity issues)
  - CSS: On  
  - HTML: On
- **Brotli Compression**: On
- **Early Hints**: On
- **HTTP/3**: Enabled
- **0-RTT Connection Resumption**: On

## Page Rules
```
# Force HTTPS for all pages
Pattern: *fermtrack.com/*
Settings: Always Use HTTPS: On

# Cache static assets
Pattern: *fermtrack.com/*.css
Settings: Cache Level: Cache Everything, Edge Cache TTL: 1 month

Pattern: *fermtrack.com/*.js
Settings: Cache Level: Cache Everything, Edge Cache TTL: 1 month

Pattern: *fermtrack.com/*.woff2
Settings: Cache Level: Cache Everything, Edge Cache TTL: 1 month

# API endpoints - minimal caching
Pattern: *fermtrack.com/api/*
Settings: Cache Level: Bypass, Disable Apps
```

## Security Headers (Transform Rules)
```
# Add security headers
Expression: (http.host eq "fermtrack.com" or http.host eq "test.fermtrack.com")

Headers to add:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY  
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

## Web Analytics Settings (to fix Cloudflare Insights issues)
- **Web Analytics**: Off (or configure with proper CORS)
- **Browser Insights**: Off
- **Zaraz**: Off (unless specifically needed)

## Disable Problematic Features
- **Rocket Loader**: Off (can cause JavaScript issues)
- **Mirage**: Off (can cause image loading issues)
- **Polish**: Off (can cause integrity issues)
- **Auto Minify JavaScript**: Off (to prevent integrity hash mismatches)

## Custom Response Headers
```
# Disable Cloudflare features that cause console errors
cf-cache-status: remove
cf-ray: remove
cf-request-id: remove
```

## Troubleshooting Common Issues

### 1. Password Field Insecure Warning
**Cause**: Site served over HTTP instead of HTTPS
**Solution**: 
- Ensure "Always Use HTTPS" is enabled
- Verify SSL certificate is active
- Check that HTTPS redirect is working

### 2. CORS Beacon Errors  
**Cause**: Cloudflare Analytics trying to load cross-origin
**Solution**:
- Disable Web Analytics in Cloudflare dashboard
- Or configure proper CORS policy for static.cloudflareinsights.com

### 3. Integrity Hash Mismatch
**Cause**: Cloudflare modifying JavaScript files
**Solution**:
- Disable Auto Minify for JavaScript
- Disable Rocket Loader
- Use SRI hashes only for external CDN resources, not Cloudflare-modified content

### 4. Font Loading Issues
**Cause**: CDN caching or compression issues
**Solution**:
- Add proper Cache-Control headers for font files
- Ensure CORS is configured for font CDN
- Use font-display: swap in CSS

## Testing Commands

### Test HTTPS Redirect
```bash
curl -I http://test.fermtrack.com
# Should return 301/302 redirect to HTTPS

curl -I https://test.fermtrack.com  
# Should return 200 with security headers
```

### Test Security Headers
```bash
curl -I https://test.fermtrack.com | grep -E "(Strict-Transport|X-Content|X-Frame)"
```

### Test API Connectivity
```bash
curl -X GET https://test.fermtrack.com/api/health
# Should return: {"status":"healthy","message":"FermTrack API is running"}
```

## Recommended Cloudflare Plan Settings

### Free Plan (Basic)
- SSL/TLS: Full
- Always Use HTTPS: On
- Auto Minify HTML/CSS: On, JS: Off
- Brotli: On

### Pro Plan (Recommended)
- All Free features plus:
- WAF Custom Rules
- Page Rules (20)
- Polish: Off
- Mirage: Off  
- Advanced Security Features

### Business Plan (Production)
- All Pro features plus:
- Custom SSL certificates
- Advanced security rules
- Priority support
- Enhanced performance features

## Monitoring & Alerts

Set up alerts for:
- SSL certificate expiration
- High error rates (5xx responses)  
- DDoS attacks
- Unusual traffic patterns
- API endpoint failures

## Backup Configuration

Export Cloudflare settings regularly:
- DNS records
- Page rules  
- Security settings
- Analytics configuration

Use Cloudflare API or Terraform for infrastructure as code.