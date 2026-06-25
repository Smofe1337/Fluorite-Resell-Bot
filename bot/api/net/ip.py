from fastapi import Request


def get_client_ip(request: Request) -> str:
    return request.headers.raw
