from typing import Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont
import httpx
from io import BytesIO
import os
import asyncio
from Chino_old.plugins_parser import plugin_common
from Chino_old.model_definition import AnswerBase, AnswerBaseList
from Chino_old.standard_print import logger


class Pixivbiu(plugin_common):


    _version_ ='0.1'
    @classmethod
    async def main(cls,msg_l) -> AnswerBase | AnswerBaseList | None:
        qu=msg_l["qu"]
        if qu.find("&bpixiv") == 0:
            PIXIVBIU_BASE_URL="http://127.0.0.1:4001/"

            # 将qu以空格分割
            qu_split = qu.split(" ")
            if len(qu_split) < 2:
                return AnswerBase(answer="&bpixiv search|",send_way="Text")
            #如果第2项为search
            if qu_split[1] == "search":
                import json
                import requests
                params = {
                    'kt': None,
                    'mode': 'tag',
                    'totalPage': 1,
                    'groupIndex': 0,
                    'sortMode': 0,
                    'isSort': 0,
                    'isCache': 1
                }
                #params直接从qu_split[2]开始赋值（以=分割，前面为key，后面为value）
                for i in qu_split[2:]:
                    match i.split("=")[0]:
                        case "kt":
                            params["kt"] = i.split("=")[1]
                        case "mode":
                            params["mode"] = i.split("=")[1]
                        case "totalPage":
                            params["totalPage"] = i.split("=")[1]
                        case "groupIndex":
                            params["groupIndex"] = i.split("=")[1]
                        case "sortMode":
                            params["sortMode"] = i.split("=")[1]
                        case "isSort":
                            params["isSort"] = i.split("=")[1]
                        case "isCache":
                            params["isCache"] = i.split("=")[1]

                if params["kt"] is None or params["kt"] == "":
                    return AnswerBase(answer="请输入搜索关键词",send_way="Text")

                url = f'{PIXIVBIU_BASE_URL}api/biu/search/works/'
                try:
                    response = requests.get(url, params=params)
                except Exception as e:
                    return AnswerBase(answer=f"pixivbiu请求失败: {e}",send_way="Text")
                # 解析返回值
                if response.status_code == 200:
                    data = response.json()["msg"]["rst"]["data"]
                    i=1
                    req_list=[]
                    for x in data:
                        x_all=x["all"]
                        translated_tags=[]
                        for tags_tran in x_all["tags"]:
                            translated_tags.append(tags_tran["translated_name"])
                        req=f"""id: {x["id"]} title: {x["title"]}
total_bookmarked: {x["total_bookmarked"]} total_viewed: {x["total_viewed"]}
tags: {str(x["tags"])}
translated_tags: {str(translated_tags)}
page_count*width*height: {x_all["page_count"]}*{x_all["width"]}*{x_all["height"]}
author:
-id: {x["author"]["id"]}
-name: {x["author"]["name"]}
image_urls:
-small: {x["image_urls"]["small"]}
-medium: {x["image_urls"]["medium"]}
-large: {x["image_urls"]["large"]}
"""
                        image_url= x["image_urls"]["small"]
                        old_domain = 'https://i.pximg.net'
                        new_domain = 'https://i.pixiv.re'
                        image_url = image_url.replace(old_domain, new_domain)
                        req_list.append({"text": req,"image_url":image_url })
                    final_image_bool , final_image , err= await cls.text_and_image2one(req_list)
                    if final_image_bool  and final_image is not None:
                        final_image_bytes = BytesIO()
                        image_format = final_image.format
                        if image_format is None:
                            image_format = 'PNG'
                        final_image.save(final_image_bytes, format=image_format)
                        final_image_bytes.seek(0)


                        return AnswerBaseList(answers=[AnswerBase(answer={"BytesIO":  final_image_bytes.getvalue()},send_way="Image")])
                    elif final_image_bool is False:
                        return AnswerBase(answer=f"pixiv图像下载或解析失败: {err}",send_way="Text")
                    else:
                        return AnswerBase(answer="pixiv图像下载或解析失败",send_way="Text")
                else :
                    return AnswerBase(answer="pixivbiu获取失败: 状态码 "+str(response.status_code),send_way="Text")
                return




    @classmethod
    def calculate_max_text_width(cls, text: str, font: ImageFont.FreeTypeFont) -> float:
        """Calculate the maximum width of lines of text split by newline characters."""
        lines = text.split('\n')
        max_width = 0

        for line in lines:
            # Compute width of each line
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            max_width = max(max_width, line_width)

        return max_width

    @classmethod
    async def text_and_image2one(cls, data_list: List[dict], font_path=os.getenv('CHINO_FONT', 'font/NotoSansCJKtc-Regular.otf'), font_size=24) -> Tuple[bool, Optional[Image.Image], Optional[str]]:
        """Combine text and images side-by-side into a single composite image."""
        base_image_width = 800
        image_width = 400  # Fixed width for images
        image_height = 0
        images = []
        font = ImageFont.truetype(font_path, font_size)

        async with httpx.AsyncClient() as client:
            tasks = [cls.download_image(client, item['text'], item['image_url']) for item in data_list]
            results = await asyncio.gather(*tasks)

        # Find the maximum width of text lines to adjust the image width
        max_text_width = 0
        for success, Img, error, text in results:
            if not success or Img is None:
                return False, None, error

            text_width = cls.calculate_max_text_width(text, font)
            max_text_width = max(max_text_width, text_width)
            text_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in text.split('\n'))
            images.append((text, Img, text_width, text_height))
            image_height += max(text_height, Img.height) + 20

        # Increase the image width to accommodate the longest text line
        image_width = max(base_image_width, 400 + max_text_width)

        # Create a new image with the computed dimensions
        result_image = Image.new("RGB", (image_width, image_height), 'white') # type: ignore
        draw = ImageDraw.Draw(result_image)
        current_height = 0

        for text, img, text_width, text_height in images:
            # Draw text
            text_y = current_height
            for line in text.split('\n'):
                draw.text((10, text_y), line, fill="black", font=font)
                text_y += font.getbbox(line)[3] - font.getbbox(line)[1]

            # Paste image with boundary checks
            img_x = image_width - img.width - 10
            img_y = current_height + (max(text_height, img.height) - img.height) // 2

            # Ensure the image is within the bounds of the result_image
            if img_x + img.width > image_width:
                img_x = image_width - img.width
            if img_y + img.height > image_height:
                img_y = image_height - img.height

            result_image.paste(img, (img_x, img_y))
            current_height += max(text_height, img.height) + 20

        return True, result_image, None


    @staticmethod
    async def download_image(client: httpx.AsyncClient, text: str, image_url: str, retries: int = 3) -> Tuple[bool, Optional[Image.Image], Optional[str], str]:
        """
        下载图片并返回图像对象
        :param client: httpx.AsyncClient 实例
        :param text: 关联的文本
        :param image_url: 图像 URL
        :param retries: 最大重试次数
        :return: (成功标志, 图像对象或错误信息, 关联文本)
        """
        for attempt in range(retries):
            try:
                response = await client.get(image_url)
                response.raise_for_status()  # 确保请求成功
                img = Image.open(BytesIO(response.content))
                return True, img, None, text
            except httpx.RequestError as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return False, None, f"Image request failed: {e}", text
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return False, None, f"Failed to process image: {e}", text

        # 如果循环结束但仍未返回，说明所有重试都失败了
        return False, None, "All retry attempts failed", text

    # @staticmethod
    # def get_text_size_multiline(text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    #     """
    #     获取多行文本的宽度和高度
    #     :param text: 多行文本
    #     :param font: 字体对象
    #     :return: 文本的宽度和高度
    #     """
    #     dummy_image = Image.new('RGB', (1, 1))
    #     draw = ImageDraw.Draw(dummy_image)
    #     lines = text.split('\n')
    #     max_width = 0
    #     total_height = 0

    #     for line in lines:
    #         bbox = draw.textbbox((0, 0), line, font=font)
    #         width = bbox[2] - bbox[0]
    #         height = bbox[3] - bbox[1]

    #         max_width = max(max_width, width)
    #         total_height += height

    #     return max_width, total_height
    @staticmethod
    def help():
        return "&getTime to getTime"