import json

import inflection
from fastapi import Request
from fastapi.responses import JSONResponse


def to_camel_case(data):
    if isinstance(data, dict):
        return {
            inflection.camelize(str(k), uppercase_first_letter=False): to_camel_case(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [to_camel_case(i) for i in data]
    else:
        return data


async def camel_case_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        if response.headers.get("content-type") == "application/json":
            response_body = [section async for section in response.body_iterator]
            response_data = json.loads(response_body[0])
            camel_case_data = to_camel_case(response_data)
            response = JSONResponse(content=camel_case_data)
        return response
    except Exception as e:
        print(f"Camel Case Middleware Error: {e}")
        raise e
