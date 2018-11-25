UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)



class Game(object):
    GAME_OVER = 1
    
    def __init__(self):
        self.grid = Grid(15, 15)
        self.snake = Snake()
        
        self.added_length = 0

    
    def update(self):
        x, y = self.snake.position 
        current_block = Grid[x][y]
        
        direction = self.snake.direction        
        x += direction[0]
        y += direction[1]
        
        next_block = Grid[x][y]
        if not next_block.state == BLOCK.free:
            return GAME_OVER
        
        next_block.state = BLOCK.HEAD
        
        


class Snake(object):    
    def __init__(self):
        self.direction = LEFT
        self.position = [0,0]
        self.length = 5   



class Grid(object):
    def __init__(self, width, height):
        self.rows = [Row(width) for _ in range(height)]
        
    
    def __len__(self):
        return len(self.rows)
    
    
    def __getitem__(self, index):
        return self.rows[index]
        
    
    def draw(self):
        symbols = {Block.FREE:'_', 
                   Block.HEAD:'&', 
                   Block.BODY:'#',
                   Block.TAIL:'^',
                   Block.CORNER:'%'}
                
        
        for row in self.rows:
            line = ''
            for column in row.columns:
                line += symbols[column.state]                
            print line
        
        
class Row(object):
    def __init__(self, width):
        self.columns = [Block() for _ in range(width)]
        
        
    def __len__(self):
        return len(self.columns)
    
    
    def __getitem__(self, index):
        return self.columns[index]
        
        
        
class Block(object):
    FREE = 1    
    HEAD = 2
    BODY = 3    
    TAIL = 4    
    CORNER = 5
    
    APPLE = 6

    
    def __init__(self):
        self.type = Block.FREE
        self.direction = LEFT
        self.counter = 0
        
        
grid = Grid(10, 12)
grid.draw()