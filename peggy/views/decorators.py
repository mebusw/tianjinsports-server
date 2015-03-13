from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from peggy.models import *


def staff_only(redirect_url=''):
    def real_decorator(fn):

        def wrapped(*args, **kwargs):
            user = args[0].user
            if not user.is_staff:
                return HttpResponseRedirect(reverse('peggy.views.bo_login_page'))
            else:
                return fn(*args, **kwargs)

        return wrapped

    return real_decorator
