from abc import abstractclassmethod, abstractstaticmethod


class AbstractBaseRouter:

    @abstractclassmethod
    async def get_response_by_select_rel(
        cls,
        session,
        params,
        select_rel
    ):
        pass

    @abstractstaticmethod
    def set_order_by(order_by, select_rel):
        pass

    @abstractstaticmethod
    async def get_data_by_response(session, ids, params):
        pass

    @abstractstaticmethod
    def get_data(
        data: dict | list,
        status_code: int = 200,
        meta: dict | None = None,
        fmt: str = "json",
        is_download: bool = False
    ):
        pass
