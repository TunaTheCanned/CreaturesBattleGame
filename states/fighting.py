import pygame

from source import button
from source.game_state import GameState
from states.state import State
from source.moves import perform_move

class FightingState(State):
    def __init__(self, game):
        super().__init__(game)

        try:
            self.bg_image = pygame.image.load("resources/background_fight.png").convert()
        except FileNotFoundError:
            print("Error: File not found")
            self.bg_image = None

        self.current_turn = 0
        self.turns = 1
        self.move_buttons = []

        self.p1_sprite_pos = None
        self.p2_sprite_pos = None
        self.p1_stats_pos = None
        self.p2_stats_pos = None
        self.p1_hp_pos = None
        self.p2_hp_pos = None
        self.turn_text_pos = None
        self.buttons_y = None
        self.button_size = None
        self.button_gap = None
        self.log_pos = None
        self.log_message = []
        self.log_duration = 5.0
        self.log_timer = 0.0
        self.p1_stats_x = None
        self.p2_stats_x = None
        self.p1_stats_y = None
        self.p2_stats_y = None
        self.player_name_y = None
        self.p1_name_pos = None
        self.p2_name_pos = None

        for i in range(4):
            btn = button.Button("", "black", self.font, "white",
                                200, 60, 5,
                                "black", 3, self.game.screen, True)
            btn.set_position(((self.game.get_width() - 200 * 4 + 20 * 3) // 2)+i*(200 + 20), (self.game.get_height() - 60 - 20))
            self.move_buttons.append(btn)

        self.update_move_buttons()
        self.update_layout()

        try:
            with open("resources/battlelog.txt", "a") as self.f:
                self.f.write("\n")
                self.f.write("===============================================\n")
                self.f.write("NEW GAME\n")
                self.f.write("===============================================\n")
        except Exception as e:
            print(f"Battle log init failed: {e}")



    def update_move_buttons(self):

        for i in range(4):
            if i < len(self.game.players[self.current_turn].creature.moves):
                self.move_buttons[i].text = self.game.players[self.current_turn].creature.moves[i]
                self.move_buttons[i].text_surface = self.move_buttons[i].font.render(self.move_buttons[i].text, True, self.move_buttons[i].text_color)
            else:
                self.move_buttons[i].text = "none"
                self.move_buttons[i].text_surface = self.move_buttons[i].font.render(self.move_buttons[i].text, True, self.move_buttons[i].text_color)

    def game_over(self):
        self.game.message_text = f"{self.game.players[self.current_turn].creature.name} wins"
        self.game.message_duration = 1.0
        self.game.message_next_state = GameState.START_MENU
        self.game.change_state(GameState.MESSAGE)

    def use_move(self, move_name):
        attacker = self.game.players[self.current_turn].creature
        defender = self.game.players[1 - self.current_turn].creature
        result = perform_move(move_name, attacker, defender)
        try:
            with open("resources/battlelog.txt", "a") as self.f:
                self.f.write(f"Turn {self.turns}: {result}\n")
        except Exception as e:
            print(f"{move_name} failed: {e}")

        self.log_message = [result]
        self.log_timer = self.log_duration
        self.turns += 1

        if defender.hp <= 0:
            self.game_over()
            return

        self.end_turn()

    def handle_event(self, event):
        for btn in self.move_buttons:
            btn.handle_events(event)
            if btn.consume_click():
                self.use_move(btn.text)


    def end_turn(self):
        defender = self.game.players[1 - self.current_turn].creature
        messages = self.apply_status_effects(defender)
        if messages:
            self.log_message.extend(messages)
            self.log_timer = self.log_duration

            try:
                with open("resources/battlelog.txt", "a") as f:
                    for msg in messages:
                        f.write(f"Turn {self.turns}: {msg}\n")
            except Exception as e:
                print(f"status effect log failed: {e}")

        if defender.hp <= 0:
            self.game_over()
            return

        self.current_turn = 1 - self.current_turn
        self.update_move_buttons()

    def update(self, dt):
        if self.log_timer > 0:
            self.log_timer -= dt
            if self.log_timer < 0:
                self.log_timer = 0

    def apply_status_effects(self, creature):
        messages = []

        for effect in creature.status_effects[:]:
            if effect["type"] == "POISON":
                creature -= effect["damage"]
                if creature.hp <= 0:
                    return messages
                messages.append(f"{creature.name} takes {effect['damage']} poison damage")

            elif effect["type"] == "REGEN":
                creature += effect["damage"]
                if creature.hp > creature.max_hp:
                    creature.hp = creature.max_hp
                messages.append(f"{creature.name} regenerates {effect['damage']} health points")

            effect["turns_left"] -= 1
            if effect["turns_left"] <= 0:
                creature.status_effects.remove(effect)

        return messages


    def draw_healthbar(self, creature, x, y):
        width = int(self.game.screen.get_width() * 0.18)
        height = int(self.game.screen.get_height() * 0.025)

        pygame.draw.rect(self.game.screen, (80, 80, 80), (x, y, width, height))
        ratio = creature.hp / creature.max_hp
        ratio = max(0, min(1, ratio))
        pygame.draw.rect(self.game.screen, (0, 200,  0), (x, y, int(width * ratio), height))
        pygame.draw.rect(self.game.screen, (0, 0, 0), (x, y, width, height), 2)


    def draw(self):
        if self.bg_image:
            self.game.renderer.draw_image(self.bg_image, (0, 0),
                                          (self.game.get_width(), self.game.get_height()))
        else:
            self.game.renderer.clear((60, 60, 60))

        player1 = self.game.players[0].creature
        player2 = self.game.players[1].creature

        sprite_size = (int(self.game.get_width() * 0.25), int(self.game.get_height() * 0.35))
        self.game.renderer.draw_image(player1.sprite, self.p1_sprite_pos, sprite_size)
        self.game.renderer.draw_text(player1.name, (255, 255, 255), (self.p1_hp_pos[0], self.p1_hp_pos[1] - int(self.game.get_height() * 0.06)))

        self.game.renderer.draw_image(player2.sprite, self.p2_sprite_pos, sprite_size)
        self.game.renderer.draw_text(player2.name, (255, 255, 255), (self.p2_hp_pos[0], self.p2_hp_pos[1] - int(self.game.get_height() * 0.06)))

        self.draw_healthbar(player1, *self.p1_hp_pos)
        self.draw_healthbar(player2, *self.p2_hp_pos)

        line_gap = int(self.game.get_height() * 0.06)
        self.game.renderer.draw_text("Health: " + str(player1.hp), (255, 255, 255), (self.p1_stats_x, self.p1_stats_y))
        self.game.renderer.draw_text("Attack: " + str(player1.attack), (255, 255, 255), (self.p1_stats_x, self.p1_stats_y + line_gap))
        self.game.renderer.draw_text("Defense: " + str(player1.defense), (255, 255, 255), (self.p1_stats_x, self.p1_stats_y + 2*line_gap))
        self.game.renderer.draw_text("Evasion: " + str(player1.evasion), (255, 255, 255), (self.p1_stats_x, self.p1_stats_y + 3 * line_gap))

        self.game.renderer.draw_text("Health: " + str(player2.hp), (255, 255, 255), (self.p2_stats_x, self.p2_stats_y))
        self.game.renderer.draw_text("Attack: " + str(player2.attack), (255, 255, 255), (self.p2_stats_x, self.p2_stats_y + line_gap))
        self.game.renderer.draw_text("Defense: " + str(player2.defense), (255, 255, 255), (self.p2_stats_x, self.p2_stats_y + 2*line_gap))
        self.game.renderer.draw_text("Evasion: " + str(player2.evasion), (255, 255, 255), (self.p2_stats_x, self.p2_stats_y + 3*line_gap))

        self.game.renderer.draw_text(f"Player {self.current_turn + 1} turn", (255, 255, 255), self.turn_text_pos)

        self.game.renderer.draw_text(f"Player 1", (255, 255, 255), self.p1_name_pos)
        self.game.renderer.draw_text(f"Player 2", (255, 255, 255), self.p2_name_pos)

        if self.log_timer > 0 and self.log_message:
            x, y = self.log_pos
            spacing = int(self.game.get_width() * 0.04)
            for i, msg in enumerate(self.log_message):
                self.game.renderer.draw_small_text(msg, 25,(x, y + i * spacing))

        for btn in self.move_buttons:
            btn.draw()

    def update_layout(self):
        width = self.game.get_width()
        height = self.game.get_height()
        sprite_w = int(width * 0.25)
        sprite_h = int(height * 0.35)
        left_x = int(width *0.05)
        right_x = int(width * 0.95 - sprite_w)
        sprite_y = int(height * 0.15)
        player_name_y = int (height * 0.1)
        self.p1_sprite_pos = (left_x, sprite_y)
        self.p2_sprite_pos = (right_x, sprite_y)
        self.p1_name_pos = (left_x, player_name_y)
        self.p2_name_pos = (right_x, player_name_y)

        bar_offset = int(height * 0.1)
        stats_offset = int(height * 0.05)
        self.p1_hp_pos = (left_x, sprite_y + sprite_h + bar_offset)
        self.p2_hp_pos = (right_x, sprite_y + sprite_h + bar_offset)
        self.p1_stats_x = left_x
        self.p1_stats_y = (self.p1_hp_pos[1] + stats_offset)
        self.p2_stats_x = right_x
        self.p2_stats_y = (self.p2_hp_pos[1] + stats_offset)

        self.turn_text_pos = (width/2 - int(width * 0.08), int(height * 0.035))
        self.button_size = (int(width * 0.18), int(height * 0.07))
        self.button_gap = int(width * 0.02)
        self.buttons_y = int(height * 0.9)



        total_width = 4 * self.button_size[0] + 3 * self.button_gap
        start_x = (width - total_width) / 2
        self.log_pos = (width * 0.5 - width*0.2 , height * 0.55)

        for i, btn in enumerate(self.move_buttons):
            btn.set_size(*self.button_size)
            btn.set_position(start_x + i * (self.button_size[0] + self.button_gap), self.buttons_y)

    def on_resize(self):
        self.update_layout()