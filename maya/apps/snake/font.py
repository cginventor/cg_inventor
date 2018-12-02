class Font(object):
    def __init__(self, data, height):
        self.height = height

        # process symbols
        #
        self._data = {}
        for letter, grid in data.items():
            bin_str = bin(int(grid, 16))[3:]
            width = len(bin_str) / self.height
            self._data[letter] = [bin_str[i * width:(i + 1) * width] for i in range(height)]


    def __getitem__(self, text):
        grid = ['' for _ in range(self.height)]
        for letter in text:
            letter_grid = self._data.get(letter, ' ')
            for i, row in enumerate(letter_grid):
                grid[i] += row
                if letter != text[-1]:
                    grid[i] += '0'
        return len(grid[0]), [int(i, 2) for i in grid]



symbols = {' ': '100000000000',
            '!': '7ffcf0',
            '"': '7d0000',
            '\'': '7d0000',
            '(': '17ccccccc700',
            ')': '1e3333333e00',
            ',': '4000f0',
            '.': '4000f4',
            '/': '8c633198cc6000',
            '0': '5ecf3cf3cf3cde000',
            '1': '16e666666f00',
            '2': '5ecf3cc739ce3f000',
            '3': '5ecf30ce0f3cde000',
            '4': '21871e6c9b366fe18000',
            '5': '7fc30f830f3cde000',
            '6': '5ecf0fb3cf3cde000',
            '7': '7fcc30c638c30c000',
            '8': '5ecf3cdecf3cde000',
            '9': '5ecf3cf37c3cde000',
            ':': '43c3c0',
            ';': '43c3d0',
            '?': '5ecf30ce30030c000',
            'A': '5ecf3cffcf3cf3000',
            'B': '7ecf3cfecf3cfe000',
            'C': '5ecf0c30c30cde000',
            'D': '7ecf3cf3cf3cfe000',
            'E': 'ff18f6318c7c00',
            'F': 'ff18f6318c6000',
            'G': '5ecf0c30df3cde000',
            'H': '73cf3cffcf3cf3000',
            'I': '7ffff0',
            'J': '133333333e00',
            'K': '73cf3cfecf3cf3000',
            'L': '1ccccccccf00',
            'M': '3071f7ffaf1e3c78c000',
            'N': '30f1f3f7ff7e7c784000',
            'O': '5ecf3cf3cf3cde000',
            'P': '7ecf3cfec30c30000',
            'Q': '5ecf3cf3cf3dde0c0',
            'R': '7ecf3cfecf3cf3000',
            'S': '5ecf0c1e0c3cde000',
            'T': '7f30c30c30c30c000',
            'U': '73cf3cf3cf3cde000',
            'V': '73cf3cf3cde78c000',
            'W': '38f1e3d7affbe7cd8000',
            'X': '73cde78c79ecf3000',
            'Y': '73cf3cde30c30c000',
            'Z': 'fc633198cc7c00',
            '[': '17ccccccc700',
            '\\': 'e318630c618c00',
            ']': '1e3333333e00',
            'a': '4001e0dfcf3cdf000',
            'b': '70c3ecf3cf3cfe000',
            'c': '4001ecf0c30cde000',
            'd': '430dfcf3cf3cdf000',
            'e': '4001ecf3ff0cde000',
            'f': '136f66666600',
            'g': '4001ecf3cf3cdf0de',
            'h': '70c3ecf3cf3cf3000',
            'i': '73fff0',
            'j': '2c36db780',
            'k': '70c33dbce3cdb3000',
            'l': '7ffff0',
            'm': '10000fedbdbdbdbdbdb0000',
            'n': '4003ecf3cf3cf3000',
            'o': '4001ecf3cf3cde000',
            'p': '4003ecf3cf3cfec30',
            'q': '4001ecf3cf3cdf0c3',
            'r': '801bfe318c6000',
            's': '800fc61c31f800',
            't': '166f66666300',
            'u': '40033cf3cf3cdf000',
            'v': '40033cf3cd278c000',
            'w': '200063c78f5eb7cd8000',
            'x': '40033cf37bfcf3000',
            'y': '40033cf3cf3cdf0de',
            'z': '100f3366cf00',
            '{': '17ccccccc700',
            '|': '7ffff0',
            '}': '1e3333333e00'}

main_font = Font(symbols, 11)

