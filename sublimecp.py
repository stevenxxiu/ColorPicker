import os
import re
import subprocess
import threading

import sublime
import sublime_plugin

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
    if start_color in SVG_COLORS:
        start_color = f'#{SVG_COLORS[start_color]}'
    else:
        matches = re.fullmatch(r'(?:0x|#)?([\da-f]{3}|[\da-f]{6})', start_color, re.IGNORECASE)
        if matches:
            start_color = f'#{matches.group(1)}'

    args = [os.path.join(sublime.packages_path(), binpath)]
    if start_color:
        args.append(start_color)

    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    color = proc.communicate()[0].strip()

    if color:
        color = color.decode('utf-8')

    return color


class ColorPickReplaceRegionsHelperCommand(sublime_plugin.TextCommand):
    '''
    Helper command. Created since we can't use `edit` objects in separate threads.
    '''
    # noinspection PyMethodOverriding
    def run(self, edit, color):
        for region in self.view.get_regions('ColorPick'):
            self.view.replace(edit, region, color)
        self.view.erase_regions('ColorPick')


class ColorPickCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Remember all regions to replace later. Restrict each selected region to a color, if there's one there. We
        # use `view.word()` to get the closest color. `0x` is considered as being a part of a word. `#` is not.
        #
        # Checking if the character at `word.a - 1` is `#` is ok, as this will never go to the previous line. Indeed,
        # if it goes to the previous line, then the character must be `\n`.
        regions = []
        for region in self.view.sel():
            word = self.view.word(region)
            if re.fullmatch(r'[\da-f]{3}|[\da-f]{6}', self.view.substr(word), re.IGNORECASE):
                if self.view.substr(word.a - 1) == '#':
                    region = sublime.Region(word.a - 1, word.b)
                else:
                    region = word
            elif re.fullmatch(r'0x([\da-f]{3}|[\da-f]{6})', self.view.substr(word), re.IGNORECASE):
                region = word
            regions.append(region)

        self.view.erase_regions('ColorPick')
        self.view.add_regions('ColorPick', regions)

        def worker():
            color = pick_color(self.view.substr(regions[0]))
            if color:
                # Determine user preference for case of letters (default upper)
                s = sublime.load_settings('ColorPicker.sublime-settings')
                upper_case = s.get('color_upper_case', True)
                if upper_case:
                    color = color.upper()
                else:
                    color = color.lower()
                self.view.run_command('color_pick_replace_regions_helper', {'color': f'#{color}'})

        threading.Thread(target=worker).start()


libdir = os.path.join('ColorPicker', 'lib')
binpath = os.path.join(libdir, 'colorpicker.py')
