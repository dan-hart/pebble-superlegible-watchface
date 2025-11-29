# Security Policy

## Scope

This document outlines the security posture of the **Superlegible** Pebble watchface.

## No Secrets Policy

**This repository must never contain:**
- API keys or tokens
- Passwords or credentials
- Private keys (SSH, GPG, etc.)
- Environment files with sensitive values (`.env` with secrets)
- Database connection strings with credentials
- Any other sensitive authentication data

If you discover any secrets accidentally committed to this repository, please report it immediately (see below).

## Watchface Security Properties

The Superlegible watchface is designed with minimal permissions:

- **No network access**: The watchface does not connect to the internet
- **No data collection**: No user data is collected, stored, or transmitted
- **No sensitive permissions**: Only basic time display functionality
- **No external dependencies**: Runs entirely on-device using Pebble SDK APIs
- **Open source**: All code is publicly auditable

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **GitHub Issues**: Open an issue at [github.com/dan-hart/pebble-superlegible-watchface/issues](https://github.com/dan-hart/pebble-superlegible-watchface/issues)
2. **Email**: Contact the maintainer through GitHub

Please include:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact assessment

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Resolution**: Depends on severity, typically within 2 weeks for critical issues

## Security Best Practices for Contributors

When contributing to this project:

1. Never commit secrets, credentials, or API keys
2. Use `.gitignore` patterns for sensitive local files
3. Review your changes before committing
4. If you accidentally commit sensitive data, notify the maintainer immediately

---

Last updated: 2025-11-29
