import pygame
import config, utils
from components.button import Button
from components.boat import Boat
from components.goat import Goat
from components.wolf import Wolf
from components.cabbage import Cabbage
from components.row_button import RowButton
from views import menu

def view(game):
    vw = game.vw
    vh = game.vh

    game.set_background(config.images.get("background"))

    lose_conditions = [[Goat, Cabbage], [Wolf, Goat]]

    land_width = vw(30)
    land_left = config.images.get("land_left")
    land_right = config.images.get("land_right")

    land_left_h = land_width * (land_left.get_height() / land_left.get_width())
    land_left = pygame.transform.scale(land_left, (int(land_width), int(land_left_h)))

    land_right_h = land_width * (land_right.get_height() / land_right.get_width())
    land_right = pygame.transform.scale(land_right, (int(land_width), int(land_right_h)))

    boat_padding = vw(2)
    boat_width = vw(18)
    boat = Boat(land_width + boat_padding, vw(100) - land_width - boat_width - boat_padding, vh(90), boat_width)

    row_button_width = vw(8)
    row_button = RowButton(vw(50) - row_button_width // 2, vh(40), w= row_button_width)
    row_button.on_click = lambda: boat.row(callback= lambda : row_button.flip())

    objects_count = 3
    land_object_width = vw(9)
    objects_left = []
    object_in_boat = {"class": None}
    objects_right = []

    def boat_click_action():
        if boat.moving:
            return
        
        boat.hold(None)
        left = list(map(type, objects_left))
        right = list(map(type, objects_right))
        if boat.position == "left":
            left.append(object_in_boat["class"])
            define_objects(left = left)
        if boat.position == "right":
            right.append(object_in_boat["class"])
            define_objects(right = right)

        object_in_boat["class"] = None            
    
    def get_land_object_click_function(land_arr, obj, condition_func):
        def func():
            if boat.moving or not condition_func():
                return
            
            if boat.holding is not None and object_in_boat["class"] is not None:
                return
            
            index = land_arr.index(obj)
            object_in_boat["class"] = type(land_arr[index])
            boat.hold( land_arr[index].image)
            del land_arr[index]

        return func

    def define_objects(left = None, right = None):
        #Left Land
        if left is not None:
            objects_left.clear()
            gap = (land_width - objects_count * land_object_width) / (objects_count + 1)
            bottom = vh(100) - land_left_h // 4
            for i, Obj in enumerate(left):
                obj = Obj(gap * (i + 1) + land_object_width * i, bottom, w = land_object_width)
                obj.on_click = get_land_object_click_function(objects_left, obj, lambda : boat.position == "left")
                objects_left.append(obj)
        
        #Right Land
        if right is not None:
            objects_right.clear()
            gap = (land_width - objects_count * land_object_width) / (objects_count + 1)
            bottom = vh(100) - land_right_h // 4
            for i, Obj in enumerate(right):
                obj = Obj(vw(100) - (gap * (i + 1) + land_object_width * (i + 1)), bottom, w = land_object_width)
                obj.on_click = get_land_object_click_function(objects_right, obj, lambda : boat.position == "right")
                objects_right.append(obj)

    def lose(condition):
        end_screen = game.gameDisplay.copy()
        end_screen.fill((150, 150, 150), special_flags = pygame.BLEND_MULT)

        font = config.font_secondary.xxl
        text_color = config.colors["text"]
        game_over_text = font.render("Game Over", True, text_color)
        game_over_width = game_over_text.get_width()
        game_over_height = game_over_text.get_height()

        ate_text = font.render("ate", True, text_color)
        ate_text_width = ate_text.get_width()
        ate_text_height = ate_text.get_height()

        board_padding = 16 #Pixels

        entity_width = vw(10)
        gap = 20 + ate_text_width
        board_y = vh(15)

        eater = condition[0].__name__.lower()
        prey = condition[1].__name__.lower()
        eater = config.images.get(eater)
        prey = config.images.get(prey)
        eater = utils.scale_image_maintain_ratio(eater, w = entity_width)
        prey = utils.scale_image_maintain_ratio(prey, w = entity_width)
        eater_h = eater.get_height()
        prey_h = prey.get_height()

        board_w = board_padding * 2 + gap + entity_width * 2
        board_h = board_padding * 2 + game_over_height + max(eater_h, prey_h)

        board_rect = pygame.Rect(vw(50) - board_w // 2, board_y, board_w, board_h)

        pygame.draw.rect(end_screen, config.colors["bg"], board_rect)
        pygame.draw.rect(end_screen, config.colors["text"], board_rect, 2)

        end_screen.blit(game_over_text, (vw(50) - game_over_width // 2, board_y + board_padding))
        end_screen.blit(eater, (vw(50) - entity_width - gap // 2, board_y + board_h - board_padding - eater_h))
        end_screen.blit(prey, (vw(50) + gap // 2, board_y + board_h - board_padding - prey_h))
        end_screen.blit(ate_text, (vw(50) - ate_text_width // 2, board_y + board_h - board_padding - min(eater_h, prey_h) // 2 - ate_text_height // 2))

        home_button_font = config.font_primary.xxl
        home_button = Button(vw(50), board_y + board_h + vh(20), "Back Home", h = vh(25), font = home_button_font)
        home_button.on_click = lambda : game.set_screen(menu.view)

        game.set_background(end_screen)
        game.update_function = home_button.update

    def check_win():
        right = list(map(type, objects_right))
        if utils.compare_arrays_unordered(right, [Goat, Cabbage, Wolf]):
            print("WON")
    
    def check_lose():
        left = list(map(type, objects_left))
        right = list(map(type, objects_right))
        for cond in lose_conditions:
            if boat.x <= boat.left_x:
                if utils.compare_arrays_unordered(right, cond):
                    lose(cond)
            if boat.x >= boat.right_x:
                if utils.compare_arrays_unordered(left, cond):
                    lose( cond)

    define_objects([Goat, Cabbage, Wolf], [])
    boat.on_click = boat_click_action

    def draw():
        game.gameDisplay.blit(land_left, (0, int(vh(100) - 0.9 * land_left.get_height())))
        game.gameDisplay.blit(land_right, (int(vw(100) - land_width), int(vh(100) - 0.9 * land_right.get_height())))

    def update():
        draw()
        boat.update()
        row_button.update()

        for obj in objects_left:
            obj.update()
        for obj in objects_right:
            obj.update()

        check_win()
        check_lose()

    game.update_function = update
