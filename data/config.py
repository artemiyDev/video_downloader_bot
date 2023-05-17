from itertools import cycle
from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
DEVELOPER = env.list("DEVELOPER")

# POSTGRES DB
PGUSER = env.str("PGUSER")
PGPASSWORD = env.str("PGPASSWORD")
ip = env.str("ip")

# referrals
subscription_check = True
referrals_enabled = False
chanel_for_subs_ru_eng = ''
chanel_for_subs_others = ''

# proxy
TIKTOK_PROXY_LIST = cycle(env.list('PROXY_LIST'))
PINTEREST_PROXY_LIST = cycle(env.list('PROXY_LIST'))
INSTAGRAM_PROXY_LIST = cycle(env.list('PROXY_LIST'))
proxy = env.str("PROXY")
proxy_change_url = env.str("PROXY_CHANGE_URL")
failed_connection_attempts = 0
changing_proxy = False

# test
if env.str("TEST").lower() == 'true':
    test = True
else:
    test = False
