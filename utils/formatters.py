from datetime import datetime

def format_date_str(date_str):
    """Convert date string to DD-MM-YYYY regardless of input format."""
    if not date_str:
        return ""
    
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):  # try both formats
        try:
            return datetime.strptime(str(date_str), fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue

    # fallback: return as is
    return str(date_str)


def parse_date_str(date_str):
    """Parse YYYY-MM-DD string back into datetime object."""
    if not date_str:
        return None
    return datetime.strptime(str(date_str), "%d-%m-%Y")

