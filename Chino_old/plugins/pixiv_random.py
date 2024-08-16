import os
import httpx
import asyncio
from Chino_old.plugins_parser import plugin_common
from Chino_old.model_definition import AnswerBase, AnswerBaseList
from file_action import config_read

class pixiv_random(plugin_common):


    _version_ ='0.1'
    @classmethod
    async def main(cls,msg_l) -> AnswerBase | AnswerBaseList | None:
        qu=msg_l["qu"]
        if qu.find("&pixiv") == 0 or qu.find("&pixiv ") == 0:
            # API Endpoint
            url = "https://image.anosu.top/pixiv/json"

            params = {
                "num": 1,
                "r18": 0,
                "size": "original",
                "keyword": "",  # Example keyword
                "proxy": "i.pixiv.re",  # Assuming random proxy selection from the API
                "db": 0
            }
            #通过空格切割qu
            qu_l=qu.split(" ")
            #遍历每一项,当中找到keyword=,r18=,size=,proxy=,db=
            #除去第一项
            for i in qu_l[1:]:
                match i.split("=")[0]:
                    case "proxy":
                        params["proxy"] = i.split("=")[1]
                    case "keyword":
                        params["keyword"] = i.split("=")[1]
                    case "r18":
                        params["r18"] = i.split("=")[1]
                        if params["r18"] == "1":
                            params["r18"] = 1
                        else:
                            params["r18"] = 0
                    case "size":
                        params["size"] = i.split("=")[1]
                    case "db":
                        params["db"] = i.split("=")[1]
                    case "num":
                        params["num"] = i.split("=")[1]
                    case _:
                        pass


            async def fetch_images():
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        return data
                    else:
                        print(f"Failed to fetch images: HTTP {response.status_code}")
                        return None

            def process_image_data(image_data):
                # Print basic info and image URL
                an=f"""Title: {image_data['title']}, by {image_data['user']}\n
                Image URL: {image_data['url']}\n
                Image Dimensions: {image_data['width']}x{image_data['height']}\n
                Tags: {", ".join(image_data['tags'])}
                """
                return an

            var404="404Notfound"
            #下载图片到缓存文件夹.../upload/pixiv_cache.png
            async def download_image(url):
                return False
                #获取当前脚本的绝对路径
                current_script_path = os.path.abspath(__file__)
                grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))
                target_file_path = os.path.join(grandparent_dir, 'upload',"pixiv_cache.png")
                print(target_file_path)
                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                timeout = httpx.Timeout(read=60 * 1)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(url)
                    if response.status_code == 200:
                        with open(target_file_path, "wb") as f:
                            f.write(response.content)
                        return True
                    if response.status_code == 404:
                        return var404
                    else:
                        print(f"Failed to download image: HTTP {response.status_code}")
                        return False
            async def image_status(url):
                response = httpx.head(url)
                return response.status_code

            async def main():
                config=config_read()
                upload_file=f"http://{config.upload.host}:{config.upload.port}/upload/pixiv_cache.png"
                answerlist=[]
                images = await fetch_images()
                if images:
                    # Assuming the API wraps the list of images in a 'data' key
                    for item in images:
                        st=await image_status(item['url'])
                        if st == 200:
                            answerlist.append(AnswerBase(answer=process_image_data(item)))
                            answerlist.append(AnswerBase(answer=item['url'],send_way="Image"))
                        if st == 404:
                            answerlist.append(AnswerBase(answer="404NF!"))
                            continue
                else:
                    answerlist.append(AnswerBase(answer="Error in api"))
                return answerlist

            # Run the main function
            return AnswerBaseList(answers=await main())

    @staticmethod
    def help():
        return """&pixiv [keyword=] [r18=0] [size=original] [db=0] [num=1] [proxy=i.pixiv.re] (From https://image.anosu.top/)"""