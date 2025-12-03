import os
import json
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from utils import create_success_payload, create_failed_payload, send_slack_message

load_dotenv()

SLACK_WEBHOOK_URL_SUCCESS = os.getenv("SLACK_WEBHOOK_URL_SUCCESS")
SLACK_WEBHOOK_URL_ALL = os.getenv("SLACK_WEBHOOK_URL_ALL")


async def validate_product(product_data):
    url = product_data["product_url"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"접속 중... {url}")
        await page.goto(url)

        button = page.locator('li.final a:has-text("바로 구매하기")')
        is_visible = await button.is_visible()
        print("버튼 존재 여부:", is_visible)

        if is_visible:
            payload = create_success_payload(product_data)
            await send_slack_message(SLACK_WEBHOOK_URL_SUCCESS, payload)
            await send_slack_message(SLACK_WEBHOOK_URL_ALL, payload)
        else:
            payload = create_failed_payload(product_data)
            await send_slack_message(SLACK_WEBHOOK_URL_ALL, payload)

        await browser.close()


async def main():
    with open("product_list.json", "r") as f:
        product_list = json.load(f)

    tasks = [validate_product(product) for product in product_list]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
