import os
from typing import Literal
from PIL import Image, ImageDraw, ImageFont
from invokeai.app.invocations.baseinvocation import BaseInvocation, InvocationContext, invocation, InputField
from invokeai.app.invocations.primitives import ImageField, ImageOutput
from invokeai.app.models.image import ImageCategory, ResourceOrigin


@invocation(
    "Image_to_ASCII_Art_Image",
    title="Image to ASCII Art Image",
    tags=["image", "ascii art"],
    category="image",
    version="0.6.0",
)
class ImageToDetailedASCIIArtInvocation(BaseInvocation):
    """Convert an Image to Ascii Art Image"""
    input_image: ImageField = InputField(
        description="Input image to convert to ASCII art")
    font_spacing: int = InputField(
        default=6, description="Font size for the ASCII art characters")
    ascii_set: Literal["High Detail", "Medium Detail", "Low Detail", "Other", "Blocks", "Binary"] = InputField(
        default="Medium Detail",
        description="Choose the desired ASCII character set"
    )
    color_mode: bool = InputField(
        default=False, description="Enable color mode (default: grayscale)")
    output_to_file: bool = InputField(
        default=False, description="Output ASCII art to a text file")

    def get_ascii_chars(self):
        sets = {
            "High Detail": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\\^`'. ",
            "Medium Detail": "@%#*+=-:. ",
            "Low Detail": "@#=-. ",
            "Other": " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@",
            "Blocks": "[]|-",
            "Binary": "01"
        }
        return sets[self.ascii_set]

    def image_to_detailed_ascii_art(self, input_image: Image.Image, font_spacing: int, color_mode: bool) -> Image.Image:
        ascii_chars = self.get_ascii_chars()

        if color_mode:
            ascii_art_image = Image.new(
                "RGB", input_image.size, (255, 255, 255))
        else:
            ascii_art_image = Image.new("L", input_image.size, 255)

        draw = ImageDraw.Draw(ascii_art_image)

        num_cols = input_image.width // font_spacing
        num_rows = input_image.height // font_spacing

        for y in range(num_rows):
            for x in range(num_cols):
                pixel_value = input_image.getpixel(
                    (x * font_spacing, y * font_spacing))
                if isinstance(pixel_value, tuple):
                    pixel_value = pixel_value[0]

                pixel_value = max(0, min(pixel_value, 255))

                if self.ascii_set == "Binary":
                    ascii_index = 0 if pixel_value < 127.5 else 1
                else:
                    ascii_index = int(pixel_value * (len(ascii_chars) - 1) / 255)
                    
                ascii_char = ascii_chars[ascii_index]

                if color_mode:
                    color = input_image.getpixel(
                        (x * font_spacing, y * font_spacing))
                    draw.text((x * font_spacing, y * font_spacing),
                              ascii_char, fill=color)
                else:
                    draw.text((x * font_spacing, y * font_spacing),
                              ascii_char, fill=0)

        return ascii_art_image

    def image_to_ascii_string(self, input_image: Image.Image, font_spacing: int) -> str:
        ascii_chars = self.get_ascii_chars()

        ascii_str = ""
        font_aspect_ratio = 2

        num_cols = input_image.width // font_spacing
        num_rows = input_image.height // (font_spacing * font_aspect_ratio)

        for y in range(num_rows):
            for x in range(num_cols):
                pixel_value = input_image.getpixel(
                    (x * font_spacing, y * font_spacing * font_aspect_ratio))
                if isinstance(pixel_value, tuple):
                    pixel_value = pixel_value[0]
                pixel_value = max(0, min(pixel_value, 255))
                ascii_index = int(pixel_value * (len(ascii_chars) - 1) / 255)
                ascii_char = ascii_chars[ascii_index]
                ascii_str += ascii_char
            ascii_str += "\n"

        return ascii_str

    def get_next_filename(self, base_filename="output.txt"):
        counter = 0
        new_filename = base_filename

        while os.path.exists(os.path.join("asciiart_output", new_filename)):
            counter += 1
            new_filename = f"output_{counter}.txt"

        return new_filename

    def ensure_directory_exists(self, directory_name="asciiart_output"):
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

    def invoke(self, context: InvocationContext) -> ImageOutput:
        input_image = context.services.images.get_pil_image(
            self.input_image.image_name)

        if self.output_to_file:
            ascii_str = self.image_to_ascii_string(
                input_image, self.font_spacing)

            self.ensure_directory_exists()
            filename = os.path.join(
                "asciiart_output", self.get_next_filename())

            with open(filename, "w") as f:
                f.write(ascii_str)

        detailed_ascii_art_image = self.image_to_detailed_ascii_art(
            input_image, self.font_spacing, self.color_mode)
        mask_dto = context.services.images.create(
            image=detailed_ascii_art_image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate,
        )

        return ImageOutput(
            image=ImageField(image_name=mask_dto.image_name),
            width=mask_dto.width,
            height=mask_dto.height,
        )
