# Screenshots
<p align="center">
    <img src="https://raw.githubusercontent.com/stevenxxiu/ColorPicker/master/images/screenshot.png">
</p>

# Installation
Install this repository via [Package Control](https://sublime.wbond.net).

# Usage
To insert colors, use:

- Linux: `ctrl+shift+c`
- Windows: `ctrl+shift+c`
- OS X: `cmd+shift+c`

or use menu action

- **`Tools`** -> **`ColorPicker`**

To edit a color, select parts of the color text, and repeat above. All colors that are a part of the selection, will be changed the the selected color.

Supported color types:

    112233 0x112233 #112233 rgb(11, 22, 33) rgba(11, 22, 33, 0.5)

By default, the hex color code is inserted using uppercase letters. To use lowercase letters instead, copy the contents of **`Preferences -> Package Settings -> ColorPicker -> Settings-Default`** to the empty file created by selecting **`Preferences -> Package Settings -> ColorPicker -> Settings-User`**, then change `"color_upper_case"` to `false`.
