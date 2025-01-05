
def format_datetime(dt=None, fmt='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object or the current time.
    
    Args:
        dt (datetime, optional): The datetime object to format. Defaults to None (current time).
        fmt (str, optional): The format string. Defaults to '%Y-%m-%d %H:%M:%S'.
    
    Returns:
        str: The formatted datetime string.
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)

if __name__ == "__main__":
    print(format_datetime())
