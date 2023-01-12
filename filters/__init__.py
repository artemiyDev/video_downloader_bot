from .users_filters import IsSubscriber


def setup(dp):
    dp.filters_factory.bind(IsSubscriber)
