import logging

_LOGGER = logging.getLogger(__name__)

ZOLEO_LIMIT = 200
INREACH_LIMIT = 160

def split_message(text, config=None):
    """Split a forecast message into device-compatible chunks with numbering."""
    _LOGGER.debug("Splitting message, input length: %d characters, config: %s", len(text), config)
    
    parts = []
    
    if config:
        if config.get('character_limit', 0) > 0:
            max_len = config['character_limit']
            _LOGGER.debug("Using custom character limit: %d", max_len)
        elif config.get('device_type') == 'inreach':
            max_len = INREACH_LIMIT
            _LOGGER.debug("Using InReach character limit: %d", max_len)
        else:
            max_len = ZOLEO_LIMIT
            _LOGGER.debug("Using ZOLEO character limit: %d", max_len)
    else:
        max_len = ZOLEO_LIMIT
        _LOGGER.debug("No config provided, using default ZOLEO limit: %d", max_len)

    _LOGGER.debug("Effective max length per part: %d (accounting for part numbering)", max_len - 7)
    
    remaining_text = text
    part_count = 0
    
    while remaining_text:
        part_count += 1
        _LOGGER.debug("Processing part %d, remaining text length: %d", part_count, len(remaining_text))
        
        if len(remaining_text) <= max_len - 7:  # leave space for (1/3), etc.
            parts.append(remaining_text)
            _LOGGER.debug("Final part %d added, length: %d", part_count, len(remaining_text))
            break
            
        idx = remaining_text.rfind("\n", 0, max_len - 7)
        if idx == -1:
            idx = max_len - 7
            _LOGGER.debug("No newline found, splitting at character %d", idx)
        else:
            _LOGGER.debug("Found newline at position %d", idx)
            
        part_text = remaining_text[:idx].strip()
        parts.append(part_text)
        _LOGGER.debug("Part %d added, length: %d", part_count, len(part_text))
        
        remaining_text = remaining_text[idx:].strip()

    # Add part numbers
    total = len(parts)
    if total > 1:
        _LOGGER.debug("Adding part numbers to %d parts", total)
        parts = [f"({i+1}/{total}) {p}" for i, p in enumerate(parts)]
        for i, part in enumerate(parts):
            _LOGGER.debug("Part %d/%d final length: %d", i+1, total, len(part))
    else:
        _LOGGER.debug("Single part message, no numbering needed")
    
    _LOGGER.debug("Message splitting completed, %d parts created", len(parts))
    return parts
