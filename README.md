# Image to Character Art Image Node's

## Ascii Art Node
### Features
* Converts an input image into its ASCII art Image.
* Preset ASCII character Sets.
* Switch between colored and grayscale modes
* Switch between white and Black Backgrounds with the invert switch
* Gamma control on output image
* Output to a text file
  (due to text file sapincg the output wont look the same as the image in gallery)

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
  (an external font is required for unicode, but will be automaticaly downloaded and cahced for future use)
  
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
* Comming Soon...
*
  
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
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/fee7f800-a4a8-41e2-a66b-c66e4343307e" width="350" /><br />
<img src="https://github.com/mickr777/imagetoasciiimage/assets/115216705/1d9c1003-a45f-45c2-aac7-46470bb89330" width="350" /><br />


