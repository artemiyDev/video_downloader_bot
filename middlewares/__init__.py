from .throttling import ThrottlingMiddleware
from .update_user_status import UpdateUserInfo


def setup(dp):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(UpdateUserInfo())
