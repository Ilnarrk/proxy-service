import httpx
from fastapi import FastAPI, Request, Response
import uvicorn
import os

app = FastAPI(title="Proxy Service")

TARGET_HOST = os.getenv("TARGET_HOST", "http://localhost:9000").rstrip("/")
SOAP_TARGET_HOST = os.getenv("SOAP_TARGET_HOST", "http://localhost:9001").rstrip("/")


async def forward_request(request: Request, target_host: str, path: str) -> Response:
    url = f"{target_host}/{path.lstrip('/')}"
    if request.url.query:
        url += f"?{request.url.query}"

    # Forward all headers except hop-by-hop; strip values (httpx rejects trailing whitespace)
    headers = {
        k: v.strip() for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }

    body = await request.body()

    async with httpx.AsyncClient(follow_redirects=False, timeout=30.0) as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )

    # Strip hop-by-hop headers
    excluded = {
        "transfer-encoding", "connection", "keep-alive",
        "upgrade", "proxy-authenticate", "proxy-authorization",
        "te", "trailer",
    }
    resp_headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in excluded
    }

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type"),
    )


@app.post("/soap")
@app.post("/soap/{path:path}")
async def soap_proxy(request: Request, path: str = ""):
    """Forward a SOAP envelope to the separately configured SOAP server."""
    return await forward_request(request, SOAP_TARGET_HOST, path)


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
async def proxy(request: Request, path: str):
    return await forward_request(request, TARGET_HOST, path)


if __name__ == "__main__":
    host = os.getenv("PROXY_HOST", "0.0.0.0")
    port = int(os.getenv("PROXY_PORT", "8080"))
    print(
        f"Starting proxy on {host}:{port} "
        f"(HTTP → {TARGET_HOST}, SOAP → {SOAP_TARGET_HOST})"
    )
    uvicorn.run(app, host=host, port=port)
