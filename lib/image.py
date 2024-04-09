import base64
import logging

import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


def download_jpg_image(image_url, output_path):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as file:
                response.raw.decode_content = True
                file.write(response.raw.data)
            logging.info(f"Downloaded image to path: {output_path}")
        else:
            logging.error(f"Failed to download: {image_url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading to path: {output_path} due to {e}")


def download_base64_image(base64_data, file_name):
    _, encoded = base64_data.split(",", 1)
    data = base64.b64decode(encoded)
    with open(file_name, "wb") as file:
        file.write(data)
