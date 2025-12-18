## 2024-03-24 - [Log Redaction & DoS Prevention]
**Vulnerability:** PII (email username) was exposed in debug logs in `imap_handler.py`. Also, processing an unlimited number of emails in `check_imap_for_gps` could lead to a Denial of Service if the inbox is flooded.
**Learning:** Even debug logs should be sanitized for PII. Unbounded loops processing external input (emails) are a risk.
**Prevention:**
1. Redact sensitive info (username) in logs: `masked_user = f"{username[:3]}...@{...}"`.
2. Implement limits on processing loops: `MAX_EMAIL_LIMIT = 10` and break/truncate the list.
