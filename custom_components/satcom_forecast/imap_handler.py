import imaplib, email, re, logging
from email.header import decode_header

_LOGGER = logging.getLogger(__name__)

def check_imap_for_gps(host, port, username, password, folder="INBOX"):
    _LOGGER.debug("Checking IMAP for GPS coordinates - Host: %s, Port: %s, User: %s, Folder: %s", 
                 host, port, username, folder)
    
    try:
        mail = imaplib.IMAP4_SSL(host, port)
        _LOGGER.debug("IMAP SSL connection established")
        
        mail.login(username, password)
        _LOGGER.debug("IMAP login successful")
        
        mail.select(folder)
        _LOGGER.debug("Selected folder: %s", folder)
        
        status, messages = mail.search(None, '(UNSEEN)')
        if status != "OK":
            _LOGGER.error("Failed to search mailbox: %s", status)
            return []
        
        _LOGGER.debug("Found %d unread messages", len(messages[0].split()) if messages[0] else 0)
        
        result = []
        for num in messages[0].split():
            _LOGGER.debug("Processing message number: %s", num)
            
            typ, data = mail.fetch(num, '(RFC822)')
            if typ != "OK": 
                _LOGGER.debug("Failed to fetch message %s: %s", num, typ)
                continue
                
            msg = email.message_from_bytes(data[0][1])
            from_email = email.utils.parseaddr(msg["From"])[1]
            _LOGGER.debug("Processing message from: %s", from_email)
            
            body = ""
            if msg.is_multipart():
                _LOGGER.debug("Message is multipart, extracting text/plain content")
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                _LOGGER.debug("Message is single part, extracting payload")
                body = msg.get_payload(decode=True).decode(errors='ignore')
            
            _LOGGER.debug("Message body length: %d characters", len(body))
            
            fmt_match = re.search(r"\b(summary|compact|full)\b", body, re.I)
            if fmt_match:
                _LOGGER.debug("Found format preference: %s", fmt_match.group(1))
            else:
                _LOGGER.debug("No format preference found, will use default")
                
            coords = re.search(r"(-?\d+\.\d+)[,;\s]+(-?\d+\.\d+)", body)
            if coords:
                lat, lon = coords.group(1), coords.group(2)
                _LOGGER.debug("Found coordinates: %s, %s", lat, lon)
                
                result.append({
                    "lat": lat,
                    "lon": lon,
                    "sender": from_email,
                    "format": fmt_match.group(1).lower() if fmt_match else None,
                    "body": body.strip()
                })
                _LOGGER.debug("Added GPS request to processing queue")
            else:
                _LOGGER.debug("No coordinates found in message from %s", from_email)
                
        mail.logout()
        _LOGGER.debug("IMAP logout successful")
        _LOGGER.debug("Returning %d GPS requests", len(result))
        return result
        
    except Exception as e:
        _LOGGER.exception("Error checking IMAP: %s", str(e))
        return []
