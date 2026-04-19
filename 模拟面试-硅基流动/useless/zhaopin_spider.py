import asyncio
from playwright.async_api import async_playwright
import json
import os
from datetime import datetime
from urllib.parse import urlencode

BASE_URL = "https://fe-api.zhaopin.com/c/i/search/positions"

FULL_COOKIE = "x-zp-client-id=79819efb-597a-4225-bd3c-84d29949649e; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkchannel=%7B%22prop%22%3A%7B%22_sa_channel_landing_url%22%3A%22%22%7D%7D; x-zp-device-sn=9cf7ae57f7754257b33c65f656c1ecf3; zp_passport_deepknow_sessionId=ca70c104s55e5145f1a7e8ca8d0759f6b21d; at=cce92c0e2c0b486fb85d58be6653e0ec; rt=0ec10d7bec814168b37c962f598f6bb8; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221248430377%22%2C%22first_id%22%3A%2219ba20c664da98-04c620ba8a14164-4c657b58-1821369-19ba20c664e1a2b%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E4%BB%98%E8%B4%B9%E5%B9%BF%E5%91%8A%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.bing.com%2F%22%2C%22%24latest_utm_source%22%3A%22bingsem_b%22%2C%22%24latest_utm_medium%22%3A%22ocpc%22%2C%22%24latest_utm_campaign%22%3A%22youju02%22%2C%22%24latest_utm_content%22%3A%22hy%22%2C%22%24latest_utm_term%22%3A%2220014629%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTliYTIwYzY2NGRhOTgtMDRjNjIwYmE4YTE0MTY0LTRjNjU3YjU4LTE4MjEzNjktMTliYTIwYzY2NGUxYTJiIiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTI0ODQzMDM3NyJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221248430377%22%7D%2C%22%24device_id%22%3A%2219ba20c664da98-04c620ba8a14164-4c657b58-1821369-19ba20c664e1a2b%22%7D; sts_deviceid=19ba20cfd67135c-0803592b77fd1f-4c657b58-1821369-19ba20cfd682c3b; ZP_OLD_FLAG=false; sts_sg=1; sts_chnlsid=Unknown; zp_src_url=https%3A%2F%2Flanding.zhaopin.com%2F; ZL_REPORT_GLOBAL={%22/resume/new%22:{%22actionid%22:%224cef7d1b-0528-4ee0-b46e-24eda39f3d09%22%2C%22funczone%22:%22addrsm_ok_rcm%22}}; LastCity=%E6%88%90%E9%83%BD; LastCity%5Fid=801; Hm_lvt_7fa4effa4233f03d11c7e2c710749600=1767952451; HMACCOUNT=F534429C6A45A2E7; locationInfo_search=%7B%22code%22%3A%22%22%7D; Hm_lpvt_7fa4effa4233f03d11c7e2c710749600=1767954780; selectCity_search=801"

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.zhaopin.com",
    "Referer": "https://www.zhaopin.com/",
    "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
    "x-zp-business-system": "1",
    "x-zp-page-code": "4019",
    "x-zp-platform": "13",
    "x-zp-client-id": "79819efb-597a-4225-bd3c-84d29949649e",
    "x-zp-page-request-id": "2627d78980d948968368a1afb43ee931-1767954777735-611398",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
}

URL_PARAMS = {
    "at": "cce92c0e2c0b486fb85d58be6653e0ec",
    "rt": "0ec10d7bec814168b37c962f598f6bb8",
    "_v": "0.92690194",
    "x-zp-page-request-id": "2627d78980d948968368a1afb43ee931-1767954777735-611398",
    "x-zp-client-id": "79819efb-597a-4225-bd3c-84d29949649e",
}


def generate_timestamp():
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")


def save_to_txt(data, position, page_index):
    timestamp = generate_timestamp()
    safe_position = "".join(
        c if c.isalnum() or c == "\u4e00" <= c <= "\u9fa5" else "_" for c in position
    )
    file_name = f"zhaopin_{safe_position}_page{page_index}_{timestamp}.txt"
    file_path = os.path.join(os.path.dirname(__file__), file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_name


async def search_positions(position, page_index=1, page_size=20):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()

        try:
            await context.add_cookies(
                [
                    {
                        "name": "x-zp-client-id",
                        "value": "79819efb-597a-4225-bd3c-84d29949649e",
                        "url": "https://www.zhaopin.com",
                    },
                    {
                        "name": "at",
                        "value": "cce92c0e2c0b486fb85d58be6653e0ec",
                        "url": "https://www.zhaopin.com",
                    },
                    {
                        "name": "rt",
                        "value": "0ec10d7bec814168b37c962f598f6bb8",
                        "url": "https://www.zhaopin.com",
                    },
                ]
            )

            payload = {
                "S_SOU_FULL_INDEX": position,
                "S_SOU_WORK_CITY": "801",
                "anonymous": 0,
                "cvNumber": "DB1E436F80C890CB4D597E4724320281D56997774095D28CC48453C3361C8CDA71B07C91202DD9D9DE1917E756B5A136_A0001",
                "eventScenario": "pcSearchedSouSearch",
                "order": 0,
                "pageIndex": page_index,
                "pageSize": page_size,
                "platform": 13,
                "resumeNumber": "DB1E436F80C890CB4D597E4724320281D56997774095D28CC48453C3361C8CDA71B07C91202DD9D9DE1917E756B5A136_A0001",
                "sortType": "DEFAULT",
                "version": "0.0.0",
            }

            full_url = f"{BASE_URL}?{urlencode(URL_PARAMS)}"

            response = await page.request.post(
                full_url, data=payload, headers=DEFAULT_HEADERS
            )

            if not response.ok:
                raise Exception(f"HTTP error! status: {response.status}")

            data = await response.json()

            result = {
                "success": True,
                "data": data,
                "meta": {
                    "position": position,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "status": response.status,
                },
            }

            file_name = save_to_txt(result, position, page_index)
            print(f"✅ 数据已保存到文件: {file_name}")

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "meta": {
                    "position": position,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                },
            }

            file_name = save_to_txt(error_result, position, page_index)
            print(f"❌ 错误信息已保存到文件: {file_name}")

            return error_result

        finally:
            await browser.close()


async def search_multiple_pages(position, page_size=20, max_pages=5):
    all_results = []

    for i in range(1, max_pages + 1):
        print(f"📄 正在爬取第 {i} 页...")

        result = await search_positions(position, i, page_size)

        if result["success"] and result["data"]["data"].get("list"):
            all_results.extend(result["data"]["data"]["list"])
            print(f"✅ 第 {i} 页爬取成功，获取 {len(result['data']['data']['list'])} 条数据")
        else:
            print(f"❌ 第 {i} 页爬取失败或无数据")
            if result["data"]["data"].get("statusDescription"):
                print(f"   原因: {result['data']['data']['statusDescription']}")
            break

        await asyncio.sleep(2)

    final_result = {
        "success": True,
        "totalResults": len(all_results),
        "data": all_results,
    }

    file_name = save_to_txt(final_result, position, f"1-{max_pages}")
    print(f"📁 批量爬取结果已保存到文件: {file_name}")

    return final_result


def main():
    import sys

    position = sys.argv[1] if len(sys.argv) > 1 else "java开发工程师"
    page_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    page_size = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    print("=" * 50)
    print("🎯 智联招聘爬虫启动")
    print("=" * 50)
    print(f"📌 搜索岗位: {position}")
    print(f"📄 页码: {page_index}, 条数: {page_size}")
    print("=" * 50)
    print("🚀 开始爬取...\n")

    result = asyncio.run(search_positions(position, page_index, page_size))

    print("\n" + "=" * 50)
    print("📊 爬取结果")
    print("=" * 50)
    print(f"✅ 成功: {result['success']}")
    print(
        f"📋 数据条数: {result['data']['data'].get('list', []) if result['success'] else 0}"
    )

    if result["data"]["data"].get("statusDescription"):
        print(f"📝 状态描述: {result['data']['data']['statusDescription']}")

    print("=" * 50)


if __name__ == "__main__":
    main()
