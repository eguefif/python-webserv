from response.response_builder import get_time_now

PAGE_500 = "./html/500.html"
PAGE_400 = "./html/400.html"
PAGE_415 = "./html/415.html"

ERROR = {
    400: ("400", "BAD REQUEST "),
    415: ("415", "UNSUPPORTED MEDIA TYPE "),
    500: ("500", "INTERNAL ERROR "),
}


def get_header(length, error):
    code, message = ERROR[error]
    header = f"HTTP/1.1 {code} {message}\r\n"
    header += f"Date: {get_time_now()}\r\n"
    header += "Accept_Ranges: bytes\r\n"
    header += f"Content-Length: {length}\r\n"
    header += "Content-Type: html\r\n\r\n"
    return header


def get_body(path):
    with open(path, "r") as f:
        content = f.read()
    return content


def get_error_message(error):
    path = PAGE_500
    if hasattr(error, "status"):
        match error.status:
            case 400:
                path = PAGE_400
            case 415:
                path = PAGE_415
    body = get_body(path)
    response = get_header(len(body), 500)
    response += body
    return response
