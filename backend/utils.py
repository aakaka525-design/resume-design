from fastapi.responses import JSONResponse


def api_response(
    data=None,
    status: int = 200,
    message: str = "success",
    http_status: int = 200,
):
    """统一 API 响应格式，兼容前端 data.data.status / data.data.data 的访问方式"""
    return JSONResponse(
        status_code=http_status,
        content={
            "status": status,
            "data": data,
            "message": message,
        },
    )


def api_list_response(data_list: list, total: int = 0, page: int = 1, limit: int = 10):
    """分页列表响应"""
    return JSONResponse(content={
        "status": 200,
        "data": {
            "list": data_list,
            "total": total,
            "page": page,
            "limit": limit,
        },
        "message": "success",
    })
