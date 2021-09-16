from typing import Tuple
import requests
import json
from uuid import uuid4
from PIL import Image
from hashlib import sha256
from io import BytesIO
from Crypto.Cipher import ChaCha20

class CSPTechException(Exception):
    pass

class CSPTechAPI():
    client: requests.Session
    api_data: dict

    def __gen_file(self, data: bytes) -> Tuple[str, BytesIO, str]:
        return (
            str(uuid4()) + "_0",
            BytesIO(data),
            "application/octet-stream"
        )

    def __prep_image(self, data: bytes, type: str, key: str) -> Tuple[dict, dict]:
        s = sha256()
        s.update(f'{len(data):08X}{self.api_data[type][key]}'.encode("ascii"))

        img = Image.open(BytesIO(data))
        if type == "licapi" and img.size[0] > 1024:
            raise Exception("Images for colorizing can only have max 1024px width")

        fdata = {
            "original-width": img.size[0],
            "original-height": img.size[1],
            "hash": s.hexdigest()
        }
        img.close()
        return fdata, {
            "image": self.__gen_file(data)
        }

    def __post_image(self, api: str, data: dict, files: dict) -> bytes:
        r = self.client.post(self.api_data[api]["api"], data=data, files=files)
        r.raise_for_status()

        status = r.content[:12].decode("ascii")
        if status[:4] == "err ": # Error
            raise CSPTechException(status + "\n" + r.content[12:].decode("utf-8"))
        assert status[:4] == "succ" # Success!

        return r.content[12:]

    def remove_tones(self, png_data: bytes) -> bytes:
        '''
        Remove screentones from an image.
        https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_edit_cleartone.htm#XREF_72770
        '''
        data, files = self.__prep_image(png_data, "srapi", "key-general")
        data["model"] = "general"
        return self.__post_image("srapi", data, files)

    def grayscale_tones(self, png_data: bytes) -> bytes:
        '''
        Smooth over the screentones in grayscale.
        https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_edit_cleartone.htm#XREF_67441
        '''
        data, files = self.__prep_image(png_data, "srapi", "key-gray")
        data["model"] = "general-gray"
        return self.__post_image("srapi", data, files)

    def pose(self, png_data: bytes) -> bytes:
        '''
        Convert images of humans in poses to 3D poses.
        Uses a proprietary binary "Bone Layout" format that hasn't been reverse-engineered
        https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_file_read_posephoto.htm
        '''
        data, files = self.__prep_image(png_data, "poseapi", "key")
        data["est2d"] = "tfpose" # Other unused & unavailable options seems to be: openpose, posenet
        return self.__post_image("poseapi", data, files)

    def colorize(self, image_data: bytes, hint_data: bytes = None) -> bytes:
        '''
        Colorize images, using an optional color hint image.
        Only seems to accept up to 1024px width images.
        https://www.clip-studio.com/site/gd_en/csp/userguide/csp_userguide/500_menu/500_menu_edit_autocolor.htm
        '''
        data, files = self.__prep_image(image_data, "licapi", "key")
        if hint_data:
            files["hint"] = self.__gen_file(hint_data)
        print(data, files)
        return self.__post_image("licapi", data, files)

    def __init__(self) -> None:
        with open("data.bin", "rb") as f:
            # Don't expose this data in plaintext format!
            alg = ChaCha20.new(key="dontdecryptthis!secretforareason".encode("ascii"), nonce=f.read(8))
            self.api_data = json.loads(alg.decrypt(f.read()))

        self.client = requests.Session()
        self.client.headers.update({
            "Cache-Control": "no-cache",
            "User-Agent": self.api_data["UA"]
        })