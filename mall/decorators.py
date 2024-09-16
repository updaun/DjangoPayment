import functools
from django.http import HttpRequest, HttpResponseForbidden


def deny_from_untrusted_hosts(allowed_ip_list):
    def get_client_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip

    def decorator(view_function):
        @functools.wraps(view_function)
        def _wrapped_view(request, *args, **kwargs):
            ip = get_client_ip(request)
            if ip not in allowed_ip_list:
                return HttpResponseForbidden("허용되지 않은 IP에서의 요청입니다.")
            return view_function(request, *args, **kwargs)

        return _wrapped_view

    return decorator
