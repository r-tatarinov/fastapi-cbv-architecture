from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from src.app.i18n.context import DEFAULT_LANGUAGE


security = HTTPBearer()


class GeneralHeadersModel:
    def __init__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        self.authorization_token = credentials.credentials


class GeneralParams:
    def __init__(
        self,
        start: int = Query(
            default=0,
            description="С какого порядкового инстанса начинать (для пагинации)"
        ),
        limit: int = Query(
            default=20,
            description="Сколько инстансов вернуть"
        ),
        order_by: str = Query(
            default='id_asc',
            description="Сортировка в формате &lt;поле&gt;_asc или &lt;поле&gt;_desc"
        ),
        response_fmt: str = Query(
            default='json',
            description="Формат респонса (json, yaml, yml, xml)"
        ),
        is_download: int = Query(
            default=0,
            description="Нужно ли выгрузить результат файлом"
        ),
        search: str = Query(
            default=None,
            description="Поисковая строка (может по нескольким полям, если реализовано)"
        ),
        filter_by: str = Query(
            default=None,
            description=(
                    "Фильтрация по полям. Значения разделяются запятой, фильтры — точкой с запятой.<br><br>"
                    "<b>Формат:</b> "
                    "<code>&lt;поле&gt;:&lt;значение1&gt;,&lt;значение2&gt;;"
                    "&lt;другое_поле&gt;:&lt;значение&gt;</code>"
            )
        ),
        lang: str = Query(
            default=DEFAULT_LANGUAGE,
            description="Язык локализации ответа (ru, en, ar, zh, kk)"
        ),
    ):
        def _coerce(value):
            return value.default if hasattr(value, "default") else value

        self.start = _coerce(start)
        self.limit = _coerce(limit)
        self.order_by = _coerce(order_by)
        self.response_fmt = _coerce(response_fmt)
        self.is_download = _coerce(is_download)
        self.search = _coerce(search)
        self.filter_by = _coerce(filter_by)
        self.lang = _coerce(lang)


class GeneralI18nMeta(BaseModel):
    requested_lang: str = Field(..., description="Запрошенный язык ответа")
    resolved_lang: str = Field(..., description="Фактически использованный язык ответа")
    fallback_used: bool = Field(..., description="Использовался ли базовый язык вместо запрошенного")


class GeneralListMeta(BaseModel):
    total: int = Field(..., description="Количество записей на текущей странице")
    counts: int = Field(..., description="Общее количество записей после поиска и фильтрации")
    i18n: GeneralI18nMeta = Field(..., description="Информация о языке ответа")


class LanguageParams:
    def __init__(
        self,
        lang: str = Query(
            default=DEFAULT_LANGUAGE,
            description="Язык локализации/записи (ru, en, ar, zh, kk)"
        ),
    ):
        self.lang = lang.default if hasattr(lang, "default") else lang
