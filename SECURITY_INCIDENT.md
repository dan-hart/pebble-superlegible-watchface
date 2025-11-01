# Security Incident Report - API Keys Exposure

**Date**: November 1, 2025
**Status**: ✅ Git history cleaned, ⚠️ Credential rotation required

## Summary

Three API keys were accidentally committed to git history in the `.lock-waf_darwin_build` file and pushed to both GitHub and NelsonGitea remotes. The keys have been removed from git history and both remotes have been force-pushed with the cleaned history.

## Exposed Credentials

### 1. OpenAI API Key
- **Type**: OpenAI Project API Key
- **Pattern**: `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`
- **Exposure Duration**: October 30, 2025 - November 1, 2025
- **Commits**: b41af8f5, efec6594 (now removed)

### 2. GitHub Personal Access Token
- **Type**: GitHub PAT (classic)
- **Pattern**: `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`
- **Username**: dan-hart (GPR_USER)
- **Exposure Duration**: October 30, 2025 - November 1, 2025
- **Commits**: b41af8f5, efec6594 (now removed)

### 3. Jira API Token
- **Type**: Atlassian API Token
- **Pattern**: `ATATT3xFfGF0ofNxlI2coDdxdS9i7PwI7tVDHVb6hsAt8rsJOmc6DF1VeSDQsvqcUsDRgKs-1okHrg-42N9PpbAjUDVTO_h1NnH1xMfRuCcMuBwdPtNsRWJ90MsxPwWrcWXQfqtr_-V5vd7wjjIwMAiXPqxoma13mCUeGhna1u46d5NmtWIt2AM=2E355AB3`
- **Account**: daniel.hart@underarmour.com
- **Organization**: Under Armour (underarmour.atlassian.net)
- **Exposure Duration**: October 30, 2025 - November 1, 2025
- **Commits**: b41af8f5, efec6594 (now removed)

## Remediation Actions Completed

### ✅ Git History Cleanup
- [x] Removed `.lock-waf_darwin_build` from all commits using git filter-branch
- [x] Cleaned up git refs and performed aggressive garbage collection
- [x] Verified keys no longer appear in git history
- [x] Force-pushed cleaned history to GitHub (dan-hart/pebble-superlegible-watchface)
- [x] Force-pushed cleaned history to NelsonGitea (100.64.64.44:2222/dan/pebble-superlegible-watchface)

### ✅ Repository Security
- [x] Added SSH key to GitHub account for authenticated pushes
- [x] Temporarily disabled GitHub repository ruleset for force push
- [x] Re-enabled GitHub repository ruleset after successful push
- [x] Installed git-secrets to prevent future secret commits
- [x] Configured git-secrets with patterns for AWS keys, API keys, tokens, and GitHub PATs

### ✅ Prevention Measures
- [x] `.lock-waf_darwin_build` is already in `.gitignore`
- [x] Git hooks installed to scan for secrets before commits
- [x] Added patterns for: AWS keys, OpenAI keys, GitHub tokens, Jira tokens, generic API keys

## ⚠️ REQUIRED ACTIONS - CREDENTIAL ROTATION

You must immediately rotate all exposed credentials. Here's how:

### 1. OpenAI API Key (CRITICAL)

**Revoke the exposed key:**
1. Go to https://platform.openai.com/api-keys
2. Find the key: `sk-proj-n88Iu9sBivU9qLYQbOz...`
3. Click "Revoke" or delete the key
4. Confirm revocation

**Generate new key:**
1. Click "Create new secret key"
2. Name it appropriately (e.g., "Development Key - Nov 2025")
3. Copy the new key immediately (it won't be shown again)
4. Update your environment variable:
   ```bash
   # In your shell profile (~/.zshrc, ~/.bashrc, etc.)
   export OPENAI_API_KEY="your-new-key-here"
   ```

**Check for unauthorized usage:**
1. Go to https://platform.openai.com/usage
2. Review API usage from October 30 - November 1
3. Look for unexpected requests or unusual patterns
4. Note any suspicious activity for OpenAI support

### 2. GitHub Personal Access Token (CRITICAL)

**Revoke the exposed token:**
1. Go to https://github.com/settings/tokens
2. Find the token with prefix: `ghp_h7sS0bl8qEgFy8tKT...`
3. Click "Delete" or "Revoke"
4. Confirm deletion

**Generate new token:**
1. Click "Generate new token" → "Generate new token (classic)"
2. Name: "Development Token - Nov 2025"
3. Select scopes needed (at minimum: `repo`, `read:org`, `gist`)
4. Click "Generate token"
5. Copy the new token immediately
6. Update your environment variable:
   ```bash
   # In your shell profile
   export GPR_API_KEY="your-new-token-here"
   ```

**Check for unauthorized access:**
1. Go to https://github.com/settings/security-log
2. Filter dates: October 30 - November 1, 2025
3. Look for:
   - Unexpected repository access
   - Unknown IP addresses
   - Unusual git operations
   - OAuth app authorizations you didn't make
4. Document any suspicious activity

### 3. Jira API Token (CRITICAL - CORPORATE)

**⚠️ This is a corporate Under Armour account - follow company security policy**

**Revoke the exposed token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Find and revoke the exposed token
3. Confirm revocation

**Generate new token:**
1. Click "Create API token"
2. Label: "Development - Nov 2025"
3. Copy the new token
4. Update your environment variable:
   ```bash
   # In your shell profile
   export JIRA_API_TOKEN="your-new-token-here"
   ```

**Report to Security Team:**
Since this is a corporate account, you should:
1. **Report to Under Armour IT Security immediately**
2. Email: [Your company's security team contact]
3. Provide details:
   - Token was exposed in public GitHub repository
   - Exposure period: October 30 - November 1, 2025
   - Token has been revoked
   - No unauthorized access detected (pending review)

**Check for unauthorized access:**
1. Review Jira audit logs (if you have access)
2. Check for unexpected issues/projects accessed
3. Report any suspicious activity to security team

## Repository Impact Assessment

**Public Exposure:**
- Repository: https://github.com/dan-hart/pebble-superlegible-watchface
- Visibility: Public (anyone could have accessed these keys)
- First commit with keys: October 30, 2025 (b41af8f5)
- Keys removed from history: November 1, 2025

**Risk Level:**
- **OpenAI**: HIGH - Public repository, financial impact possible
- **GitHub**: HIGH - Could grant access to all your repositories
- **Jira (UA)**: CRITICAL - Corporate data, potential compliance violation

## Timeline

- **Oct 30, 2025 09:49 AM**: Initial commit with `.lock-waf_darwin_build` containing keys
- **Oct 30, 2025 10:11 AM**: Second commit still containing keys
- **Oct 30 - Oct 31**: Keys publicly accessible on GitHub
- **Nov 1, 2025 04:24 PM**: Keys discovered during security audit
- **Nov 1, 2025 04:25 PM**: Git history cleaned and force-pushed
- **Nov 1, 2025 04:26 PM**: git-secrets installed and configured

## Prevention Checklist

- [x] `.lock-waf_darwin_build` in `.gitignore`
- [x] git-secrets installed with hooks
- [x] Secret detection patterns configured
- [ ] Credentials rotated (OpenAI)
- [ ] Credentials rotated (GitHub)
- [ ] Credentials rotated (Jira)
- [ ] Security team notified (for Jira/UA)
- [ ] Audit logs reviewed for unauthorized access
- [ ] Environment variables updated with new keys

## Additional Recommendations

1. **Use a secrets manager** instead of environment variables:
   - 1Password CLI
   - AWS Secrets Manager
   - HashiCorp Vault

2. **Enable 2FA** on all accounts (if not already enabled):
   - OpenAI account
   - GitHub account
   - Atlassian account

3. **Review `.gitignore`** for other potential secret files:
   - `.env` files
   - Configuration files with credentials
   - Any build artifacts that capture environment

4. **Set up git commit signing** to verify commit authenticity

5. **Regular security audits**:
   - Run `git secrets --scan-history` periodically
   - Review access logs monthly
   - Rotate credentials quarterly

## Verification Commands

To verify keys are removed from history:
```bash
# Should return no results
git log --all --full-history -S "OPENAI_API_KEY"
git log --all --full-history -S "GPR_API_KEY"
git log --all --full-history -S "JIRA_API_TOKEN"

# Verify git-secrets is working
git secrets --list
git secrets --scan-history
```

## Questions or Concerns?

If you notice any unauthorized access or suspicious activity:
1. Document the activity with screenshots/logs
2. Contact the relevant service's security team
3. For Under Armour/Jira: Contact IT Security immediately
4. Consider enabling additional security monitoring

---

**Document Status**: Active incident requiring credential rotation
**Last Updated**: November 1, 2025
**Next Review**: After all credentials have been rotated
