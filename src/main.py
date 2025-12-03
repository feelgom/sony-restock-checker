import os
import json
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from utils import create_success_payload, create_failed_payload, send_slack_message

load_dotenv()

SLACK_WEBHOOK_URL_SUCCESS = os.getenv("SLACK_WEBHOOK_URL_SUCCESS")
SLACK_WEBHOOK_URL_ALL = os.getenv("SLACK_WEBHOOK_URL_ALL")


async def route_intercept(route, request):
    if request.resource_type in ["image", "font", "stylesheet"]:
        await route.abort()
    else:
        await route.continue_()


async def validate_product(product_data, context):
    url = product_data["product_url"]
    page = await context.new_page()

    try:
        print(f"접속 중... {url}")
        await page.goto(url, wait_until="domcontentloaded")

        button = page.locator('li.final a:has-text("바로 구매하기")')
        is_visible = await button.is_visible()
        print(f"[{url}] 버튼 존재 여부:", is_visible)

        if is_visible:
            payload = create_success_payload(product_data)
            await send_slack_message(SLACK_WEBHOOK_URL_SUCCESS, payload)
            await send_slack_message(SLACK_WEBHOOK_URL_ALL, payload)
        else:
            payload = create_failed_payload(product_data)
            await send_slack_message(SLACK_WEBHOOK_URL_ALL, payload)

    except Exception as e:
        print(f"[{url}] 에러 발생: {e}")
        payload = create_failed_payload(product_data)
        await send_slack_message(SLACK_WEBHOOK_URL_ALL, payload)

    finally:
        await page.close()


async def main():
    with open("product_list.json", "r") as f:
        product_list = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        await context.route("**/*", route_intercept)

        tasks = [validate_product(product, context) for product in product_list]
        await asyncio.gather(*tasks)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
