import aiohttp


def create_success_payload(product_data):
    product_name = product_data["product_name"]
    product_url = product_data["product_url"]
    price = product_data["price"]
    image_url = product_data["image_url"]

    payload = {
        "text": f"📸 {product_name} 재입고 안내 - 드디어 재입고되었습니다! 가격: {price}",
        "attachments": [
            {
                "color": "#36C5F0",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"📸 {product_name} 재입고 안내",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "*✨ 드디어 재입고되었습니다!*\n"
                                f"고객님이 기다리시던 *{product_name}* 가 "
                                "다시 구매 가능해졌습니다.\n\n"
                                "아래 버튼을 눌러 빠르게 확인해보세요. "
                            ),
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": image_url,
                            "alt_text": product_name,
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*가격*\n{price}"},
                            {"type": "mrkdwn", "text": "*상태*\n✔️ 재고 확보"},
                        ],
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "📦 구매 페이지 열기",
                                    "emoji": True,
                                },
                                "style": "primary",
                                "url": product_url,
                            },
                        ],
                    },
                ],
            }
        ]
    }

    return payload


def create_failed_payload(product_data):
    product_name = product_data["product_name"]
    image_url = product_data["image_url"]
    product_url = product_data["product_url"]

    payload = {
        "text": f"⚠️ {product_name} 아직 품절 상태입니다 - 계속 모니터링 중입니다.",
        "attachments": [
            {
                "color": "#FFA500",  # 주의/품절 안내용 강조 색상
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"⚠️ {product_name} 아직 품절 상태입니다",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*{product_name}* 은(는) 현재도 여전히 *품절 상태*입니다.\n"
                                "입고 여부를 계속 확인하고 있으며, 재입고 시 즉시 알려드릴게요.\n"
                            ),
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": image_url,
                            "alt_text": product_name,
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "🔎 상품 페이지 열기",
                                    "emoji": True,
                                },
                                "url": product_url,
                            }
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "⏳ 재입고 주기는 불규칙할 수 있습니다. 계속 모니터링 중입니다!",
                            }
                        ],
                    },
                ],
            }
        ]
    }

    return payload


async def send_slack_message(webhook_url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload) as response:
            text = await response.text()
            if response.status != 200:
                raise Exception(f"Slack 전송 실패: {response.status}, {text}")
            print("Slack 전송 성공:", text)
