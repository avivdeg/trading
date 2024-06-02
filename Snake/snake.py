import pygame
import time
import random

pygame.init()

# Define colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
grey = (169, 169, 169)
dark_grey = (105, 105, 105)

# Set display dimensions for the Nokia phone screen
phone_width = 400
phone_height = 300
phone_border = 20
button_panel_height = 200
screen_width = phone_width + 2 * phone_border
screen_height = phone_height + 2 * phone_border + button_panel_height

# Initialize display
dis = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Snake Game on Nokia Phone')

# Set clock
clock = pygame.time.Clock()
snake_block = 10
snake_speed = 15

# Fonts for score display and button labels
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 25)
button_font = pygame.font.SysFont("bahnschrift", 20)

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, green, [x[0] + phone_border, x[1] + phone_border + 50, snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [screen_width / 6, screen_height / 2])

def your_score(score):
    value = score_font.render("Score: " + str(score), True, yellow)
    dis.blit(value, [phone_border, phone_border + 10])

def draw_phone():
    # Draw phone body
    pygame.draw.rect(dis, dark_grey, [0, 0, screen_width, screen_height])
    
    # Draw phone screen
    pygame.draw.rect(dis, black, [phone_border, phone_border + 50, phone_width, phone_height])
    
    # Draw phone buttons
    button_labels = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["*", "0", "#"]
    ]
    
    button_width = 40
    button_height = 30
    button_spacing = 10
    start_x = (screen_width - (3 * button_width + 2 * button_spacing)) // 2
    start_y = screen_height - button_panel_height + 50
    
    for i in range(4):
        for j in range(3):
            x = start_x + j * (button_width + button_spacing)
            y = start_y + i * (button_height + button_spacing)
            pygame.draw.ellipse(dis, grey, [x, y, button_width, button_height])
            label = button_font.render(button_labels[i][j], True, black)
            label_rect = label.get_rect(center=(x + button_width / 2, y + button_height / 2))
            dis.blit(label, label_rect)

def gameLoop():
    game_over = False
    game_close = False

    x1 = phone_width / 2
    y1 = phone_height / 2

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    foodx = round(random.randrange(0, phone_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, phone_height - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            dis.fill(blue)
            draw_phone()
            message("You Lost! Press Q-Quit or C-Play Again", red)
            your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        x1 += x1_change
        y1 += y1_change

        # Allow snake to go through walls
        if x1 >= phone_width:
            x1 = 0
        elif x1 < 0:
            x1 = phone_width - snake_block
        if y1 >= phone_height:
            y1 = 0
        elif y1 < 0:
            y1 = phone_height - snake_block

        dis.fill(black)
        draw_phone()
        pygame.draw.rect(dis, red, [foodx + phone_border, foody + phone_border + 50, snake_block, snake_block])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        your_score(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, phone_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, phone_height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()
