from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright
from celery import Celery

app = Celery('tasks', broker='amqp://user:QwertyUI@84.46.245.185:5672/myvhost', backend='redis://84.46.245.185:6379/0')


@app.task
def get_tiktok_video_url(tik_tok_url, proxy_server, proxy_login, proxy_pass):
    playwright = sync_playwright().start()
    iphone = playwright.devices["iPhone 11 Pro"]
    browser = playwright.chromium.launch(headless=True, proxy={
        "server": proxy_server,
        "username": proxy_login,
        "password": proxy_pass
    })
    context = browser.new_context(**iphone)
    page = context.new_page()

    excluded_resource_types = ["stylesheet", "script", "image", "font"]

    def block_aggressively(route):
        if (route.request.resource_type in excluded_resource_types):
            route.abort()
        else:
            route.continue_()

    page.route("**/*", block_aggressively)

    page.goto(tik_tok_url)
    page.wait_for_selector('//video', timeout=5000)
    soup = bs(page.content(), 'lxml')
    video = soup.find('video').get('src')
    browser.close()
    playwright.stop()
    return video
