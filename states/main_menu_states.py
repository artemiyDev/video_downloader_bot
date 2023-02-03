from aiogram.dispatcher.filters.state import StatesGroup, State


class PostDownloadStates(StatesGroup):
    S1 = State()


class MailingStates(StatesGroup):
    S1 = State()


class SubsListChangeStateRuEng(StatesGroup):
    S1 = State()


class SubsListChangeStateOthers(StatesGroup):
    S1 = State()
