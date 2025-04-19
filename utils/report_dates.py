from datetime import date, datetime, timedelta

def get_last_complete_quarter():
    """Get last completed quarter"""
    today = date.today()
    quarter = (today.month - 1) // 3 or 4  # Q1 wraps to Q4 of prior year
    year = today.year - (1 if quarter == 4 else 0)
    return quarter, year

def get_quarter_dates(year: int, quarter: int) -> tuple[str, str]:
    """
    Returns (start_datetime, end_datetime) for a given quarter in ISO format with UTC timezone.
    
    Args:
        year: The year (e.g., 2025)
        quarter: The quarter (1-4)
    
    Returns:
        Tuple of (start_datetime, end_datetime) in format like "2025-03-31T23:59:59Z"
    
    Raises:
        ValueError: If quarter is not between 1 and 4
    """
    if quarter not in {1, 2, 3, 4}:
        raise ValueError("Quarter must be between 1 and 4")
    
    # Calculate start and end months for the quarter
    start_month = 3 * quarter - 2  # 1, 4, 7, 10
    end_month = 3 * quarter        # 3, 6, 9, 12
    
    # Start of quarter (first day of first month at 00:00:00)
    start_dt = datetime(year, start_month, 1, 0, 0, 0)
    
    # End of quarter (last day of last month at 23:59:59)
    if end_month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = end_month + 1
        next_year = year
    
    end_dt = datetime(next_year, next_month, 1, 0, 0, 0) - timedelta(seconds=1)
    
    # Format as ISO with UTC timezone (Z suffix)
    return start_dt.isoformat() + "Z", end_dt.isoformat() + "Z"