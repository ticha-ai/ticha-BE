import json
import logging

import inflection
from fastapi import Request, Response
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
        # OpenAPI 문서 요청은 변환하지 않음
        if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
            return await call_next(request)

        response = await call_next(request)

        if response is None:
            return Response(status_code=500)

        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type.lower():
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            if not response_body:
                return response

            try:
                response_data = json.loads(response_body)
                camel_case_data = to_camel_case(response_data)

                headers = dict(response.headers)
                headers.pop("content-length", None)

                return JSONResponse(
                    content=camel_case_data,
                    status_code=response.status_code,
                    headers=headers,
                )
            except json.JSONDecodeError:
                logger.error("Invalid JSON in response body")
                return response

        return response

    except Exception as e:
        logger.error(f"Camel Case Middleware Error: {e}", exc_info=True)
        return Response(status_code=500, content={"detail": "Internal Server Error"})
