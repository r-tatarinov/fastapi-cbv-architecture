import datetime
import json

import yaml
import dicttoxml
from starlette.responses import JSONResponse, Response

from src.app.i18n.context import get_i18n_meta


def make_data_by_response(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, JSONResponse):
            return result

        data, status_code, meta, fmt, is_download = result
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        response = {
            "data": data,
            "success": status_code < 400
        }
        if meta:
            if isinstance(meta, dict):
                meta.setdefault("i18n", get_i18n_meta())
            response['meta'] = meta

        if fmt == "xml":
            xml_bytes = dicttoxml.dicttoxml(response, custom_root="response", attr_type=False)
            headers = {"Content-Disposition": f"attachment; filename={timestamp_str}.xml"} if is_download else None
            return Response(
                content=xml_bytes,
                media_type="application/xml",
                headers=headers,
                status_code=status_code
            )

        elif fmt in ("yaml", "yml"):
            yaml_str = yaml.dump(response, allow_unicode=True)
            headers = {"Content-Disposition": f"attachment; filename={timestamp_str}.yaml"} if is_download else None
            return Response(
                content=yaml_str.encode("utf-8"),
                media_type="application/x-yaml",
                headers=headers,
                status_code=status_code
            )

        if is_download:
            json_str = json.dumps(response)
            headers = {"Content-Disposition": f"attachment; filename={timestamp_str}.json"}
            return Response(
                content=json_str.encode("utf-8"),
                media_type="application/json",
                headers=headers,
                status_code=status_code
            )

        return JSONResponse(content=response, status_code=status_code)

    return wrapper
