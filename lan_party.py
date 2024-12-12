import random
import pygame
import pygame.time
from pygame.locals import *
from abc import ABC, abstractmethod


class Screen(ABC):
    def __init__(self, screen):
        self.screen = screen
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.background = None
        self.font = pygame.font.SysFont('Arial', 80)

    @abstractmethod
    def draw(self):
        ...

    @abstractmethod
    def play_music(self):
        ...

    @staticmethod
    def stop_music():
        pygame.mixer.music.stop()


class Button:
    def __init__(self, x, y, image_path, scale=None, hover_image_path=None):
        self.image = pygame.image.load(image_path).convert_alpha()
        if scale:
            self.image = pygame.transform.scale(self.image, scale)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.hover_image = None
        if hover_image_path:
            self.hover_image = pygame.image.load(hover_image_path).convert_alpha()
            if scale:
                self.hover_image = pygame.transform.scale(self.hover_image, scale)
        self.is_hovered = False

    def draw(self, screen):
        """Draw the button on the screen."""
        if self.is_hovered and self.hover_image:
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def is_clicked(self, event):
        """Check if the button is clicked."""
        if event.type == MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)


class TitleScreen(Screen, ABC):
    def __init__(self, screen, party):
        super().__init__(screen)
        self.background = self.title_background = pygame.image.load('Images/Title.png').convert()
        self.background = pygame.transform.scale(self.background, (1920, 1080))
        self.font = pygame.font.SysFont('Arial', 40)
        self.party = party

    def draw(self):
        self.screen.blit(self.background, (0, 0))

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load('Sounds/darkwave.wav')
        pygame.mixer.music.set_volume(0.1)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Loop the music (-1 means infinite loop)


class BasementScreen(Screen, ABC):
    def __init__(self, screen, party):
        super().__init__(screen)
        self.party = party
        self.background = self.basement_background = pygame.image.load('Images/Basement.png').convert()
        self.background = pygame.transform.scale(self.background, (1920, 1080))

        # Door Button (invisible)
        self.door_button = Button(240, 24, 'Images/Door_Button.png', (170, 192), "Images/Door_Button_on_Hover.png")

        # End Day Button
        self.end_d_button = Button(1375, 925, "Images/End_day_button1.png", (400, 125), "Images/End_day_button2.png")

        # Desk dimensions and spacing
        self.desk_width = 200  # Width of each desk
        self.desk_height = 200  # Height of each desk
        self.desk_spacing = 35  # Spacing between desks
        self.desks_per_row = 7  # Number of desks per row

        # Offsets to shift desks down and to the right
        self.horizontal_offset = 155  # Horizontal shift
        self.vertical_offset = 280  # Vertical shift

        # Desk image
        self.desk_image = pygame.image.load('Images/Desk.png').convert_alpha()
        self.desk_image = pygame.transform.scale(self.desk_image, (self.desk_width, self.desk_height))

        # Normal Gamer image
        self.normal_gamer_image = pygame.image.load('Images/Gamer.png').convert_alpha()
        self.normal_gamer_image = pygame.transform.scale(self.normal_gamer_image, (self.desk_width, self.desk_height))

        # Angry
        self.angry_gamer_image = pygame.image.load('Images/Gamer_Angry.png').convert_alpha()
        self.angry_gamer_image = pygame.transform.scale(self.angry_gamer_image, (self.desk_width, self.desk_height))
        # Rich
        self.rich_gamer_image = pygame.image.load('Images/Gamer_Rich.png').convert_alpha()
        self.rich_gamer_image = pygame.transform.scale(self.rich_gamer_image, (self.desk_width, self.desk_height))

        # Star
        self.star_gamer_image = pygame.image.load('Images/Gamer_Star.png').convert_alpha()
        self.star_gamer_image = pygame.transform.scale(self.star_gamer_image, (self.desk_width, self.desk_height))

        # Star
        self.calm_gamer_image = pygame.image.load('Images/Gamer_Calm.png').convert_alpha()
        self.calm_gamer_image = pygame.transform.scale(self.calm_gamer_image, (self.desk_width, self.desk_height))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_desks()
        self.draw_gamer()
        self.end_d_button.draw(self.screen)
        self.door_button.draw(self.screen)
        self.draw_stats()

    def draw_stats(self):
        turns = self.party.turns_remaining
        coin = self.party.coin
        rep = self.party.rep

        turns_surface = self.font.render(f"{turns}", False, (0, 0, 0))
        coin_surface = self.font.render(f"{coin}", False, (0, 0, 0))
        rep_surface = self.font.render(f"{rep}", False, (0, 0, 0))

        self.screen.blit(turns_surface, (1080, 15))
        self.screen.blit(coin_surface, (1780, 15))
        self.screen.blit(rep_surface, (1400, 15))

    def draw_desks(self):
        num_desks = self.party.desks
        for i in range(num_desks):
            # Calculate row and column
            row = i // self.desks_per_row
            col = i % self.desks_per_row

            # Calculate position with offsets
            x = col * (self.desk_width + self.desk_spacing) + self.horizontal_offset
            y = row * (self.desk_height + self.desk_spacing) + self.vertical_offset

            # Draw desk
            self.screen.blit(self.desk_image, (x, y))

    def draw_gamer(self):
        for i, gamer in enumerate(self.party.in_party):
            # Calculate row and column
            row = i // self.desks_per_row
            col = i % self.desks_per_row

            x = col * (self.desk_width + self.desk_spacing) + self.horizontal_offset
            y = row * (self.desk_height + self.desk_spacing) + self.vertical_offset

            # Adjust gamer position to center on the desk
            gamer_x = x
            gamer_y = y + 10

            # Determine the correct image based on gamer type
            if gamer.name == 'Normal Gamer':
                image = self.normal_gamer_image
            elif gamer.name == 'Rich Gamer':
                image = self.rich_gamer_image
            elif gamer.name == 'Angry Gamer':
                image = self.angry_gamer_image
            elif gamer.name == 'Star Gamer':
                image = self.star_gamer_image
            elif gamer.name == 'Calm Gamer':
                image = self.calm_gamer_image
            else:
                image = self.normal_gamer_image  # Fallback in case of unknown type

            # Draw gamer image
            self.screen.blit(image, (gamer_x, gamer_y))

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load('Sounds/dark.wav')  # Replace with your music file path
        pygame.mixer.music.set_volume(0.1)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Loop the music (-1 means infinite loop)


class ShopScreen(Screen, ABC):
    def __init__(self, screen, party):
        super().__init__(screen)
        self.party = party
        self.background = pygame.image.load('Images/Shop.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (1920, 1080))

        # Fonts for stats
        self.stats_font = pygame.font.SysFont('Arial', 80)

        # Next Day Button
        self.next_d_button = Button(1340, 900, "Images/Next_Day_Button1.png", (400, 125), "Images/Next_Day_Button2.png")

        # Font for labels
        self.font = pygame.font.SysFont('Arial', 30)

        # Shop Items (Desks and Gamers)
        self.items = [
            {"name": "New Desk", "cost": 5, "currency": "coin", "image": 'Images/Desk.png',
             "action": self.upgrade_desk},
            {"name": "Rich Gamer", "cost": 10, "currency": "rep", "image": 'Images/Gamer_Rich.png',
             "action": self.add_rich_gamer},
            {"name": "Angry Gamer", "cost": 8, "currency": "rep", "image": 'Images/Gamer_Angry.png',
             "action": self.add_angry_gamer},
            {"name": "Normal Gamer", "cost": 5, "currency": "rep", "image": 'Images/Gamer.png',
             "action": self.add_normal_gamer},
            {"name": "Star Gamer", "cost": 25, "currency": "rep", "image": 'Images/Gamer_Star.png',
             "action": self.add_star_gamer},
            {"name": "Calm Gamer", "cost": 15, "currency": "rep", "image": 'Images/Gamer_Calm.png',
             "action": self.add_calm_gamer},
        ]

        # Positioning adjustments
        self.grid_start_x = 150  # Shift the grid to the right
        self.grid_start_y = 260  # Shift the grid down
        self.button_width = 150  # Width of each button
        self.button_height = 150  # Height of each button
        self.button_padding = 300  # Space between buttons

        # Item Buttons
        self.item_buttons = []
        for i, item in enumerate(self.items):
            x = self.grid_start_x + (i % 3) * (self.button_width + self.button_padding)
            y = self.grid_start_y + (i // 3) * (self.button_height + self.button_padding)
            button = Button(x, y, item["image"], scale=(self.button_width, self.button_height))
            self.item_buttons.append({"button": button, "item": item})

    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Draw stats
        self.draw_stats()

        # Draw item buttons and labels
        for item_button in self.item_buttons:
            item_button["button"].draw(self.screen)

            # Render item name
            name_surface = self.font.render(item_button["item"]["name"], True, (0, 0, 0))
            x, y = item_button["button"].rect.topleft

            # Adjust name position above the button
            name_x = x + (self.button_width // 2) - (name_surface.get_width() // 2)
            name_y = y - 50

            self.screen.blit(name_surface, (name_x, name_y))

            # Render item cost
            cost_surface = self.font.render(
                f"Cost: {item_button['item']['cost']} {item_button['item']['currency'].capitalize()}",
                True, (0, 0, 0)
            )
            cost_x = x + (self.button_width // 2) - (cost_surface.get_width() // 2)
            cost_y = y + self.button_height + 10

            self.screen.blit(cost_surface, (cost_x, cost_y))

        # Draw next day button
        self.next_d_button.draw(self.screen)

    def draw_stats(self):
        turns = self.party.turns_remaining
        coin = self.party.coin
        rep = self.party.rep

        turns_surface = self.stats_font.render(f"{turns}", True, (0, 0, 0))
        coin_surface = self.stats_font.render(f"{coin}", True, (0, 0, 0))
        rep_surface = self.stats_font.render(f"{rep}", True, (0, 0, 0))

        # Draw stats on the screen
        self.screen.blit(turns_surface, (1740, 180))
        self.screen.blit(coin_surface, (1740, 360))
        self.screen.blit(rep_surface, (1740, 270))

    def upgrade_desk(self):
        self.party.upgrade_desk()

    def add_rich_gamer(self):
        self.party.deck.append(Gamer("Rich Gamer", rep=2, coin=1, rage=0))

    def add_angry_gamer(self):
        self.party.deck.append(Gamer("Angry Gamer", rep=2, coin=0, rage=1))

    def add_normal_gamer(self):
        self.party.deck.append(Gamer("Normal Gamer", rep=1, coin=0, rage=0))

    def add_star_gamer(self):
        self.party.deck.append(Gamer("Star Gamer", rep=5, coin=2, rage=0, star=1))

    def add_calm_gamer(self):
        self.party.deck.append(Gamer(name="Calm Gamer", rep=1, coin=0, rage=-1))

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load('Sounds/dope.wav')
        pygame.mixer.music.set_volume(0.05)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Loop the music (-1 means infinite loop)


class WinScreen(Screen, ABC):
    def __init__(self, screen):
        super().__init__(screen)
        self.background = self.shop_background = pygame.image.load('Images/Win_Screen.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (1920, 1080))

    def draw(self):
        self.screen.blit(self.background, (0, 0))

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load('Sounds/money.wav')
        pygame.mixer.music.set_volume(0.1)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Loop the music (-1 means infinite loop)


class RageScreen(Screen, ABC):
    def __init__(self, screen):
        super().__init__(screen)
        self.background = self.shop_background = pygame.image.load('Images/Rage_Screen.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (1920, 1080))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.enter_to_continue()

    def play_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load('Sounds/drone synth1.wav')
        pygame.mixer.music.set_volume(0.1)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Loop the music (-1 means infinite loop)

    def enter_to_continue(self):
        text = self.font.render(f"Press enter to continue", False, (255, 255, 255))
        self.screen.blit(text, (0, 0))


class OverFlowScreen(RageScreen):
    def __init__(self, screen):
        super().__init__(screen)
        self.background = self.shop_background = pygame.image.load('Images/Overflow_Screen.png').convert_alpha()
        self.background = pygame.transform.scale(self.background, (1920, 1080))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.enter_to_continue()


class GameState:
    def __init__(self):
        # initialize pygame
        pygame.init()
        pygame.display.set_caption('Lan Party')

        # Screen settings
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption('Lan Party')
        icon_image = pygame.image.load('Images/Logo.png')
        pygame.display.set_icon(icon_image)

        # Screens
        self.party = Party()
        self.title_screen = TitleScreen(self.screen, self.party)
        self.party_screen = BasementScreen(self.screen, self.party)
        self.shop_screen = ShopScreen(self.screen, self.party)
        self.rage_screen = RageScreen(self.screen)
        self.overflow_screen = OverFlowScreen(self.screen)
        self.current_screen = self.title_screen
        self.cash_sound = pygame.mixer.Sound('Sounds/cash.mp3')
        self.cash_sound.set_volume(0.1)
        self.win_screen = WinScreen(self.screen)

        # Shared assets
        self.clock = pygame.time.Clock()

        # Play music for the starting screen
        self.current_screen.play_music()

    def purchase_shop_item(self, item):
        currency = item["currency"]
        cost = item["cost"]

        # Check if the player has enough currency
        if getattr(self.party, currency) >= cost:
            # Perform the item's action
            action_result = item["action"]()

            # Only deduct cost if the action doesn't handle it
            if action_result is None or action_result is True:  # Assume success if no return value
                if action_result is None:  # Action like adding gamers doesn't deduct coins
                    setattr(self.party, currency, getattr(self.party, currency) - cost)  # Deduct currency
                print(f"Purchased {item['name']}!")
                self.cash_sound.play()  # Play cash sound on success
            else:
                print(f"Failed to purchase {item['name']}!")
        else:
            print(f"Not enough {currency} to purchase {item['name']}!")

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                # Handles Title Screen Actions
                if isinstance(self.current_screen, TitleScreen):
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            self.current_screen = self.party_screen
                            self.current_screen.play_music()
                            self.party.start_day()
                            print(self.party.deck)
                        elif event.key == K_ESCAPE:
                            running = False

                # Basement Screen
                if isinstance(self.current_screen, BasementScreen):
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            running = False
                    elif self.current_screen.end_d_button.is_clicked(event):
                        self.party.end_day()
                        self.current_screen = self.shop_screen
                        self.current_screen.play_music()
                        break
                    elif event.type == MOUSEMOTION:
                        self.current_screen.door_button.update_hover(event.pos)
                        self.current_screen.end_d_button.update_hover(event.pos)
                    elif self.current_screen.door_button.is_clicked(event):
                        self.party.let_in_party(self)

                # Raged or Overflow Screen
                if isinstance(self.current_screen, (RageScreen, OverFlowScreen)):
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            self.current_screen = self.shop_screen
                            self.current_screen.play_music()

                # Shop Screen
                if isinstance(self.current_screen, ShopScreen):
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            running = False
                    elif self.current_screen.next_d_button.is_clicked(event):
                        self.current_screen = self.party_screen
                        self.current_screen.play_music()
                        self.party.start_day()
                        break
                    elif event.type == MOUSEBUTTONUP:
                        for item_button in self.current_screen.item_buttons:
                            if item_button["button"].is_clicked(event):
                                self.purchase_shop_item(item_button["item"])
                    elif event.type == MOUSEMOTION:
                        self.current_screen.next_d_button.update_hover(event.pos)
                        for item_button in self.current_screen.item_buttons:
                            item_button["button"].update_hover(event.pos)

            # Render the current screen
            self.current_screen.draw()

            # Update the display
            pygame.display.flip()

            self.clock.tick(60)


class Gamer:
    def __init__(self, name, rep=0, coin=0, rage=0, ability=None, cost=1, star=False):
        self.name = name
        self.rep = rep
        self.coin = coin
        self.rage = rage
        self.ability = ability
        self.cost = cost
        self.star = star

    def __str__(self):
        return (f"I am a {self.name},"
                f" I give {self.rep}REP and {self.coin}COIN"
                f"I give {self.rage} RAGE"
                f"I have this ability:{self.ability}"
                f"I cost {self.cost}")

    def __repr__(self):
        return f"Gamer({self.name}, {self.rep}, {self.coin}, {self.rage}, {self.ability}, {self.cost})"

    def use_ability(self, party):
        if self.ability:
            self.ability(party)


class Party:
    def __init__(self):
        self.deck = [
            Gamer("Normal Gamer", 1, 0, 0, None, 0, 0),
            Gamer("Normal Gamer", 1, 0, 0, None, 0, 0),
            Gamer("Normal Gamer", 1, 0, 0, None, 0, 0),
            Gamer("Angry Gamer", 2, 0, 1, None, 0, 0),
            Gamer("Angry Gamer", 2, 0, 1, None, 0, 0),
            Gamer("Angry Gamer", 2, 0, 1, None, 0, 0),
        ]
        self.in_party = []
        self.desks = 5
        self.coin = 0
        self.rage_level = 0
        self.star_level = 0
        self.rep = 0
        self.turns_remaining = 25
        self.desk_cost = 5

    def upgrade_desk(self):
        if self.coin >= self.desk_cost:
            self.desks += 1
            self.desk_cost += 2
            print(f"Desk upgraded! Total desks: {self.desks}, Remaining coins: {self.coin}")
            return True
        else:
            print("Not enough coins to upgrade desk!")
            return False

    def start_day(self):
        # Shuffles cards and signals a new day has started
        self.shuffle_gamers()

    def end_day(self, raged=False, over_flow=False, win=False):
        if raged:
            print(f"Raged to hard mom ended the party")

        elif over_flow:
            print("You overflowed! Mom ended the party!")

        elif win:
            print("You win!")

        else:
            for gamer in self.in_party:
                self.coin += gamer.coin
                self.rep += gamer.rep

        # Refills deck
        self.deck.extend(self.in_party)

        # Clears the in party list for next day
        self.in_party = []

        # Sets turn count
        self.turns_remaining -= 1

        # Resets rage level
        self.rage_level = 0

        self.star_level = 0

        print(f"\nEND OF DAY REPORT\n----------------\n\n"
              f"COIN: {self.coin}\nREP: {self.rep}\nTurns remaining:{self.turns_remaining}\n rage:{self.rage_level}")

    def let_in_party(self, game_state):
        # Draw the next gamer
        next_gamer = self.deck.pop(0)

        # Add to the party
        self.in_party.append(next_gamer)
        print(f"You've let {next_gamer.name} into the party!")
        print(f"Current party members: {len(self.in_party)}")

        # adds gamers rage to rage_level
        self.rage_level += next_gamer.rage
        self.star_level += next_gamer.star
        print(self.rage_level)
        # Check for the party-ending rage condition
        if len(self.in_party) > self.desks:
            self.end_day(over_flow=True)
            game_state.current_screen = game_state.overflow_screen
            game_state.current_screen.play_music()
            return

        elif self.rage_level >= 3:
            self.end_day(raged=True)
            game_state.current_screen = game_state.rage_screen
            game_state.current_screen.play_music()
            return

        elif self.star_level == 4:
            game_state.current_screen = game_state.win_screen
            game_state.current_screen.play_music()
            return

    def shuffle_gamers(self):
        random.shuffle(self.deck)
