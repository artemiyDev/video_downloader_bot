from bs4 import BeautifulSoup as bs

from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
iphone = playwright.devices["iPhone 11 Pro"]
proxy_server = 'http://gw.mobileproxy.space:1007'
proxy_login = '3er8FA'
proxy_pass = '1EFbEw9NAT1f'
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


# page.route("**/*", block_aggressively)

# def handle_request(request):
#     print(request)
#     if 'https://www.tiktok.com/api/related/item_list' in request.url:
#         print(request)
#
# page.on("request", handle_request)

page.goto('https://www.tiktok.com/@saan_taan/video/7174056351860149506')
page.wait_for_selector('//video')
soup = bs(page.content(), 'lxml')
video = soup.find('video')
browser.close()
print(video)
