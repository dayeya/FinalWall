from datetime import datetime

def current_time_formatted():
    now = datetime.now()
    date_string = now.strftime('%d %B %Y, %H:%M')
    return date_string

# Example usage:
print(current_time_formatted())