import json
import logging

import inflection
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


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
        if "application/json" in response.headers.get("content-type", "").lower():
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            if not response_body:
                return response

            response_data = json.loads(response_body)
            camel_case_data = to_camel_case(response_data)
            return JSONResponse(content=camel_case_data)  # 새로운 응답 객체 반환
    except Exception as e:
        logger.error(f"Camel Case Middleware Error: {e}", exc_info=True)
        raise e
