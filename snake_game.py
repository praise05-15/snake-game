# Import required modules
import pygame      # For creating the game GUI
import random      # For randomizing food placement
import sys         # For system-level operations (like quitting)
import os          # For working with file paths
import json        # For saving and loading high score as JSON
import time        # For bonus mode duration control

# Main SnakeGame class using object-oriented programming
class SnakeGame:
    def __init__(self):
        # Initialize Pygame and sound mixer
        pygame.init()
        pygame.mixer.init()
        
        # Game window setup
        self.WIDTH, self.HEIGHT = 800, 600  
        self.BLOCK = 20                    
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))  # Game window
        pygame.display.set_caption("Snake Game")  
        
        # Define color constants
        self.LIGHT_GREEN = (204, 255, 204)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.SNAKE_HEAD = (0, 100, 0)
        self.SNAKE_BODY = (34, 139, 34)
        self.FOOD = (255, 0, 0)
        self.BORDER = (0, 0, 0)
        self.TEXT = (50, 50, 50)
        
        # Set fonts
        self.font = pygame.font.SysFont("Segoe UI", 28)
        self.big_font = pygame.font.SysFont("Segoe UI", 50, bold=True)
        
        # Difficulty and speed mapping
        self.difficulty = 'Beginner'
        self.speeds = {'Beginner': 6, 'Intermediate': 12, 'Advanced': 20}
        self.clock = pygame.time.Clock()  # Controls frame rate
        
        # File path for storing high scores
        self.score_file = "highscore.json"
        
        # Try loading sound for food eating effect
        try:
            self.eat_sound = pygame.mixer.Sound(
                file=os.path.join(pygame.__path__[0], 'examples/data/boom.wav')
            )
        except Exception:
            self.eat_sound = None  # Disable sound if not available
        
        # Bonus mode variables
        self.bonus_active = False
        self.bonus_start_time = 0
        self.bonus_duration = 10  # Active for 10 seconds

    # Load high score from JSON file
    def load_highscore(self):
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, "r") as f:
                    return json.load(f).get("highscore", 0)
        except Exception:
            pass
        return 0

    # Save high score to file if it's a new record
    def save_highscore(self, score):
        high = self.load_highscore()
        if score > high:
            try:
                with open(self.score_file, "w") as f:
                    json.dump({"highscore": score}, f)
            except Exception:
                pass

    # Draw any text on the screen
    def draw_text(self, text, x, y, size=None, color=None, center=False):
        size = size or self.font
        color = color or self.TEXT
        label = size.render(text, True, color)
        rect = label.get_rect(center=(x, y) if center else (x, y))
        self.screen.blit(label, rect)
        return rect

    # Create an interactive button
    def draw_button(self, text, x, y, w, h, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        hovered = pygame.Rect(x, y, w, h).collidepoint(mouse)
        pygame.draw.rect(self.screen, self.BLACK if hovered else self.WHITE, (x, y, w, h), border_radius=10)
        self.draw_text(text, x + w // 2, y + h // 2, center=True)
        if hovered and click[0] and action:
            pygame.time.wait(150)  # Prevent multiple clicks
            action()

    # Cycle to the next difficulty level
    def change_difficulty(self):
        levels = list(self.speeds.keys())
        i = levels.index(self.difficulty)
        self.difficulty = levels[(i + 1) % len(levels)]

    # Spawn food in a location not occupied by the snake
    def spawn_food(self, snake):
        while True:
            x = random.randint(0, self.WIDTH - self.BLOCK) // self.BLOCK * self.BLOCK
            y = random.randint(80, self.HEIGHT - self.BLOCK) // self.BLOCK * self.BLOCK
            if (x, y) not in snake:
                return x, y

    # Draw the snake on the screen
    def draw_snake(self, snake, block_size):
        for i, (x, y) in enumerate(snake):#for loop that goes through every part of the snake.
            color = self.SNAKE_HEAD if i == 0 else self.SNAKE_BODY
           
            pygame.draw.rect(self.screen, color, (x, y, block_size, block_size), border_radius=8)
        # Draw eyes on the head
        head_x, head_y = snake[0]
        eye_radius = max(2, block_size // 7)
        pygame.draw.circle(self.screen, self.BLACK, (head_x + eye_radius*2, head_y + eye_radius*2), eye_radius)
        pygame.draw.circle(self.screen, self.BLACK, (head_x + block_size - eye_radius*2, head_y + eye_radius*2), eye_radius)

    # Display game over screen and options
    def game_over_screen(self, score):
        while True:
            self.screen.fill(self.LIGHT_GREEN)
            self.draw_text("Oops! Game Over", self.WIDTH // 2, 150, self.big_font, center=True)
            self.draw_text(f"Your Score: {score}", self.WIDTH // 2, 220, center=True)
            self.draw_button("Restart", self.WIDTH // 2 - 100, 300, 200, 50, self.game_loop)
            self.draw_button("Quit", self.WIDTH // 2 - 100, 380, 200, 50, lambda: sys.exit())

           #Starts a loop to handle all pending Pygame events like quitting or clicking.


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

    # Main game logic
    def game_loop(self):
        
        x, y = self.WIDTH // 2, self.HEIGHT // 2
        dx, dy = self.BLOCK, 0
        snake = [(x, y)]    # snake body segments
        food = self.spawn_food(snake)
        score = 0
        speed = self.speeds[self.difficulty]
        highscore = self.load_highscore()
        block_size = self.BLOCK
        self.bonus_active = False
        self.bonus_start_time = 0
        paused = False
        running = True


        '''Infinite loop while the game is running.'''
        while running: 
           
            self.screen.fill(self.LIGHT_GREEN)

            # Draw border around game area
            border_thickness = 5
            pygame.draw.rect(self.screen, self.BORDER, 
                             (border_thickness, 80 + border_thickness, 
                              self.WIDTH - 2 * border_thickness, 
                              self.HEIGHT - 80 - 2 * border_thickness), border_thickness)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_highscore(score)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_highscore(score)
                        return
                    if event.key == pygame.K_p:
                        paused = not paused
                    if not paused:
                        if event.key == pygame.K_UP and dy == 0:
                            dx, dy = 0, -self.BLOCK
                        if event.key == pygame.K_DOWN and dy == 0:
                            dx, dy = 0, self.BLOCK
                        if event.key == pygame.K_LEFT and dx == 0:
                            dx, dy = -self.BLOCK, 0
                        if event.key == pygame.K_RIGHT and dx == 0:
                            dx, dy = self.BLOCK, 0

            #DRAW Pause screen
            if paused:
                self.draw_text("Paused", self.WIDTH // 2, self.HEIGHT // 2, self.big_font, self.BLACK, center=True)
                pygame.display.update()
                self.clock.tick(10)
                continue  #Skip the rest of the loop until unpaused.



            # Bonus mode: activated every 10 points
            if score >= 10 and score % 10 == 0 and not self.bonus_active:
                self.bonus_active = True
                self.bonus_start_time = time.time()
                speed = max(1, speed + 7)  # Temporary speed change
                block_size = self.BLOCK + 10  # Visually larger snake

            # End bonus mode after duration
            if self.bonus_active and time.time() - self.bonus_start_time >= self.bonus_duration:
                self.bonus_active = False
                speed = self.speeds[self.difficulty]
                block_size = self.BLOCK

            # Update snake position
            x += dx
            y += dy
            head = (x, y) #Create new head tuple.

            # Collision detection
            if head in snake or x < 0 or y < 80 or x >= self.WIDTH or y >= self.HEIGHT:
                self.save_highscore(score)
                self.game_over_screen(score)
                return # end game loop.

            snake.insert(0, head)

            # Food collision
            if head == food:
                score += 2 if self.bonus_active else 1
                if self.eat_sound:
                    self.eat_sound.play()
                food = self.spawn_food(snake)
            else:
                snake.pop()  

            # Draw updated snake and food
            self.draw_snake(snake, block_size)
            pygame.draw.circle(self.screen, self.FOOD,
                               (food[0] + self.BLOCK // 2, food[1] + self.BLOCK // 2), self.BLOCK // 2)

            # Draw Upper panel
            pygame.draw.rect(self.screen, self.WHITE, (0, 0, self.WIDTH, 80))
            self.draw_text(f"Score: {score}", 150, 25)
            self.draw_text(f"High Score: {highscore}", 600, 25)
            self.draw_text(f"{self.difficulty}", self.WIDTH // 2, 25, center=True)

            pygame.display.update()  
            self.clock.tick(speed)

    # Main menu 
    def main_menu(self):
        while True:
            self.screen.fill(self.LIGHT_GREEN)
            self.draw_text("Snake Game", self.WIDTH // 2, 100, self.big_font, center=True)
            self.draw_button("Start Game", self.WIDTH // 2 - 100, 180, 200, 50, self.game_loop)
            self.draw_button(self.difficulty, self.WIDTH // 2 - 100, 260, 200, 50, self.change_difficulty)
            self.draw_button("Quit", self.WIDTH // 2 - 100, 340, 200, 50, lambda: sys.exit())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

# Start the game
if __name__ == "__main__":
    try:
        game = SnakeGame()
        game.main_menu()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        pygame.quit()
        sys.exit()
