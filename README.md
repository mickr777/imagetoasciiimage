# Image to Character Art Image Node's

## Ascii Art Node
### Features
* Converts an input image into its ASCII art Image.
* Preset ASCII character Sets.
* Switch between colored and grayscale modes
* Switch between white and Black Backgrounds with the invert switch
* Gamma control on the output image
* Output to a text file
  (due to text file spacing the output won't look the same as the image in the gallery)

### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `input_image`  | The input image that you want to convert to ASCII art.|
| `font_spacing` | Font spacing for the ASCII characters.|
| `ascii_set`| Choose the desired ASCII character set.|
| `color_mode`   | Whether to use colors in the ASCII art or not.|
| `invert_colors`   | Invert background color and ASCII character order.|
| `output_to_file`| Output ASCII art to a text file. |
| `gamma` | Gamma correction value for the output image. |
| `board` | Pick Board to add output too. |

## Unicode Art Node
### Features
* Converts an input image into its Unicode art Image.
* Preset Unicode character Sets.
* Switch between colored and grayscale modes
* Switch between white and Black Backgrounds with the invert switch
* Gamma control on output image
  (an external font is required for Unicode, but will be automatically downloaded and cached for future use)
  
### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `input_image`  | The input image that you want to convert to Unicode art.|
| `font_size` | Font size for the Unicode characters.|
| `unicode_set`| Choose the desired Unicode character set.|
| `color_mode`   | Whether to use colors in the Unicode art or not.|
| `invert_colors`   | Invert background color and Unicode character order.|
| `gamma` | Gamma correction value for the output image. |
| `board` | Pick Board to add output too. |

## i2aa Any Font Node (skunkworxdark)
### Features
* Converts an input image into its ASCII art image but you can use any font or range of characters.
* Font download into a font_cache in the same way as the [textfontimage](https://github.com/mickr777/textfontimage) node.
* A large array of predefined character ranges and an option to provide a custom string of characters.
* Switch between colored and grayscale output
* The output image is built by comparing the image one character-sized block at a time to determine which character to use for that block of the image. For this you can choose comparison methods to use. As a starting point, I would recommend using NAL or MSE as these produce the best output in most cases at a reasonable speed. 
  * `Sum of Absolute Differences` (SAD) - This is a basic math approach to see which character is the least different 
  * `Mean Squared Error` (MSE) - This uses a mathematical approach that takes into account a bit more of the structure.
  * `Structural Similarity` (SSIM) - This is VERY VERY Slow but it attempts to find the character with the closest structural similarity for each block. This sometimes works better if the convert to mono is used and is included only for completeness.
  * `Normalized Average Luminance` (NAL) - This is very quick and produces quite a good result. It works by calculating the average luminance of each available character and then normalizes this to the full 0-255 range and then compares this to the average luminance of each block of the image to determine which is the best character to use. 
* Can select which board to output to.
  
### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `input_image`  | The input image that you want to convert to Unicode art.|
| `font_url` | Path/Name of the font to use. |
| `local_font_path` | URL address of the font file to download. |
| `local_font` | Local font file path (overrides font_url) |
| `font_size` | Name of the local font file to use from the font_cache folder|
| `character_range`| The character range to use.|
| `custom_characters`| Custom Characters only used if Custom is selected from range|
| `comparison_type` | Choose the comparison type. |
| `mono_comparison`   | Convert input image to mono for comparison.|
| `color_mode`   | Enable color mode (default: grayscale).|
| `board` | Pick Board to add output too. |

## Examples
### Ascii Art Node
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/f0a8ee6a-94d9-4108-a660-5103215aac03" width="250" /><br />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/7f596e75-3992-41e6-a88b-408bcc986da9" width="400" /><br />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/46b1b022-af7d-4758-aec3-5c4717e88530" width="400" /><br />

### Unicode Art Node
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/3c4990eb-2f42-46b9-90f9-0088b939dc6a" width="350" /><br />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/384155e0-8e12-4753-946e-0804e0dde94c" width="250" /><br />

### i2aa Any Font Node
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/fee7f800-a4a8-41e2-a66b-c66e4343307e" width="300" />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/21961335/969f8c75-3254-4ab5-b294-8adbf87b2123" width="300" />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/21961335/8844bc51-5b95-4c41-87f2-3316c7737956" width="300" />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/21961335/3c7817ae-5159-419b-a023-2459e2b2035b" width="300" />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/21961335/81c57259-cabd-44a6-b522-c0857976c0cd" width="300" />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/21961335/264793f3-838a-49bc-9356-0ae674f15cd8" width="300" />
<br />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/1d9c1003-a45f-45c2-aac7-46470bb89330" width="600" />
<br />

