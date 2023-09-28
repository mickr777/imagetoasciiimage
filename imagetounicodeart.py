import os
import requests
from typing import Literal, Optional
from PIL import Image, ImageDraw, ImageFont
from invokeai.app.invocations.baseinvocation import BaseInvocation, Input, InvocationContext, invocation, InputField
from invokeai.app.invocations.primitives import ImageField, ImageOutput, BoardField
from invokeai.app.models.image import ImageCategory, ResourceOrigin

FONT_PATH = "font_cache/DejaVuSansMono.ttf"


def download_font(url: str, save_path: str) -> None:
    font_directory = os.path.dirname(FONT_PATH)
    if not os.path.exists(font_directory):
        os.makedirs(font_directory)

    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(save_path, "wb") as font_file:
        for chunk in response.iter_content(chunk_size=8192):
            font_file.write(chunk)


@invocation(
    "Image_to_Unicode_Art",
    title="Image to Unicode Art",
    tags=["image", "unicode art", "shading"],
    category="image",
    version="0.2.0",
)
class ImageToUnicodeArtInvocation(BaseInvocation):
    """Convert an Image to Unicode Art using Extended Characters"""

    input_image: ImageField = InputField(
        description="Input image to convert to Unicode art")
    font_size: int = InputField(
        default=8, description="Font size for the Unicode art characters")
    gamma: float = InputField(
        default=1.0, description="Gamma correction value for the output image")
    unicode_set: Literal[
        "Shaded",
        "Extended Shading",
        "Intermediate Detail",
        "Checkerboard Patterns",
        "Vertical Lines",
        "Horizontal Lines",
        "Diagonal Lines",
        "Arrows",
        "Circles",
        "Blocks",
        "Triangles",
        "Math Symbols",
        "Stars",
    ] = InputField(default="Shaded", description="Use shaded Unicode characters for artwork")
    color_mode: bool = InputField(
        default=False, description="Enable color mode (default: grayscale)")
    board: Optional[BoardField] = InputField(
        default=None, description="Pick Board to add output too", input=Input.Direct
    )

    def get_unicode_chars(self):
        sets = {
            "Shaded": " ░▒▓█",
            "Extended Shading": " ▁▂▃▄▅▆▇█",
            "Intermediate Detail": " □○◐◼",
            "Checkerboard Patterns": " ▖▗▘▙▚▛▜▝",
            "Vertical Lines": " │┃┆┇┊┋",
            "Horizontal Lines": " ─━┄┅┈┉",
            "Diagonal Lines": " ╲╳╱",
            "Arrows": " ←↑→↓↔↕↖↗↘↙",
            "Circles": " ●○◔◕◐◑",
            "Blocks": " █▇▆▅▄▃▂▁",
            "Triangles": " ▲△▼▽◀▶◁▷",
            "Math Symbols": " +−×÷±∓",
            "Stars": " ★☆✦✧✩✪✫✬",
        }
        return sets[self.unicode_set]

    def image_to_unicode_art(self, input_image: Image.Image, font_size: int, color_mode: bool) -> Image.Image:

        def adjust_gamma(image, gamma=1.0):
            invGamma = 1.0 / gamma
            table = [((i / 255.0) ** invGamma) * 255 for i in range(256)]
            if image.mode == "L":
                return image.point(table)
            elif image.mode == "RGB":
                return image.point(table * 3)

        input_image = adjust_gamma(input_image, gamma=self.gamma)

        if not os.path.exists(FONT_PATH):
            font_url = "https://candyfonts.com/wp-data/2021/05/09/122551/DejaVuSansMono.ttf"
            download_font(font_url, FONT_PATH)
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception as e:
            print("Error loading font:", e)
            raise e

        ascii_chars = self.get_unicode_chars()

        if color_mode:
            ascii_art_image = Image.new("RGB", input_image.size, (0, 0, 0))
        else:
            ascii_art_image = Image.new("L", input_image.size, 0)

        draw = ImageDraw.Draw(ascii_art_image)

        num_cols = input_image.width // font_size
        num_rows = input_image.height // font_size

        for y in range(num_rows):
            for x in range(num_cols):
                pixel_value = input_image.getpixel(
                    (x * font_size, y * font_size))
                if isinstance(pixel_value, tuple):
                    pixel_value = pixel_value[0]

                pixel_value = max(0, min(pixel_value, 255))

                ascii_index = int(pixel_value * (len(ascii_chars) - 1) / 255)
                ascii_char = ascii_chars[ascii_index]

                if color_mode:
                    color = input_image.getpixel(
                        (x * font_size, y * font_size))
                    draw.text((x * font_size, y * font_size),
                              ascii_char, fill=color, font=font)
                else:
                    draw.text((x * font_size, y * font_size),
                              ascii_char, fill=255, font=font)

        return ascii_art_image

    def invoke(self, context: InvocationContext) -> ImageOutput:
        input_image = context.services.images.get_pil_image(
            self.input_image.image_name)
        shaded_ascii_art_image = self.image_to_unicode_art(
            input_image, self.font_size, self.color_mode)

        mask_dto = context.services.images.create(
            image=shaded_ascii_art_image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            board_id=self.board.board_id if self.board else None,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate,
            workflow=self.workflow,
        )

        return ImageOutput(
            image=ImageField(image_name=mask_dto.image_name),
            width=mask_dto.width,
            height=mask_dto.height,
        )
