

class Font(object):
    def __init__(self):
        self.lookup = {}
        
        
    def load(self, keys, font_str, font_width, compressed=False):
        if compressed:
            font_str = Font.uncompress(font_str)
            
        font = []
        for i in range(len(font_str) / font_width):
            line = font_str[i*font_width:(i+1)*font_width]
            font.append([int(num) for num in line])
        
        break_points = [0]
        for i in range(len(font[0])):
            break_line = True
            for j in range(len(font)):
                if font[j][i] != 0:
                    break_line = False
        
            if break_line:    
                break_points.append(i)        
        break_points.append(-1)
        
        self.lookup = {}
        for index, key in enumerate(keys):
            self.lookup[key] = grid = []
            for i in range(len(font)):
                j, k = break_points[index], break_points[index+1]
                j = j if j == 0 else (j + 1)
                grid.append(font[i][j:k])
        
    
    @staticmethod
    def compress(image_str):
        image_str = self.image_string
        if not image_str:
            return ''
        
        lookup = {'0':'!', '1':'-'}
        output = []
        previous_letter = image_str[0]
        letter_count = 1
        image_str += '|'
        for letter in image_str[1:]:
            if letter == previous_letter:
                letter_count += 1
                continue
            
            if letter_count == 1:
                output.append(lookup[previous_letter])
            else:
                output.append(lookup[previous_letter])
                output.append(str(letter_count))
                
            previous_letter = letter
            letter_count = 1
        
        return ''.join(output)
    

    @staticmethod
    def uncompress(image_str):
        lookup = {'!':'0', '-':'1','&':'2'}
        current_number = ''
        counter_str = '1'
        image_str += '&'
        
        output = []
        for letter in image_str:
            number = lookup.get(letter, None)
            
            if number is None:
                counter_str += letter
            else:
                output.append(current_number * int(counter_str if counter_str != '' else '1'))
                
                current_number = number            
                counter_str = ''
                
        return ''.join(output)


    def process(self, keys, font_str, font_width):    
        font_str = uncompress(font_str)
        font = []
        for i in range(len(font_str) / font_width):
            line = font_str[i*font_width:(i+1)*font_width]
            font.append([int(num) for num in line])
            
        break_points = [0]
        for i in range(len(font[0])):
            break_line = True
            for j in range(len(font)):
                if font[j][i] != 0:
                    break_line = False
        
            if break_line:    
                break_points.append(i)        
        break_points.append(-1)
        
        all_grids = {}
        for index, key in enumerate(keys):
            all_grids[key] = grid = []
            for i in range(len(font)):
                j, k = break_points[index], break_points[index+1]
                j = j if j == 0 else (j + 1)
                grid.append(font[i][j:k])
         
        return all_grids

font_lower_width, font_lower_height = 166, 11
font_lower = \
'!7-2!16-2!10-2!8-2!5-2!2-2!-2!5-2!51-2!50-2!16-2!9-2!9-2!12-2!5-2!51-2!44-4!2-5!3-4!3-5!2-4!2-4!'\
'2-4!2-5!2-2!2-2!-2!2-2!-2!-7!2-5!3-4!2-5!3-4!2-2!-2!2-4!-4!-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!2-2!-5'\
'!4-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!2-2!2-2!2-2!-2!2-2!-2!2-2!-2!-2!2-2!-2!-2!-2!-2!2-2!-2!2-2!-2!2'\
'-2!-2!2-2!-5!-2!5-2!2-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!2-2!3-2!2-5!-2!2-2!-2!5-2!2-2!-2!2-2!2-2!2-2'\
'!2-2!-2!2-2!-2!2-2!-4!3-2!-2!-2!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!4-2!5-2!2-2!2-2!-2!2-2!-2!3-2!'\
'-2!2-2!-2!2-2!3-2!-2!2-2!-2!2-2!-2!5-2!2-2!-6!2-2!2-2!2-2!-2!2-2!-2!2-2!-3!4-2!-2!-2!-2!-2!2-2!-'\
'2!2-2!-2!2-2!-2!2-2!-2!5-3!3-2!2-2!2-2!-2!2-2!-2!-!-2!2-4!2-2!2-2!2-2!2-2!2-2!-2!2-2!-2!5-2!2-2!'\
'-2!6-2!2-2!2-2!-2!2-2!-2!2-2!-4!3-2!-2!-2!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!7-2!2-2!2-2!2-2!2-!2'\
'-!2-2!-!-2!-6!-2!2-2!2-2!2-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!2-2!2-2!2-2!-2!2-2!-2!2-2!-2!-2!2-2'\
'!-2!-2!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!7-2!2-2!2-2!2-2!2-4!3-5!2-2!2-2!-2!2-2!-2!4-5!-5!3-4!3-'\
'5!2-4!3-2!3-5!-2!2-2!-2!-2!2-2!2-2!-2!-2!-2!-2!-2!2-2!2-4!2-5!3-5!-2!4-4!4-2!2-5!3-2!4-2!-2!2-2!'\
'2-2!2-5!-5!44-2!48-2!9-2!51-2!47-4!49-2!9-2!48-4!7'

font_upper_width, font_upper_height = 174, 11
font_upper = \
'!-4!2-5!3-4!2-5!2-5!-5!2-4!2-2!2-2!-2!3-2!-2!2-2!-2!3-!5-!-!4-2!2-4!2-5!3-4!2-5!3-4!2-6!-2!2-2!-'\
'2!2-2!-2!3-2!-2!2-2!-2!2-2!-8!2-2!-2!2-2!-2!2-2!-2!2-2!-2!4-2!4-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!3-'\
'2!3-2!-2!3-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!3-2!3-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!2-2!4-2!-2!2'\
'-2!-2!2-2!-2!5-2!2-2!-2!4-2!4-2!5-2!2-2!-2!3-2!-2!2-2!-2!3-3!-3!-3!2-2!-2!2-2!-2!2-2!-2!2-2!-2!2'\
'-2!-2!7-2!3-2!2-2!-2!2-2!-2!3-2!2-4!2-2!2-2!4-2!-2!2-2!-2!2-2!-2!5-2!2-2!-4!2-4!2-2!5-2!2-2!-2!3'\
'-2!-2!2-2!-2!3-7!-4!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!7-2!3-2!2-2!-2!2-2!-2!-!-2!2-4!2-2!2-2!3-2'\
'!2-6!-5!2-2!5-2!2-2!-2!4-2!4-2!5-6!-2!3-2!-5!2-2!3-2!-!-2!-7!-2!2-2!-5!2-2!2-2!-5!3-4!4-2!3-2!2-'\
'2!-2!2-2!-2!-!-2!3-2!4-4!4-2!2-2!2-2!-2!2-2!-2!5-2!2-2!-2!4-2!4-2!-3!-2!2-2!-2!3-2!-2!2-2!-2!3-2'\
'!3-2!-2!-4!-2!2-2!-2!5-2!2-2!-2!2-2!5-2!3-2!3-2!2-2!-2!2-2!-7!2-4!4-2!4-2!3-2!2-2!-2!2-2!-2!5-2!'\
'2-2!-2!4-2!4-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!3-2!3-2!-2!2-3!-2!2-2!-2!5-2!2-2!-2!2-2!5-2!3-2!3-2!2'\
'-2!2-4!3-5!3-4!4-2!4-2!3-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!4-2!4-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!3-2!3'\
'-2!-2!3-2!-2!2-2!-2!5-2!-3!-2!2-2!-2!2-2!3-2!3-2!2-2!2-4!3-5!2-2!2-2!3-2!3-2!4-2!2-2!-5!3-4!2-5!'\
'2-5!-2!5-4!2-2!2-2!-2!-3!2-2!2-2!-4!-2!3-2!-2!4-!2-4!2-2!6-4!2-2!2-2!2-4!4-2!4-4!4-2!4-2!-2!2-2!'\
'2-2!3-2!3-6!108-2!238'

font_numbers_width, font_number_height = 70, 11
font_numbers = \
'!-4!3-2!3-4!3-4!6-2!2-6!2-4!2-6!2-4!3-4!3-2!2-2!-3!2-2!2-2!-2!2-2!4-3!2-2!5-2!2-2!-2!2-2!-2!2-2'\
'!-2!2-2!2-2!2-2!2-2!2-2!2-2!-2!2-2!3-4!2-2!5-2!9-2!-2!2-2!-2!2-2!2-2!2-2!2-2!2-2!2-2!5-2!2-2!-2'\
'!2-5!2-5!6-2!-2!2-2!-2!2-2!2-2!2-2!2-2!5-3!3-3!3-!2-2!6-2!-2!2-2!4-2!3-4!2-2!2-2!2-2!2-2!2-2!4-'\
'3!6-2!-2!2-2!6-2!-2!2-2!3-3!2-2!2-2!2-5!2-2!2-2!2-2!3-3!3-2!2-2!-2!2-2!2-2!2-2!-2!2-2!3-2!3-2!2'\
'-2!5-2!2-2!2-2!2-2!2-3!4-2!2-2!-7!-2!2-2!-2!2-2!3-2!3-2!2-2!-2!2-2!3-4!2-4!-6!2-4!6-2!3-4!3-4!4'\
'-2!4-4!3-4!143'

font_symbols_width, font_symbols_height = 49, 11
font_symbols = \
'!6-2!2-4!5-2!-2!10-2!-2!2-3!-3!7-2!-2!2-2!4-2!-2!10-2!-2!-2!5-4!-2!-2!-2!2-2!4-2!-2!10-2!2-!-2!'\
'5-4!-2!-2!5-2!3-2!3-2!9-2!4-2!5-2!6-2!3-3!4-2!3-2!9-2!4-2!5-2!6-2!3-2!4-2!5-2!8-2!4-2!5-4!-2!12'\
'-2!5-2!8-2!4-2!5-4!-2!-2!3-2!3-2!7-2!-2!-2!-2!4-2!5-2!4-!-2!3-2!3-2!7-2!-2!-2!-2!5-3!-3!30-!68'
symbols = ':',';','!','?','/','\\','.',',','|','\'','(',')'

font = splitLetters([chr(index + 97) for index in range(26)], font_lower, font_lower_width)
font.update(splitLetters([chr(index + 65) for index in range(26)], font_upper, font_upper_width))
font.update(splitLetters([str(index) for index in range(10)], font_numbers, font_numbers_width))
font.update(splitLetters(symbols, font_symbols, font_symbols_width))
font[' '] = [[0 for _ in range(4)] for _ in range(11)]
font['"'] = font['\'']
font['{'] = font['['] = font['(']
font['}'] = font[']'] = font['('] 