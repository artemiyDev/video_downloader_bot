import instaloader
from data import config


InstaLoaderObjProxy = instaloader.Instaloader(proxy={'https': config.proxy})
