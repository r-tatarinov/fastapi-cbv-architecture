from src.app.routes.utils import make_data_by_response


class MainRouterMIXIN:

    @classmethod
    def make_response_by_ok(cls):
        data: dict = {'ok': 'success'}
        result = cls.get_data(data)
        return result

    @classmethod
    def make_response_by_error_not_exists(cls):
        data: dict = {'error': 'Ресурс не найден'}
        result = cls.get_data(data, 400)
        return result

    @classmethod
    def make_response_by_error_already_exists(cls):
        data: dict = {'error': 'Ресурс уже существует'}
        result = cls.get_data(data, 400)
        return result

    @classmethod
    def make_response_by_format_file_error(cls, format_str: str):
        data: dict = {'error': f'Формат {format_str} не поддерживается'}
        result = cls.get_data(data, 400)
        return result

    @classmethod
    def make_response_by_auth_error(cls):
        data: dict = {'error': 'Ошибка аутентификации'}
        result = cls.get_data(data, 401)
        return result

    @classmethod
    def make_response_by_permission_error(cls):
        data: dict = {'error': 'Ошибка доступа'}
        result = cls.get_data(data, 400)
        return result

    @staticmethod
    @make_data_by_response
    def get_data(
        data: dict | list,
        status_code: int = 200,
        meta: dict | None = None,
        fmt: str = "json",
        is_download: bool = False
    ):
        return data, status_code, meta, fmt, is_download
