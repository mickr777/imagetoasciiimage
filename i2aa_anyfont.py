import os
import string
from typing import Literal, Optional

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    FieldDescriptions,
    Input,
    InputField,
    InvocationContext,
    invocation,
)
from invokeai.app.invocations.metadata import CoreMetadata
from invokeai.app.invocations.primitives import BoardField, ImageField, ImageOutput
from invokeai.app.models.image import ImageCategory, ResourceOrigin


def list_local_fonts() -> list:
    cache_dir = "font_cache"
    if not os.path.exists(cache_dir):
        return []
    fonts = [f for f in os.listdir(cache_dir) if f.lower().endswith((".ttf", ".otf"))]
    return sorted(fonts, key=lambda x: x.lower())


available_fonts = list_local_fonts()

if available_fonts:
    fonts_str = ", ".join([repr(f) for f in available_fonts])
    FontLiteral = eval(f'Literal["None", {fonts_str}]')
else:
    FontLiteral = Literal["None"]


COMPARISON_TYPES = Literal[
    "SAD",
    "MSE",
    "SSIM",
    "NAL",
]

COMPARISON_TYPE_LABELS = dict(
    SAD="Sum of Absolute Differences",
    MSE="Mean Squared Error",
    SSIM="Structural Similarity",
    NAL="Normalized Average Luminance",
)

CHAR_RANGES = Literal[
    "All",
    "Low",
    "High",
    "Ascii",
    "Numbers",
    "Letters",
    "Lowercase",
    "Uppercase",
    "Hex",
    "Punctuation",
    "Printable",
    "AH",
    "AM",
    "AL",
    "Blocks",
    "Binary",
    "Custom",
]

CHAR_RANGE_LABELS = dict(
    All="ALL chars 0-255",
    Low="Low chars 32-127",
    High="High chars 128-255",
    Ascii="ASCII chars 32-255",
    Numbers="Numbers: 0-9 + .",
    Letters="Letters: a-z + A-Z + space",
    Lowercase="Lowercase: a-z + space",
    Uppercase="Uppercase: A-Z + space",
    Hex="Hex: 0-9 + a-f + A-F",
    Punctuation="All Punctuation",
    Printable="Letters + Numbers + Punctuation + space",
    AH="AH: @$B%8WM#&*oahkbdpqwmZO0QLCJYXzcvunxrjft/\|()1{}[]?-+~<>i!lI;:,^'. ",
    AM="AM: @%#*+=-:. ",
    AL="AL: @#=-. ",
    Blocks="Blocks: []|-",
    Binary="Binary: 01",
    Custom="Custom: Chars entered in the custom field",
)

CHAR_SETS = {
    "All": [chr(i) for i in range(0, 255)],
    "Low": [chr(i) for i in range(32, 127)],
    "High": [chr(i) for i in range(128, 255)],
    "Ascii": [chr(i) for i in range(32, 255)],
    "Numbers": string.digits + ".",
    "Letters": string.ascii_letters + " ",
    "Lowercase": string.ascii_lowercase + " ",
    "Uppercase": string.ascii_uppercase + " ",
    "Hex": string.hexdigits,
    "Punctuation": string.punctuation,
    "Printable": string.digits + string.ascii_letters + string.punctuation + " ",
    "AH": "@$B%8WM#&*oahkbdpqwmZO0QLCJYXzcvunxrjft/\|()1{}[]?-+~<>i!lI;:,^'. ",
    "AM": "@%#*+=-:. ",
    "AL": "@#=-. ",
    "Blocks": "[]|-",
    "Binary": "01",
}


@invocation(
    "I2AA_AnyFont",
    title="Image to ASCII Art AnyFont",
    tags=["image", "ascii art"],
    category="image",
    version="0.2.0",
)
class ImageToAAInvocation(BaseInvocation):
    """Convert an Image to Ascii Art Image using any font or size
    https://github.com/dernyn/256/tree/master this is a great font to use"""

    input_image: ImageField = InputField(description="Image to convert to ASCII art")
    board: Optional[BoardField] = InputField(default=None, description=FieldDescriptions.board, input=Input.Direct)
    metadata: CoreMetadata = InputField(
        default=None,
        description=FieldDescriptions.core_metadata,
        ui_hidden=True,
    )
    font_url: Optional[str] = InputField(
        default="https://github.com/dernyn/256/raw/master/Dernyn's-256(baseline).ttf",
        description="URL address of the font file to download",
    )
    local_font_path: Optional[str] = InputField(description="Local font file path (overrides font_url)")
    local_font: Optional[FontLiteral] = InputField(
        default=None, description="Name of the local font file to use from the font_cache folder"
    )
    font_size: int = InputField(default=6, description="Font size for the ASCII art characters")
    character_range: CHAR_RANGES = InputField(
        default="Ascii",
        description="The character range to use",
        ui_choice_labels=CHAR_RANGE_LABELS,
    )
    custom_characters: str = InputField(
        default="▁▂▃▄▅▆▇█ ", description="Custom characters. Used if Custom is selected from character range"
    )
    comparison_type: COMPARISON_TYPES = InputField(
        default="NAL",
        description="Choose the comparison type (Sum of Absolute Differences, Mean Squared Error, Structural Similarity Index, Normalized Average Luminance)",
        ui_choice_labels=COMPARISON_TYPE_LABELS,
    )
    mono_comparison: bool = InputField(default=False, description="Convert input image to mono for comparison")
    color_mode: bool = InputField(default=False, description="Enable color mode (default: grayscale)")

    def download_font(self, font_url: str) -> str:
        font_filename = font_url.split("/")[-1]
        cache_dir = "font_cache"
        font_path = f"{cache_dir}/{font_filename}"

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if not os.path.isfile(font_path):
            print("\033[1;31mFont not found in cache, downloading...\033[0m")
            response = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        else:
            print("\033[1;32mFont found in cache, using cached version.\033[0m")

        return font_path

    def get_font_chars(self, font_path, font_size, chars):
        font = ImageFont.truetype(font_path, font_size)
        # chars = CHAR_SETS.get(char_range, [])
        char_images = {c: Image.new("L", (font_size, font_size)) for c in chars}
        for c, img in char_images.items():
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), c, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((font_size - w) / 2, (font_size - h) / 2), c, font=font, fill=255)
        return {c: np.array(img) for c, img in char_images.items()}

    def sad(self, img1, img2):
        return np.sum(np.abs(img1 - img2))

    def mse(self, img1, img2):
        err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
        err /= float(img1.shape[0] * img1.shape[1])
        return err

    def ssim(self, img1, img2, mu_img1, mu_img2, sigma_img1, sigma_img2):
        sigma_img12 = np.cov(img1.flatten(), img2.flatten())[0, 1]
        k1, k2, L = 0.01, 0.03, 255
        C1 = (k1 * L) ** 2
        C2 = (k2 * L) ** 2
        ssim = ((2 * mu_img1 * mu_img2 + C1) * (2 * sigma_img12 + C2)) / (
            (mu_img1**2 + mu_img2**2 + C1) * (sigma_img1 + sigma_img2 + C2)
        )
        return ssim

    def calculate_luminosities(self, char_images):
        luminosities = {c: np.mean(np.array(img)) for c, img in char_images.items()}

        # Normalize the luminosities to the range 0-255.
        min_luminosity = min(luminosities.values())
        max_luminosity = max(luminosities.values())
        for c in char_images.keys():
            luminosities[c] = 255 * (luminosities[c] - min_luminosity) / (max_luminosity - min_luminosity)

        return luminosities

    def convert_image_to_mosaic_weighted(
        self,
        input_image: Image.Image,
        font_path: str,
        font_size: int,
        color_mode: bool,
        comparison_method: str,
        char_range: str,
        mono_comparison: bool,
        custom_chars: str,
    ):
        if mono_comparison:
            l_image = input_image.convert("1").convert("L")  # grayscale for comparison
        else:
            l_image = input_image.convert("L")  # grayscale for comparison
        c_image = input_image.convert("RGB")  # full color for average color calculation

        # Check for custom char range selected
        chars = custom_chars if char_range == "Custom" else CHAR_SETS.get(char_range, [])

        char_images = self.get_font_chars(font_path, font_size, chars)  # get the char images for comparison
        if comparison_method == "SSIM":
            char_images_mean = {c: np.mean(img) for c, img in char_images.items()}
            char_images_variance = {c: np.var(img) for c, img in char_images.items()}
        else:
            char_images_mean = char_images_variance = None

        if comparison_method == "NAL":
            char_lumi = self.calculate_luminosities(char_images)
        else:
            char_lumi = None

        mosaic_img = Image.new("RGB" if color_mode else "L", input_image.size)  # create a color or grayscale output

        draw = ImageDraw.Draw(mosaic_img)
        for i in range(0, l_image.width, font_size):
            for j in range(0, l_image.height, font_size):
                box = (i, j, i + font_size, j + font_size)
                l_region = l_image.crop(box)
                l_region_array = np.array(l_region.resize((font_size, font_size)))

                # Calculate which char is the closest matching using selected method
                if comparison_method == "SAD":  # Sum of Absolute Differences (SAD).
                    comparisons = {c: self.sad(l_region_array, char_img) for c, char_img in char_images.items()}
                elif comparison_method == "MSE":  # Mean Squared Error (MSE)
                    comparisons = {c: self.mse(l_region_array, char_img) for c, char_img in char_images.items()}
                elif comparison_method == "SSIM":  # Structural Similarity (SSIM)
                    comparisons = {
                        c: -self.ssim(
                            l_region_array,
                            char_img,
                            np.mean(l_region_array),
                            char_images_mean[c],
                            np.var(l_region_array),
                            char_images_variance[c],
                        )
                        for c, char_img in char_images.items()
                    }
                elif comparison_method == "NAL":  # Average Luminance check
                    avg_luminosity = np.mean(l_region_array)
                    comparisons = {c: abs(avg_luminosity - char_lumi[c]) for c, char_img in char_images.items()}

                # Pick the char with the smallest difference.
                best_char = min(comparisons, key=comparisons.get)
                if color_mode:
                    c_region = c_image.crop(box)
                    c_region_array = np.array(c_region.resize((font_size, font_size)))
                    avg_color = tuple(np.mean(c_region_array, axis=(0, 1)).astype(int))
                else:
                    avg_color = 255

                # Draw the character image on the mosaic image.
                draw.text((i, j), best_char, font=ImageFont.truetype(font_path, font_size), fill=avg_color)
        # Save the mosaic image.
        return mosaic_img

    def invoke(self, context: InvocationContext) -> ImageOutput:
        input_image = context.services.images.get_pil_image(self.input_image.image_name)

        if self.local_font and self.local_font != "None":
            font_path = os.path.join("font_cache", self.local_font)
        elif self.local_font_path:
            font_path = self.local_font_path
        else:
            font_path = self.download_font(self.font_url)

        if not os.path.isfile(font_path):
            print("\033[1;31mFont file not found. Please check the font file path.\033[0m")
            return

        detailed_ascii_art_image = self.convert_image_to_mosaic_weighted(
            input_image,
            font_path,
            self.font_size,
            self.color_mode,
            self.comparison_type,
            self.character_range,
            self.mono_comparison,
            self.custom_characters,
        )
        image_dto = context.services.images.create(
            image=detailed_ascii_art_image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            board_id=self.board.board_id if self.board else None,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate,
            metadata=self.metadata.dict() if self.metadata else None,
            workflow=self.workflow,
        )

        return ImageOutput(
            image=ImageField(image_name=image_dto.image_name),
            width=image_dto.width,
            height=image_dto.height,
        )
