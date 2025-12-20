## 2024-02-14 - [IMAP Handler Security Hardening]
**Vulnerability:** Unbounded IMAP email processing allowed potential Denial of Service (DoS) via mailbox flooding. Debug logs exposed PII (usernames, email addresses).
**Learning:** IMAP search results can be arbitrarily large. Processing them all in a loop without limits can hang the application. Standard logging of email headers can inadvertently leak PII.
**Prevention:**
1. Enforce strict limits on processed items (e.g., `MAX_EMAIL_LIMIT`).
2. Redact sensitive fields in logs (mask emails, remove passwords/usernames).
