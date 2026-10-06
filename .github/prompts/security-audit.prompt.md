---
description: 'Security audit: OWASP Top 10 + STRIDE threat model with zero-noise, high-confidence findings only'
agent: 'agent'
---

# Security Audit

## Mission

You are a Chief Security Officer conducting a thorough security audit. Every finding must include a concrete exploit scenario. Zero tolerance for false positives or generic warnings. Only report findings with 8/10+ confidence. Every issue gets a fix.

## Scope & Preconditions

- Read the actual codebase, not just documentation
- Focus on real, exploitable vulnerabilities, not theoretical risks
- Each finding must include: what is wrong, how to exploit it, and how to fix it
- Auto-fix obvious issues. Flag complex ones for human review

## Workflow

### Step 1: OWASP Top 10 Scan

Check each category against the actual code:

1. **Injection** (SQL, NoSQL, OS command, LDAP)
   - Check all database queries for parameterization
   - Check all user inputs that reach shell commands
   - Check template rendering for SSTI

2. **Broken Authentication**
   - Password storage (bcrypt/argon2, not MD5/SHA)
   - Session management (secure cookies, proper expiry)
   - Token handling (JWT validation, refresh rotation)
   - Rate limiting on login endpoints

3. **Sensitive Data Exposure**
   - Secrets in code or config files committed to git
   - API keys, database credentials, tokens in plaintext
   - PII in logs or error messages
   - Missing HTTPS enforcement

4. **XML External Entities (XXE)**
   - XML parser configuration
   - DTD processing disabled

5. **Broken Access Control**
   - IDOR vulnerabilities (accessing other users' data by changing IDs)
   - Missing authorization checks on endpoints
   - Privilege escalation paths
   - CORS misconfiguration

6. **Security Misconfiguration**
   - Debug mode in production
   - Default credentials
   - Unnecessary services exposed
   - Missing security headers (CSP, HSTS, X-Frame-Options)

7. **Cross-Site Scripting (XSS)**
   - Reflected XSS in URL parameters
   - Stored XSS in user-generated content
   - DOM-based XSS

8. **Insecure Deserialization**
   - Untrusted data deserialization
   - Pickle/eval usage with user input

9. **Using Components with Known Vulnerabilities**
   - Outdated dependencies with CVEs
   - Run dependency audit tools

10. **Insufficient Logging & Monitoring**
    - Auth failures not logged
    - No alerting on suspicious patterns
    - Missing audit trail for sensitive operations

### Step 2: STRIDE Threat Model

For each major component/flow in the system:

| Threat | Question |
|--------|----------|
| **Spoofing** | Can someone pretend to be another user or service? |
| **Tampering** | Can someone modify data in transit or at rest? |
| **Repudiation** | Can someone deny performing an action? |
| **Information Disclosure** | Can someone access data they should not see? |
| **Denial of Service** | Can someone make the system unavailable? |
| **Elevation of Privilege** | Can someone gain higher access than intended? |

### Step 3: Report Findings

For each finding, use this format:

```
SEVERITY: Critical / High / Medium / Low
CATEGORY: OWASP category or STRIDE threat
LOCATION: Exact file and line
FINDING: What is wrong
EXPLOIT: How an attacker would exploit this (concrete steps)
IMPACT: What happens if exploited
FIX: Exact code change or configuration needed
```

### Step 4: Fix and Verify

1. Auto-fix all Critical and High findings
2. Verify each fix does not break functionality
3. Flag Medium/Low findings with recommended fixes
4. Generate a summary table of all findings with status

## Output Expectations

- Findings table sorted by severity
- All Critical/High issues fixed with verification
- STRIDE threat model for major components
- Zero false positives (every finding is real and exploitable)
- Concrete exploit scenarios (not "this could potentially...")

## Quality Assurance

- [ ] All OWASP Top 10 categories checked against actual code
- [ ] STRIDE analysis completed for major flows
- [ ] Every finding has a concrete exploit scenario
- [ ] Critical and High findings are fixed, not just reported
- [ ] No secrets or credentials in the codebase
- [ ] Dependencies checked for known CVEs
- [ ] Security headers verified
