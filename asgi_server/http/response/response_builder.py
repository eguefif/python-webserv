import datetime


def closing_message():
    header = "HTTP/1.1 200 OK\r\n"
    header += f"Date: {get_time_now()}\r\n"
    header += "Content-Length: 0\r\n"
    header += "Connection: close\r\n"

    return header


def get_time_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d, %b %Y %H:%M:%S GMT")
