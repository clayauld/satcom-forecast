from __future__ import annotations

import asyncio
import email
import imaplib
import logging
import re
from email.message import Message
from email.utils import parseaddr
from typing import Any, Dict, List, Optional, Union, cast

_LOGGER = logging.getLogger(__name__)


async def check_imap_for_gps(
    host: str,
    port: int,
    username: str,
    password: str,
    folder: str = "INBOX",
    security: str = "SSL",
) -> List[Dict[str, Any]]:
    _LOGGER.debug(
        "Checking IMAP for GPS coordinates - Host: %s, Port: %s, User: %s, Folder: %s, Security: %s",
        host,
        port,
        username,
        folder,
        security,
    )

    try:
        # Run the synchronous IMAP operation in a thread pool
        result = await asyncio.to_thread(
            _check_imap_sync,
            host,
            port,
            username,
            password,
            folder,
            security,
        )
        return result

    except Exception as e:
        _LOGGER.exception("Error checking IMAP: %s", str(e))
        return []


def _check_imap_sync(
    host: str,
    port: int,
    username: str,
    password: str,
    folder: str = "INBOX",
    security: str = "SSL",
) -> List[Dict[str, Any]]:
    """Blocking IMAP interaction executed in a background thread."""

    mail: Optional[Union[imaplib.IMAP4, imaplib.IMAP4_SSL]] = None
    try:
        # Establish connection based on security type
        if security == "SSL":
            _LOGGER.debug("Establishing IMAP SSL connection to %s:%s", host, port)
            mail = imaplib.IMAP4_SSL(host, port)
            _LOGGER.debug("IMAP SSL connection established successfully")
        elif security == "STARTTLS":
            _LOGGER.debug(
                "Establishing IMAP connection to %s:%s with STARTTLS", host, port
            )
            mail = imaplib.IMAP4(host, port)
            mail.starttls()
            _LOGGER.debug("IMAP STARTTLS connection established successfully")
        else:  # None
            _LOGGER.debug(
                "Establishing unencrypted IMAP connection to %s:%s", host, port
            )
            mail = imaplib.IMAP4(host, port)
            _LOGGER.debug("IMAP unencrypted connection established successfully")

        _LOGGER.debug("Attempting login for user: %s", username)
        mail.login(username, password)
        _LOGGER.debug("IMAP login successful")

        # List available folders for debugging
        try:
            status, folders = mail.list()
            if status == "OK":
                decoded_folders: List[str] = []
                for raw in folders or []:
                    folder_bytes = cast(Union[bytes, Any], raw)
                    if isinstance(folder_bytes, bytes):
                        decoded = folder_bytes.decode(errors="ignore")
                    else:
                        decoded = str(folder_bytes)

                    name = (
                        decoded.split('"')[-2]
                        if '"' in decoded
                        else decoded.split()[-1]
                    )
                    decoded_folders.append(name)

                _LOGGER.debug("Available folders: %s", decoded_folders)
            else:
                _LOGGER.debug("Could not list folders: %s", status)
        except Exception as e:
            _LOGGER.debug("Error listing folders: %s", str(e))

        # Select the folder and check the response
        _LOGGER.debug("Attempting to select folder: %s", folder)
        status, data = mail.select(folder)
        if status != "OK":
            _LOGGER.error("Failed to select folder '%s': %s", folder, status)
            if data:
                _LOGGER.error("Folder selection error details: %s", data)
            return []

        _LOGGER.debug("Successfully selected folder: %s", folder)

        # Now we can safely search since we're in SELECTED state
        _LOGGER.debug("Searching for unread messages")
        status, messages = mail.search(None, "(UNSEEN)")
        if status != "OK":
            _LOGGER.error("Failed to search mailbox: %s", status)
            if messages:
                _LOGGER.error("Search error details: %s", messages)
            return []

        message_count = len(messages[0].split()) if messages and messages[0] else 0
        _LOGGER.debug("Found %d unread messages", message_count)

        result = []
        for num in messages[0].split():
            _LOGGER.debug("Processing message number: %s", num)

            typ, data = mail.fetch(num, "(RFC822)")
            if typ != "OK":
                _LOGGER.debug("Failed to fetch message %s: %s", num, typ)
                continue

            if not data or not isinstance(data[0], tuple):
                _LOGGER.debug("Unexpected fetch data format for msg %s: %s", num, data)
                continue

            payload = data[0][1]
            if not isinstance(payload, (bytes, bytearray)):
                _LOGGER.debug("Skipping non-bytes payload for msg %s", num)
                continue

            msg: Message = email.message_from_bytes(payload)
            sender_header = msg.get("From", "")
            from_email = parseaddr(sender_header)[1] if sender_header else "unknown"
            _LOGGER.debug("Processing message from: %s", from_email)

            body = ""
            if msg.is_multipart():
                _LOGGER.debug("Message is multipart, extracting text/plain content")
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = _safe_decode_payload(part.get_payload(decode=True))
                        break
            else:
                _LOGGER.debug("Message is single part, extracting payload")
                body = _safe_decode_payload(msg.get_payload(decode=True))

            _LOGGER.debug("Message body length: %d characters", len(body))

            fmt_match = re.search(r"\b(summary|compact|full)\b", body, re.I)
            if fmt_match:
                _LOGGER.debug("Found format preference: %s", fmt_match.group(1))
            else:
                _LOGGER.debug("No format preference found, will use default")

            # Extract days override
            days_override = extract_days_override(body)
            if days_override:
                _LOGGER.debug("Found days override: %d days", days_override)
            else:
                _LOGGER.debug("No days override found, will use default")

            coords = re.search(r"(-?\d+\.\d+)[,;\s]+(-?\d+\.\d+)", body)
            if coords:
                lat, lon = coords.group(1), coords.group(2)
                _LOGGER.debug("Found coordinates: %s, %s", lat, lon)

                result.append(
                    {
                        "lat": lat,
                        "lon": lon,
                        "sender": from_email,
                        "format": fmt_match.group(1).lower() if fmt_match else None,
                        "days": days_override,
                        "body": body.strip(),
                    }
                )
                _LOGGER.debug("Added GPS request to processing queue")
                # Mark the message as seen to avoid reprocessing it in future polling cycles
                try:
                    mail.store(num, "+FLAGS", "\\Seen")
                    _LOGGER.debug("Marked message %s as seen", num)
                except Exception as e:
                    _LOGGER.debug("Failed to mark message %s as seen: %s", num, str(e))
            else:
                _LOGGER.debug("No coordinates found in message from %s", from_email)

        _LOGGER.debug("Returning %d GPS requests", len(result))
        return result

    except Exception as e:
        _LOGGER.exception("Error checking IMAP: %s", str(e))
        return []
    finally:
        if mail:
            try:
                _LOGGER.debug("Logging out from IMAP")
                mail.logout()
                _LOGGER.debug("IMAP logout successful")
            except Exception as e:
                _LOGGER.debug("Error during IMAP logout: %s", str(e))


def extract_days_override(body: str) -> Optional[int]:
    """Extract days override from message body.

    Looks for patterns like "5days", "5 days", "3day", "3 day", "0days", "current", "today" etc.
    Returns the number of days (0-7) if found, otherwise None.

    Special values:
    - 0, "current", "today" = only current day (day 0)
    - 1 = current day + next full day (day 0 + day 1)
    - 2 = current day + next 2 full days (day 0 + day 1 + day 2)
    - etc.
    """
    # First check for special keywords
    if re.search(r"\b(current|today)\b", body, re.IGNORECASE):
        _LOGGER.debug("Found special keyword 'current' or 'today', returning 0 days")
        return 0

    # Pattern to match: number 0-7 followed by optional space and "day" or "days"
    # Examples: "5days", "5 days", "3day", "3 day", "0days", "0 day", "7days", "7 days"
    # Excludes negative numbers like "-1days" and numbers outside 0-7
    pattern = r"(?<![\d-])([0-7])\s*(?:day|days)\b"
    match = re.search(pattern, body, re.IGNORECASE)

    if match:
        days = int(match.group(1))
        # Validate range 0-7
        if 0 <= days <= 7:
            _LOGGER.debug("Found days override: %d days", days)
            return days
        else:
            _LOGGER.debug("Days override out of range (0-7): %d", days)
            return None

    _LOGGER.debug("No days override found in message")
    return None


def _safe_decode_payload(payload: Any) -> str:
    """Return the e-mail *payload* as text regardless of its underlying type.

    ``email.message.Message.get_payload(decode=True)`` may return *bytes*,
    *str*, or even ``None``.  Trying to call ``.decode`` unconditionally on the
    result can therefore raise *AttributeError* when the payload is already a
    string.  This helper normalises the value so that the caller always
    receives a plain ``str``.
    """

    if payload is None:
        return ""

    # If we already have a string, return it unchanged.
    if isinstance(payload, str):
        return payload

    # Fallback: assume bytes-like – try UTF-8 first and ignore errors.
    try:
        return payload.decode("utf-8", errors="ignore")
    except Exception:  # pragma: no cover – extremely rare encodings
        try:
            return payload.decode(errors="ignore")  # Use system default
        except Exception:
            # As a last resort, repr() keeps us from crashing the loop.
            return repr(payload)
