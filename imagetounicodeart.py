import os
import requests
from typing import Literal
from PIL import Image, ImageDraw, ImageFont
from invokeai.invocation_api import (
    BaseInvocation,
    InvocationContext,
    invocation,
    InputField,
    ImageField, 
    ImageOutput,
)

font_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font_cache")
os.makedirs(font_cache_dir, exist_ok=True)
FONT_PATH = os.path.join(font_cache_dir, "DejaVuSansMono.ttf")

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
    version="1.4.0",
    use_cache=False,
)
class ImageToUnicodeArtInvocation(BaseInvocation):
    """Convert an Image to Unicode Art using Extended Characters"""

    input_image: ImageField = InputField(
        description="Input image to convert to Unicode art"
    )
    font_size: int = InputField(
        default=8, description="Font size for the Unicode art characters"
    )
    gamma: float = InputField(
        default=1.0, description="Gamma correction value for the output image"
    )
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
    ] = InputField(
        default="Shaded", description="Use shaded Unicode characters for artwork"
    )
    color_mode: bool = InputField(
        default=True, description="Enable color mode (default: grayscale)"
    )
    invert_colors: bool = InputField(
        default=True, description="Invert background color and ASCII character order"
    )

    def get_unicode_chars(self):
        char_set = {
            "Shaded": "█▓▒░ ",
            "Extended Shading": "█▇▆▅▄▃▂▁▀",
            "Intermediate Detail": "◼◐○□ ",
            "Checkerboard Patterns": "▝▜▛▚▙▘▗▖ ",
            "Vertical Lines": "┋┊┇┆┃│ ",
            "Horizontal Lines": "┉┈┅┄━─ ",
            "Diagonal Lines": "╱╳╲ ",
            "Arrows": "↙↘↗↖↕↔↓→↑← ",
            "Circles": "◑◐◕◔○● ",
            "Blocks": "▁▂▃▄▅▆▇█ ",
            "Triangles": "▷◁◶▷▽▼△▲ ",
            "Math Symbols": "∓±÷×−+ ",
            "Stars": "✬✫✪✩✧✦☆★ ",
        }
        return (
            char_set[self.unicode_set]
            if not self.invert_colors
            else char_set[self.unicode_set][::-1]
        )

    def image_to_unicode_art(
        self, input_image: Image.Image, font_size: int, color_mode: bool
    ) -> Image.Image:
        def adjust_gamma(image, gamma=1.0):
            invGamma = 1.0 / gamma
            table = [((i / 255.0) ** invGamma) * 255 for i in range(256)]
            if image.mode == "L":
                return image.point(table)
            elif image.mode == "RGB":
                return image.point(table * 3)

        input_image = adjust_gamma(input_image, gamma=self.gamma)

        if not os.path.exists(FONT_PATH):
            font_url = (
                "https://candyfonts.com/wp-data/2021/05/09/122551/DejaVuSansMono.ttf"
            )
            download_font(font_url, FONT_PATH)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception as e:
            print("Error loading font:", e)
            raise e

        ascii_chars = self.get_unicode_chars()

        if color_mode:
            ascii_art_image = Image.new(
                "RGB",
                input_image.size,
                (0, 0, 0) if self.invert_colors else (255, 255, 255),
            )
        else:
            ascii_art_image = Image.new(
                "L", input_image.size, 0 if self.invert_colors else 255
            )

        draw = ImageDraw.Draw(ascii_art_image)

        num_cols = input_image.width // font_size
        num_rows = input_image.height // font_size

        for y in range(num_rows):
            for x in range(num_cols):
                pixel_value = input_image.getpixel((x * font_size, y * font_size))
                if isinstance(pixel_value, tuple):
                    pixel_value = pixel_value[0]

                pixel_value = max(0, min(pixel_value, 255))

                ascii_index = int(pixel_value * (len(ascii_chars) - 1) / 255)
                ascii_char = ascii_chars[ascii_index]

                if color_mode:
                    color = input_image.getpixel((x * font_size, y * font_size))
                    draw.text(
                        (x * font_size, y * font_size),
                        ascii_char,
                        fill=color,
                        font=font,
                    )
                else:
                    font_color = 255 if self.invert_colors else 0
                    draw.text(
                        (x * font_size, y * font_size),
                        ascii_char,
                        fill=font_color,
                        font=font,
                    )

        return ascii_art_image

    def invoke(self, context: InvocationContext) -> ImageOutput:
        input_image = context.images.get_pil(self.input_image.image_name)
        shaded_ascii_art_image = self.image_to_unicode_art(
            input_image, self.font_size, self.color_mode
        )

        image_dto = context.images.save(image=shaded_ascii_art_image)

        return ImageOutput.build(image_dto)
