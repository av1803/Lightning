from datetime import datetime


def date_time():
    """
    Prints the current date and time in the format [Month/Day/Year Hour:Minute:Second].

    Example: [04/27/2022 18:13:23]

    :returns the current date-time with format [%m/%d/%Y %H:%M:%S]
    """
    return datetime.now().strftime("[%m/%d/%Y %H:%M:%S] ")


def is_blocked(text: str):
    """
    Helper method which checks to see if we are blocked from purchasing

    :returns a boolean value
    """
    return text.find('blocked') != -1 or text.find('Verify') != -1 or text.find('Forbidden') != -1
