# Security Policy

## Supported Versions

We aim to keep the main branch secure. Please use the latest version.

## Reporting a Vulnerability

- Email: security@example.com (replace with your security contact)
- Or open a private security advisory on the repository (preferred).

Please include:
- A clear description of the issue and potential impact
- Steps to reproduce (PoC)
- Affected components/paths
- Any suggested mitigations

We will:
- Acknowledge receipt within 72 hours
- Investigate and assess severity
- Provide a timeline and remediation plan
- Credit you if desired (and permitted)

## Secure Development Guidelines

- Never commit secrets (use `.env`, Docker secrets, or vaults)
- Always run with HTTPS in production
- Keep dependencies updated (use dependabot or similar)
- Enforce strong password policies and CSRF protection (already enabled)
- Restrict admin routes with role checks (already enforced)

## Disclosure

We prefer responsible coordinated disclosure. Do not exploit the vulnerability beyond what is necessary to prove its existence.
