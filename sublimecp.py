import enum
import re
import shutil
import subprocess
import threading
from enum import Enum
from pathlib import Path

import sublime
import sublime_plugin


class ColorType(Enum):
    HEX_PLAIN = enum.auto()
    HEX_ZERO_X = enum.auto()
    HEX_HASH = enum.auto()
    RGB = enum.auto()
    RGBA = enum.auto()


# SVG Colors spec: http://www.w3.org/TR/css3-color/#svg-color
SVG_COLORS = {
    'aliceblue': 'F0F8FF',
    'antiquewhite': 'FAEBD7',
    'aqua': '00FFFF',
    'aquamarine': '7FFFD4',
    'azure': 'F0FFFF',
    'beige': 'F5F5DC',
    'bisque': 'FFE4C4',
    'black': '000000',
    'blanchedalmond': 'FFEBCD',
    'blue': '0000FF',
    'blueviolet': '8A2BE2',
    'brown': 'A52A2A',
    'burlywood': 'DEB887',
    'cadetblue': '5F9EA0',
    'chartreuse': '7FFF00',
    'chocolate': 'D2691E',
    'coral': 'FF7F50',
    'cornflowerblue': '6495ED',
    'cornsilk': 'FFF8DC',
    'crimson': 'DC143C',
    'cyan': '00FFFF',
    'darkblue': '00008B',
    'darkcyan': '008B8B',
    'darkgoldenrod': 'B8860B',
    'darkgray': 'A9A9A9',
    'darkgreen': '006400',
    'darkgrey': 'A9A9A9',
    'darkkhaki': 'BDB76B',
    'darkmagenta': '8B008B',
    'darkolivegreen': '556B2F',
    'darkorange': 'FF8C00',
    'darkorchid': '9932CC',
    'darkred': '8B0000',
    'darksalmon': 'E9967A',
    'darkseagreen': '8FBC8F',
    'darkslateblue': '483D8B',
    'darkslategray': '2F4F4F',
    'darkslategrey': '2F4F4F',
    'darkturquoise': '00CED1',
    'darkviolet': '9400D3',
    'deeppink': 'FF1493',
    'deepskyblue': '00BFFF',
    'dimgray': '696969',
    'dimgrey': '696969',
    'dodgerblue': '1E90FF',
    'firebrick': 'B22222',
    'floralwhite': 'FFFAF0',
    'forestgreen': '228B22',
    'fuchsia': 'FF00FF',
    'gainsboro': 'DCDCDC',
    'ghostwhite': 'F8F8FF',
    'gold': 'FFD700',
    'goldenrod': 'DAA520',
    'gray': '808080',
    'green': '008000',
    'greenyellow': 'ADFF2F',
    'grey': '808080',
    'honeydew': 'F0FFF0',
    'hotpink': 'FF69B4',
    'indianred': 'CD5C5C',
    'indigo': '4B0082',
    'ivory': 'FFFFF0',
    'khaki': 'F0E68C',
    'lavender': 'E6E6FA',
    'lavenderblush': 'FFF0F5',
    'lawngreen': '7CFC00',
    'lemonchiffon': 'FFFACD',
    'lightblue': 'ADD8E6',
    'lightcoral': 'F08080',
    'lightcyan': 'E0FFFF',
    'lightgoldenrodyellow': 'FAFAD2',
    'lightgray': 'D3D3D3',
    'lightgreen': '90EE90',
    'lightgrey': 'D3D3D3',
    'lightpink': 'FFB6C1',
    'lightsalmon': 'FFA07A',
    'lightseagreen': '20B2AA',
    'lightskyblue': '87CEFA',
    'lightslategray': '778899',
    'lightslategrey': '778899',
    'lightsteelblue': 'B0C4DE',
    'lightyellow': 'FFFFE0',
    'lime': '00FF00',
    'limegreen': '32CD32',
    'linen': 'FAF0E6',
    'magenta': 'FF00FF',
    'maroon': '800000',
    'mediumaquamarine': '66CDAA',
    'mediumblue': '0000CD',
    'mediumorchid': 'BA55D3',
    'mediumpurple': '9370DB',
    'mediumseagreen': '3CB371',
    'mediumslateblue': '7B68EE',
    'mediumspringgreen': '00FA9A',
    'mediumturquoise': '48D1CC',
    'mediumvioletred': 'C71585',
    'midnightblue': '191970',
    'mintcream': 'F5FFFA',
    'mistyrose': 'FFE4E1',
    'moccasin': 'FFE4B5',
    'navajowhite': 'FFDEAD',
    'navy': '000080',
    'oldlace': 'FDF5E6',
    'olive': '808000',
    'olivedrab': '6B8E23',
    'orange': 'FFA500',
    'orangered': 'FF4500',
    'orchid': 'DA70D6',
    'palegoldenrod': 'EEE8AA',
    'palegreen': '98FB98',
    'paleturquoise': 'AFEEEE',
    'palevioletred': 'DB7093',
    'papayawhip': 'FFEFD5',
    'peachpuff': 'FFDAB9',
    'peru': 'CD853F',
    'pink': 'FFC0CB',
    'plum': 'DDA0DD',
    'powderblue': 'B0E0E6',
    'purple': '800080',
    'red': 'FF0000',
    'rosybrown': 'BC8F8F',
    'royalblue': '4169E1',
    'saddlebrown': '8B4513',
    'salmon': 'FA8072',
    'sandybrown': 'F4A460',
    'seagreen': '2E8B57',
    'seashell': 'FFF5EE',
    'sienna': 'A0522D',
    'silver': 'C0C0C0',
    'skyblue': '87CEEB',
    'slateblue': '6A5ACD',
    'slategray': '708090',
    'slategrey': '708090',
    'snow': 'FFFAFA',
    'springgreen': '00FF7F',
    'steelblue': '4682B4',
    'tan': 'D2B48C',
    'teal': '008080',
    'thistle': 'D8BFD8',
    'tomato': 'FF6347',
    'turquoise': '40E0D0',
    'violet': 'EE82EE',
    'wheat': 'F5DEB3',
    'white': 'FFFFFF',
    'whitesmoke': 'F5F5F5',
    'yellow': 'FFFF00',
    'yellowgreen': '9ACD32'
}


def pick_color(start_color=None):
    args = [shutil.which('python'), Path(sublime.packages_path()) / 'ColorPicker/bin/colorpicker.py']
    if start_color:
        args.append(start_color)
    return subprocess.check_output(args).decode('utf-8').strip()


def extract_color_texts(s):
    return re.finditer(
        r'\b[\da-fA-F]{6}|[\da-fA-F]{3}(\b|$)|' +
        r'\b0x[\da-fA-F]{6}|[\da-fA-F]{3}(\b|$)|' +
        r'#[\da-fA-F]{6}|[\da-fA-F]{3}(\b|$)|' +
        r'\brgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|' +
        r'\brgba\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*(1(\.0?)?|0(\.\d*)?)\s*\)|' +
        r'\b[a-zA-Z]+(\b|$)',
        s
    )


def find_color_text_type(color_text):
    if re.fullmatch(r'[\da-fA-F]{3}|[\da-fA-F]{6}', color_text):
        return ColorType.HEX_PLAIN, f'#{color_text}'
    elif color_text.startswith('0x'):
        return ColorType.HEX_ZERO_X, f'#{color_text[2:]}'
    elif color_text.startswith('#'):
        return ColorType.HEX_HASH, color_text
    elif color_text.startswith('rgb'):
        return ColorType.RGB, color_text
    elif color_text.startswith('rgba'):
        return ColorType.RGBA, color_text
    elif color_text.lower() in SVG_COLORS:
        return ColorType.HEX_HASH, f'#{SVG_COLORS[color_text.lower()]}'


def do_regions_overlap(start_1, end_1, start_2, end_2):
    return start_1 <= start_2 <= end_1 or start_2 <= start_1 <= end_2


class ColorPickReplaceRegionsHelperCommand(sublime_plugin.TextCommand):
    '''
    Helper command. Created since we can't use `edit` objects in separate threads.
    '''
    # noinspection PyMethodOverriding
    def run(self, edit, color_text, color_text_types):
        r, g, b, a = color_text.split(' ', 4)
        r, g, b, a = round(float(r) * 255), round(float(g) * 255), round(float(b) * 255), float(a)

        # Determine user preference for case of letters (default to upper-case)
        settings = sublime.load_settings('ColorPicker.sublime-settings')
        upper_case = settings.get('color_upper_case', True)
        cf = '02X' if upper_case else '02x'  # Color format

        # Replace the text in reverse order. Otherwise if we have an alpha, the text will jumbled.
        for (region, color_type) in zip(self.view.get_regions('ColorPick')[::-1], color_text_types[::-1]):
            # If alpha isn't 1.0, then the only possible format we can use is `rgba()`
            if a != 1.0:
                self.view.replace(edit, region, f'rgba({r}, {g}, {b}, {a:.2f})')
                continue
            # Match the color format we previously had
            color_type = ColorType(color_type)
            if color_type == ColorType.HEX_PLAIN:
                self.view.replace(edit, region, f'{r:{cf}}{g:{cf}}{b:{cf}}')
            elif color_type == ColorType.HEX_ZERO_X:
                self.view.replace(edit, region, f'0x{r:{cf}}{g:{cf}}{b:{cf}}')
            elif color_type == ColorType.HEX_HASH:
                self.view.replace(edit, region, f'#{r:{cf}}{g:{cf}}{b:{cf}}')
            elif color_type == ColorType.RGB:
                self.view.replace(edit, region, f'rgb({r}, {g}, {b})')
            elif color_type == ColorType.RGBA:
                self.view.replace(edit, region, f'rgba({r}, {g}, {b}, {a:.2f})')
        self.view.erase_regions('ColorPick')


class ColorPickCommand(sublime_plugin.TextCommand):
    def extract_colors(self):
        # Find all colors that overlaps a selection. Do this by finding all colors on all selected lines, then
        # checking to see if a selection overlaps the color text. Remember the color types too, so we can re-use
        # the same type, once a new color is selected.
        color_regions = []
        color_texts = []
        color_text_types = []
        line_to_color_text_matches = {}
        for region in self.view.sel():
            for line in self.view.lines(region):
                if line.to_tuple() not in line_to_color_text_matches:
                    line_to_color_text_matches[line.to_tuple()] = list(extract_color_texts(self.view.substr(line)))
                for color_text_match in line_to_color_text_matches[line.to_tuple()]:
                    if not do_regions_overlap(
                        region.begin(), region.end(),
                        line.begin() + color_text_match.start(), line.begin() + color_text_match.end()
                    ):
                        continue
                    color_text_type_res = find_color_text_type(color_text_match.group(0))
                    if not color_text_type_res:
                        continue
                    color_regions.append(
                        sublime.Region(line.begin() + color_text_match.start(), line.begin() + color_text_match.end())
                    )
                    color_text_type, color_text = color_text_type_res
                    color_text_types.append(color_text_type)
                    color_texts.append(color_text)
        return color_regions, color_texts, color_text_types

    def run(self, edit):
        (color_regions, color_texts, color_text_types) = self.extract_colors()
        if not color_regions:
            # No colors are selected. Pick a new color for each selected region.
            color_regions = self.view.sel()
            color_texts = [''] * len(color_regions)
            color_text_types = [ColorType.HEX_HASH] * len(color_regions)
        self.view.erase_regions('ColorPick')
        self.view.add_regions('ColorPick', color_regions)

        def worker():
            new_color = pick_color(color_texts[0])
            if new_color:
                self.view.run_command(
                    'color_pick_replace_regions_helper', {
                        'color_text': new_color,
                        'color_text_types': [color_text_type.value for color_text_type in color_text_types],
                    }
                )

        # Run the color picker in a thread, so we don't block
        threading.Thread(target=worker).start()
