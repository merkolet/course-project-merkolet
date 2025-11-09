"""XSS protection utilities (S06-03)"""

import html
from typing import Any, Dict, List, Union


def escape_html(text: str) -> str:
    """Escape HTML special characters to prevent XSS"""
    return html.escape(text, quote=True)


def sanitize_string(value: Any) -> str:
    """Sanitize string value by escaping HTML"""
    if value is None:
        return ""
    return escape_html(str(value))


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize dictionary values"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = escape_html(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = sanitize_list(value)
        else:
            sanitized[key] = value
    return sanitized


def sanitize_list(data: List[Any]) -> List[Any]:
    """Recursively sanitize list values"""
    sanitized = []
    for item in data:
        if isinstance(item, str):
            sanitized.append(escape_html(item))
        elif isinstance(item, dict):
            sanitized.append(sanitize_dict(item))
        elif isinstance(item, list):
            sanitized.append(sanitize_list(item))
        else:
            sanitized.append(item)
    return sanitized


def sanitize_response_data(
    data: Union[Dict, List, str, Any]
) -> Union[Dict, List, str, Any]:
    """Sanitize response data to prevent XSS in JSON responses"""
    if isinstance(data, dict):
        return sanitize_dict(data)
    elif isinstance(data, list):
        return sanitize_list(data)
    elif isinstance(data, str):
        return escape_html(data)
    else:
        return data
