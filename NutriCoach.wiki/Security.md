## Security

### Built-in Protections
- BCrypt password hashing
- CSRF protection on forms (Flask-WTF)
- Session security (HTTPOnly cookies; Redis-backed via `Flask-Session`)
- RBAC: `is_admin` checks and admin-only views/APIs
- Upload safeguards: content length, extension allowlist, filename sanitization, image processing strips EXIF
- ORM protections against SQL injection

### Best Practices
- Use HTTPS in production; set `SESSION_COOKIE_SECURE=true`
- Store secrets in environment variables, not VCS
- Keep dependencies updated; run linters and tests in CI
- Limit admin access; audit logs regularly
- Enable reverse-proxy limits and WAF where applicable

### Threat Model Notes
- Session fixation/CSRF: protected by signed session and CSRF tokens on forms
- XSS: prefer escaped templates; avoid injecting unsanitized HTML
- SSRF/Outbound calls: guard with `OFFLINE_MODE` and `DISABLE_EXTERNAL_CALLS`

