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

# Game settings
FPS = 60
GRAVITY = 0.5
JUMP = -10
PIPE_SPEED = 3
PIPE_GAP = 150

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

# Load and remove background of bird images for animation
def load_bird_images(path_up, path_down):
    bird_up = remove_bg(path_up)
    bird_down = remove_bg(path_down)
    bird_up = pygame.transform.scale(bird_up, (40, 40))
    bird_down = pygame.transform.scale(bird_down, (40, 40))
    return bird_up, bird_down

# Load background image
bg = pygame.image.load('background.jpg')  # Replace with your background image file name
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Game Over screen image
game_over_img = remove_bg('game_over.jpg')  # Replace with your game over image file name
game_over_img = pygame.transform.scale(game_over_img, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Fill the screen

# Bird class with animations and smoother jump
class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.radius = 15
        self.vel = 0
        self.image_up, self.image_down = load_bird_images('bird.png', 'bird.png')  # Add your paths
        self.image = self.image_up
        self.rotation = 0
        self.flap_count = 0  # Counter for the flap animation

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        screen.blit(rotated_image, (self.x - 20, self.y - 20))

    def move(self):
        self.vel += GRAVITY
        self.y += self.vel

        # Animation effect: alternate between flapping and falling
        if self.vel < -1:
            self.image = self.image_up
            self.flap_count += 1
            if self.flap_count % 2 == 0:  # Toggle between flapping images
                self.image = self.image_down
        elif self.vel > 1:
            self.image = self.image_down
        else:
            self.image = self.image_up
            self.flap_count = 0  # Reset the flap counter

    def jump(self):
        self.vel = JUMP

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

# Check for collision
def check_collision(bird, pipes):
    for pipe in pipes:
        if bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + pipe.width:
            if bird.y - bird.radius < pipe.top or bird.y + bird.radius > pipe.bottom:
                return True
    if bird.y - bird.radius < 0 or bird.y + bird.radius > SCREEN_HEIGHT:
        return True
    return False

# Draw text function
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Add difficulty progression based on score
def update_difficulty(score):
    global PIPE_SPEED, PIPE_GAP
    if score > 10:  # After score of 10, make the game harder
        PIPE_SPEED = 4
        PIPE_GAP = 140
    if score > 20:
        PIPE_SPEED = 5
        PIPE_GAP = 130

# Pause functionality
def toggle_pause():
    paused = False
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Press "P" to unpause
                    paused = False
        # Draw paused text
        draw_text("PAUSED", font, BLACK, SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2)
        pygame.display.update()

    return paused

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
                if event.key == pygame.K_p:  # Press "P" to pause the game
                    toggle_pause()

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

        # Update difficulty based on score
        update_difficulty(score)

        # Check collision with pipes
        if check_collision(bird, pipes):
            screen.blit(game_over_img, (0, 0))  # Display Game Over screen
            draw_text(f"Score: {score}", font, BLACK, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 50)
            draw_text("Press R to Restart", font, BLACK, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 100)
            pygame.display.update()

            # Wait for the player to press 'R' to restart or close the window
            restart = False
            while not restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        restart = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()  # Restart the game
                            restart = True
            break

        # Draw score
        draw_text(f"Score: {score}", font, BLACK, 10, 10)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
