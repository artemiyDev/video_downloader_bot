from bs4 import BeautifulSoup as bs

from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
iphone = playwright.devices["iPhone 11 Pro"]
browser = playwright.chromium.launch(headless=False)
context = browser.new_context(**iphone)
page = context.new_page()

excluded_resource_types = ["stylesheet", "script", "image", "font"]


def block_aggressively(route):
    if (route.request.resource_type in excluded_resource_types):
        route.abort()
    else:
        route.continue_()


page.route("**/*", block_aggressively)

page.goto('https://www.tiktok.com/@saan_taan/video/7174056351860149506?is_from_webapp=1&sender_device=pc')
page.wait_for_selector('//video')
soup = bs(page.content(), 'lxml')
video = soup.find('video')
browser.close()
print(video)
