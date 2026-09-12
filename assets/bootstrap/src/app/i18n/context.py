from contextvars import ContextVar


SUPPORTED_LANGUAGES = {"ru", "en", "ar", "zh", "kk"}
DEFAULT_LANGUAGE = "ru"

_current_language: ContextVar[str] = ContextVar("current_language", default=DEFAULT_LANGUAGE)
_requested_language: ContextVar[str] = ContextVar("requested_language", default=DEFAULT_LANGUAGE)
_fallback_used: ContextVar[bool] = ContextVar("fallback_used", default=False)


def normalize_language(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LANGUAGE

    normalized = lang.strip().lower()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized

    return DEFAULT_LANGUAGE


def set_current_language(lang: str | None):
    _fallback_used.set(False)
    requested = (lang or DEFAULT_LANGUAGE).strip().lower()
    resolved = normalize_language(lang)
    if requested != resolved:
        _fallback_used.set(True)
    _requested_language.set(requested)
    return _current_language.set(resolved)


def reset_current_language(token) -> None:
    _current_language.reset(token)


def get_current_language() -> str:
    return _current_language.get()


def mark_fallback_used() -> None:
    _fallback_used.set(True)


def get_i18n_meta() -> dict:
    return {
        "requested_lang": _requested_language.get(),
        "resolved_lang": _current_language.get(),
        "fallback_used": _fallback_used.get(),
    }
