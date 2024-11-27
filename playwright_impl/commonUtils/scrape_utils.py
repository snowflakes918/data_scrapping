import base64


def apply_transform(value, transform_name):
    if transform_name == 'strip_mailto':
        return strip_mailto(value)
    return value


def strip_mailto(value):
    if value and value.startswith("mailto:"):
        return value.replace("mailto:", "")
    return value


def decode_email(script_content):
    """
    Decodes the Base64-encoded email address from script content.
    """
    try:
        # Extract the Base64 string from the script content
        start = script_content.find('atob("') + len('atob("')
        end = script_content.find('")', start)
        encoded_email = script_content[start:end]
        return base64.b64decode(encoded_email).decode('utf-8')
    except Exception as e:
        print(f"Error decoding email: {e}")
        return "N/A"


def safe_text_content(page, selector, default='N/A'):
    try:
        element = page.query_selector(selector)
        if element:
            return element.text_content().strip()
    except Exception as e:
        print(f"Error extracting content for selector {selector}: {e}")
    return default


def safe_attribute_content(page, selector, attribute, default='N/A'):
    try:
        element = page.query_selector(selector)
        if element:
            return element.get_attribute(attribute).strip()
    except Exception as e:
        print(f"Error extracting attribute {attribute} for selector {selector}: {e}")
    return default
