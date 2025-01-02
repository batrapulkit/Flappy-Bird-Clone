import pygame
import random
from rembg import remove
from PIL import Image
import io

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)  # Pipe color (orange)
LAVA_COLOR = (255, 69, 0)  # Lava color

# Game settings
FPS = 60
GRAVITY = 0.5
JUMP = -10
PIPE_SPEED = 3
PIPE_GAP = 150
LAVA_HEIGHT = 50  # Lava height at top and bottom of the screen

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Clock
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("comicsansms", 40)

# Cache for images after removing background
image_cache = {}

# Function to remove the background of an image using rembg
def remove_bg(input_image_path):
    if input_image_path in image_cache:  # Check if the image has already been processed
        return image_cache[input_image_path]  # Return the cached image
    
    with open(input_image_path, 'rb') as input_file:
        input_data = input_file.read()
    output_data = remove(input_data)
    output_image = Image.open(io.BytesIO(output_data))
    pygame_image = pygame.image.fromstring(output_image.tobytes(), output_image.size, output_image.mode)
    
    image_cache[input_image_path] = pygame_image  # Cache the processed image
    return pygame_image

# Load and remove background of the bird image
def load_bird_image(path):
    bird_image = remove_bg(path)
    bird_image = pygame.transform.scale(bird_image, (40, 40))  # Resize bird image
    return bird_image

# Load and remove background of the game over image
def load_game_over_image(path):
    game_over_image = remove_bg(path)
    game_over_image = pygame.transform.scale(game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Fill the screen
    return game_over_image

# Load background image
bg = pygame.image.load('background.jpg')  # Replace with your background image file name
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Game Over screen image
game_over_img = load_game_over_image('game_over.jpg')  # Replace with your game over image file name

# Bird class with animations and smoother jump
class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.radius = 15
        self.vel = 0
        self.image_up = load_bird_image('bird.png')  # Replace with your image path
        self.image_down = load_bird_image('bird.png')  # Replace with your image path
        self.image = self.image_up
        self.rotation = 0

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        screen.blit(rotated_image, (self.x - 20, self.y - 20))

    def move(self):
        self.vel += GRAVITY
        self.y += self.vel

        # Limit bird's movement within the screen boundaries
        if self.y - self.radius < 0:
            self.y = self.radius  # Prevent going above the top
        elif self.y + self.radius > SCREEN_HEIGHT - LAVA_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius - LAVA_HEIGHT  # Prevent going below the lava (bottom)

        # Rotation effect
        if self.vel < -1:
            self.rotation = -15  # Rotate upwards when jumping
        elif self.vel > 1:
            self.rotation = 15  # Rotate downwards when falling
        else:
            self.rotation = 0  # No rotation when level

    def jump(self):
        self.vel = JUMP
        self.image = self.image_up  # Change to flapping up image

    def fall(self):
        self.image = self.image_down  # Change to falling image

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.top = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        self.bottom = self.top + PIPE_GAP
        self.width = 50
        self.color = ORANGE  # Orange color for pipes

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, 0, self.width, self.top))
        pygame.draw.rect(screen, self.color, (self.x, self.bottom, self.width, SCREEN_HEIGHT - self.bottom))

    def move(self):
        self.x -= PIPE_SPEED

    def is_off_screen(self):
        return self.x + self.width < 0

# Check for collision (now it will check if the bird goes out of bounds or hits pipes)
def check_collision(bird, pipes):
    # Check if the bird goes beyond top and bottom boundaries (lava)
    if bird.y - bird.radius < LAVA_HEIGHT or bird.y + bird.radius > SCREEN_HEIGHT - LAVA_HEIGHT:
        return True
    
    for pipe in pipes:
        if bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + pipe.width:
            if bird.y - bird.radius < pipe.top or bird.y + bird.radius > pipe.bottom:
                return True
    return False

# Draw text function
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Draw lava (top and bottom boundaries)
def draw_lava():
    pygame.draw.rect(screen, LAVA_COLOR, (0, 0, SCREEN_WIDTH, LAVA_HEIGHT))  # Top lava
    pygame.draw.rect(screen, LAVA_COLOR, (0, SCREEN_HEIGHT - LAVA_HEIGHT, SCREEN_WIDTH, LAVA_HEIGHT))  # Bottom lava

# Main game function
def main():
    run = True
    score = 0

    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + 100)]  # Starting pipes

    # Background position for continuous scroll
    bg_x1 = 0  # First background position
    bg_x2 = SCREEN_WIDTH  # Second background position

    while run:
        screen.fill(WHITE)

        # Scroll the background: draw both backgrounds
        screen.blit(bg, (bg_x1, 0))  # Draw the first background
        screen.blit(bg, (bg_x2, 0))  # Draw the second background

        # Draw lava (top and bottom boundaries)
        draw_lava()

        # Move the backgrounds
        bg_x1 -= 1
        bg_x2 -= 1

        # Reset the background positions when they go off-screen
        if bg_x1 <= -SCREEN_WIDTH:
            bg_x1 = SCREEN_WIDTH
        if bg_x2 <= -SCREEN_WIDTH:
            bg_x2 = SCREEN_WIDTH

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()
        bird.draw()

        # Create pipes when needed
        if len(pipes) == 0 or pipes[-1].x < SCREEN_WIDTH - 200:  # Add pipe when needed
            pipes.append(Pipe(SCREEN_WIDTH + 100))

        # Move pipes and check for collision
        for pipe in pipes:
            pipe.move()
            pipe.draw()
            if pipe.is_off_screen():
                pipes.remove(pipe)
                score += 1

        # Check collision with pipes and boundaries (lava)
        if check_collision(bird, pipes):
            # You can add a visual cue, like changing the bird's image or showing a message
            draw_text("Touched the lava!", font, BLACK, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)

        # Draw score
        draw_text(f"Score: {score}", font, BLACK, 10, 10)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
