from PIL import Image, ImageDraw, ImageFont
from invokeai.app.invocations.baseinvocation import BaseInvocation, InvocationContext, invocation, InputField
from invokeai.app.invocations.primitives import ImageField, ImageOutput
from invokeai.app.models.image import ImageCategory, ResourceOrigin


@invocation(
    "Image_to_ASCII_Art_Image",
    title="Image to ASCII Art Image",
    tags=["image", "ascii art", "detailed"],
    category="image",
    version="0.5.0",
)
class ImageToDetailedASCIIArtInvocation(BaseInvocation):
    input_image: ImageField = InputField(
        description="Input image to convert to detailed ASCII art")
    font_spacing: int = InputField(
        default=6, description="Font size for the ASCII art characters")
    detailed_mode: bool = InputField(
        default=True, description="Enable detailed mode (default: true)")
    color_mode: bool = InputField(
        default=False, description="Enable color mode (default: grayscale)")

    def image_to_detailed_ascii_art(self, input_image: Image.Image, font_spacing: int, detailed_mode: bool, color_mode: bool) -> Image.Image:
        if detailed_mode:
            ascii_chars = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\\^`'. "
        else:
            ascii_chars = "@%#*+=-:. "

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
                ascii_index = int(pixel_value * (len(ascii_chars) - 1) / 255)
                ascii_char = ascii_chars[ascii_index]

                if color_mode:
                    color = input_image.getpixel(
                        (x * font_spacing, y * font_spacing))
                    draw.text((x * font_spacing, y * font_spacing),
                              ascii_char, fill=color)
                else:
                    # Fill is black, and the character itself represents the shade
                    draw.text((x * font_spacing, y * font_spacing),
                              ascii_char, fill=0)

        return ascii_art_image

    def invoke(self, context: InvocationContext) -> ImageOutput:
        input_image = context.services.images.get_pil_image(
            self.input_image.image_name)
        detailed_ascii_art_image = self.image_to_detailed_ascii_art(
            input_image, self.font_spacing, self.detailed_mode, self.color_mode)
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
