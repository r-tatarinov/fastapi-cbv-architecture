from abc import ABC

from sqlalchemy import select, func, Boolean, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from src.app.routes.base.abstract_routes import AbstractBaseRouter


class GeneralBaseRouter(AbstractBaseRouter, ABC):

    @classmethod
    async def get_response_by_select_rel(
        cls,
        session: AsyncSession,
        params,
        select_rel,
        **kwargs
    ):
        instances = await cls.get_instances_by_response(session, params, select_rel)
        if not instances:
            return cls.make_response_by_data_of_zero(params)

        data: list = await cls.get_data_by_response(
            session,
            [instance.id for instance in instances],
            params,
            **kwargs
        )   # TODO убрать итерацию по ID инстансов
        meta: dict = {
            'total': len(data),
            'counts': await cls.get_count_by_select_rel(session, select_rel, **{'params': params})
        }
        return cls.get_data(
            data=data,
            status_code=200,
            meta=meta,
            fmt=params.response_fmt,
            is_download=bool(params.is_download)
        )

    @classmethod
    def apply_filter_by(cls, filter_by: str, model_class, select_rel, allowed_keys: list | None = None):
        filters = cls.parse_filter_by(filter_by, allowed_keys)
        for field, values in filters.items():
            select_rel = cls.apply_filter_by_model_field(field, values, model_class, select_rel)
        return select_rel

    @classmethod
    async def get_instances_by_response(cls, session: AsyncSession, params, select_rel):
        _query = select_rel
        start = int(params.start) if params.start is not None else 0
        limit = int(params.limit) if params.limit is not None else None

        if start > 0:
            _query = _query.offset(start)
        if limit is not None and limit > 0:
            _query = _query.limit(limit)

        result = await session.execute(_query)
        return result.scalars().unique().all()

    @classmethod
    def make_response_by_data_of_zero(cls, params):
        return cls.get_data(
            data=[],
            status_code=200,
            meta={
                'total': 0,
                'counts': 0
            },
            fmt=params.response_fmt,
            is_download=bool(params.is_download)
        )

    @staticmethod
    def apply_filter_by_model_field(field: str, values: list, model_class, select_rel):
        mapper = inspect(model_class)
        if field not in mapper.attrs:
            return select_rel

        attr = getattr(model_class, field, None)
        sa_type = None
        column_expr = None

        if isinstance(attr, InstrumentedAttribute):
            column_expr = attr
            try:
                sa_type = getattr(attr.property.columns[0], "type", None)
            except Exception:
                sa_type = getattr(attr, "type", None)
        else:
            prop = mapper.attrs[field]
            if hasattr(prop, "columns") and prop.columns:
                column_expr = prop.columns[0]
                sa_type = getattr(column_expr, "type", None)
            else:
                return select_rel

        try:
            if isinstance(sa_type, Boolean) or getattr(sa_type, "python_type", None) is bool:
                truthy = {"true", "1", "yes", "y", "on", "t"}
                falsy = {"false", "0", "no", "n", "off", "f"}
                casted = []
                for v in values:
                    s = str(v).strip().lower()
                    if s in truthy: casted.append(True)
                    elif s in falsy: casted.append(False)
                if not casted:
                    return select_rel
                values = casted
            else:
                py_type = getattr(sa_type, "python_type", None)
                if py_type:
                    values = [py_type(v) for v in values]
        except (ValueError, TypeError):
            return select_rel

        return select_rel.where(column_expr.in_(values))

    @staticmethod
    async def get_count_by_select_rel(session: AsyncSession, select_rel, **kwargs) -> int:
        result = await session.execute(
            select(func.count()).select_from(select_rel.subquery())
        )
        count = result.scalar_one()
        return count

    @staticmethod
    def parse_filter_by(filter_string: str, allowed_keys: list | None = None) -> dict:
        if not filter_string:
            return {}

        result = {}
        for pair in filter_string.split(';'):
            if ':' not in pair:
                continue
            key, values = pair.split(':', 1)
            if allowed_keys:
                if key not in allowed_keys:
                    continue

            result[key.strip()] = [v.strip() for v in values.split(',') if v.strip()]
        return result
