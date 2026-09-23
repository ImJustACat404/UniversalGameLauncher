import pygame
import tkinter as tk
from tkinter import ttk, filedialog
import sys
import threading
import queue
from Core import Core

pygame.init()

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (180, 180, 255)
GREEN = (25, 220, 18)
CHAMBRAY = (51, 66, 138)
EAST_BAY = (39, 48, 93)
DARK_BAY = (22, 29, 69)
WAIKAWA_GRAY = (84, 96, 155)


# Fonts
FONT = pygame.font.SysFont("Arial", 20)

# Others
WINDOW_TITLE = "Universal Game Launcher"


def wrap_text(text, font, max_width):
    """Splits text into lines that fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        elif font.size(current_line)[0] >= max_width:
            # A very long word
            long_word_split_line = ""
            for letter in current_line:
                if font.size(long_word_split_line + letter)[0] <= max_width:
                    long_word_split_line += letter
                else:
                    lines.append(long_word_split_line)
                    long_word_split_line = letter
            if font.size(f"{long_word_split_line} {word}".strip())[0] <= max_width:
                current_line = f"{long_word_split_line} {word}".strip()
            else:
                lines.append(long_word_split_line)
                current_line = word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return '\n'.join(lines)


def add_game_dialog():
    new_game = None

    def submit():
        nonlocal new_game
        new_game = Core.add_game(
            platform_var.get(),
            name_var.get(),
            icon_path.get(),
            banner_path.get(),
            info_var.get(),
            exe_path.get()
        )
        root.destroy()

    def browse_file(var, types):
        path = filedialog.askopenfilename(filetypes=types)
        if path:
            var.set(path)

    # Run Tkinter in its own root
    root = tk.Tk()
    root.title("Add New Game")
    root.geometry("400x400")
    root.resizable(False, False)

    platform_var = tk.StringVar(value="exe")
    name_var = tk.StringVar()
    icon_path = tk.StringVar()
    banner_path = tk.StringVar()
    info_var = tk.StringVar()
    exe_path = tk.StringVar()

    platforms = ["exe", "Steam", "Epic Games", "Origin"]

    ttk.Label(root, text="Platform:").pack(pady=5)
    ttk.OptionMenu(root, platform_var, platforms[0], *platforms).pack()

    ttk.Label(root, text="Game Name:").pack(pady=5)
    ttk.Entry(root, textvariable=name_var).pack(fill="x", padx=10)

    ttk.Label(root, text="Game info:").pack(pady=5)
    ttk.Entry(root, textvariable=info_var).pack(fill="x", padx=10)

    def make_browse_row(label, var, types):
        ttk.Label(root, text=label).pack(pady=5)
        frame = ttk.Frame(root)
        frame.pack(fill="x", padx=10)
        ttk.Entry(frame, textvariable=var, width=30).pack(side="left", expand=True, fill="x")
        ttk.Button(frame, text="Browse", command=lambda: browse_file(var, types)).pack(side="left")

    make_browse_row("Icon Path:", icon_path, [("Image Files", "*.png *.jpg *.ico *.jpeg")])
    make_browse_row("Banner Path:", banner_path, [("Image Files", "*.png *.jpg *.jpeg")])
    make_browse_row("Executable Path:", exe_path, [("Executables", "*.exe *.sh *.app"), ("All Files", "*.*")])

    ttk.Button(root, text="Add Game", command=submit).pack(pady=20)

    root.mainloop()

    return new_game


class GameLauncherUI:
    def __init__(self, width=1280, height=820):
        # Window params
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        # Game data
        self.games = []
        self.displayed_games = []
        self.selected_game = None
        self.note_input = ""
        self.scroll_offset = 0
        self.max_visible = 23
        self.line_height = 30
        self.list_top_gap = 115

        # Backspace control
        self.backspace_held = False
        self.backspace_timer = 0
        self.backspace_repeat_delay = 300
        self.backspace_repeat_rate = 50
        self.refresh_results = queue.Queue()
        self.refresh_status = ""
        self.favorite_ids = set(Core.get_favorite_games())
        self.active_filter = "A-Z"
        self.filter_buttons = {}

    def refresh_libraries(self):
        def refresh():
            errors = []
            for platform, update in (("Steam", Core.update_steam_db), ("Epic", Core.update_epic_db)):
                try:
                    update()
                except Exception as error:
                    errors.append(f"{platform}: {error}")
            self.refresh_results.put(errors)

        threading.Thread(target=refresh, name="library-refresh", daemon=True).start()

    def get_nav_buttons(self, screen_width):
        return {
            "add_game": pygame.Rect(screen_width - 240, 10, 100, 40),
            "add_account": pygame.Rect(screen_width - 130, 10, 100, 40),
            "remove_game": pygame.Rect(screen_width - 350, 10, 100, 40)
        }

    def get_game_action_buttons(self, screen_width):
        return {
            "favorite": pygame.Rect(screen_width - 270, 690, 240, 40),
            "launch": pygame.Rect(screen_width - 520, 640, 240, 40)
        }

    def get_filter_buttons(self):
        labels = ("A-Z", "Steam", "Epic", "Other", "Favorites")
        buttons = {}
        x = 20
        for label in labels:
            width = 110 if label == "Favorites" else 90
            buttons[label] = pygame.Rect(x, 65, width, 30)
            x += width + 10
        return buttons

    def apply_game_filter(self, selected_game=None, preserve_scroll=False):
        previous_scroll = self.scroll_offset
        previous_selection = self.selected_game
        if self.active_filter == "Favorites":
            games = [game for game in self.games
                     if (game.get_platform(), game.get_id()) in self.favorite_ids]
        elif self.active_filter == "A-Z":
            games = self.games.copy()
        else:
            games = [game for game in self.games if game.get_platform() == self.active_filter]

        self.displayed_games = sorted(games, key=lambda game: game.get_name().upper())
        if preserve_scroll:
            max_scroll = max(0, len(self.displayed_games) - self.max_visible)
            self.scroll_offset = min(previous_scroll, max_scroll)
        else:
            self.scroll_offset = 0
        self.selected_game = (self.displayed_games.index(selected_game)
                              if selected_game in self.displayed_games
                              else (min(previous_selection, len(self.displayed_games) - 1)
                                    if preserve_scroll and self.displayed_games
                                    else (0 if self.displayed_games else None)))
        if (preserve_scroll and self.selected_game is not None
                and self.selected_game < self.scroll_offset):
            self.scroll_offset = self.selected_game
        elif (preserve_scroll and self.selected_game is not None
              and self.selected_game >= self.scroll_offset + self.max_visible):
            self.scroll_offset = self.selected_game - self.max_visible + 1
        if self.selected_game is not None:
            self.note_input = self.displayed_games[self.selected_game].get_notes()
        else:
            self.note_input = ""

    def draw_nav_bar(self, screen_width):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, screen_width, 60))
        title = FONT.render(WINDOW_TITLE, True, WHITE)
        self.screen.blit(title, (20, 20))
        if self.refresh_status:
            status = FONT.render(self.refresh_status, True, WHITE)
            self.screen.blit(status, (250, 20))
        self.filter_buttons = self.get_filter_buttons()
        for label, rect in self.filter_buttons.items():
            color = BLUE if label == self.active_filter else DARK_GRAY
            pygame.draw.rect(self.screen, color, rect)
            text = FONT.render(label, True, WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))
        buttons = self.get_nav_buttons(screen_width)
        pygame.draw.rect(self.screen, BLUE, buttons["add_game"])
        pygame.draw.rect(self.screen, BLUE, buttons["add_account"])
        pygame.draw.rect(self.screen, BLUE, buttons["remove_game"])
        self.screen.blit(FONT.render("Add Game", True, WHITE), (buttons["add_game"].x + 5, buttons["add_game"].y + 10))
        self.screen.blit(FONT.render("Account", True, WHITE), (buttons["add_account"].x + 5, buttons["add_account"].y + 10))
        self.screen.blit(FONT.render("Remove", True, WHITE), (buttons["remove_game"].x + 5, buttons["remove_game"].y + 10))

    def draw_game_list(self, width, height):
        if len(self.displayed_games) == 0:
            return

        row_y = self.list_top_gap

        for i in range(self.scroll_offset, min(len(self.displayed_games), self.scroll_offset + self.max_visible)):
            game = self.displayed_games[i]

            if i == self.selected_game:
                pygame.draw.rect(self.screen, WAIKAWA_GRAY, (0, row_y, width - 550, self.line_height))

            self.screen.blit(game.get_icon(), (20, row_y + (self.line_height - game.get_icon().get_size()[1]) // 2))
            shortened_name = wrap_text(game.get_name(), FONT, 220).split('\n')[0]
            self.screen.blit(FONT.render(shortened_name, True, WHITE), (70, row_y + 5))
            self.screen.blit(FONT.render(f"Platform: {game.get_platform()}", True, WHITE), (300, row_y + 5))
            self.screen.blit(FONT.render(f"Last Played: {'Placeholder'}", True, WHITE), (480, row_y + 5))

            row_y += self.line_height

    def draw_game_banner(self, screen_width):
        if self.selected_game is None:
            return

        banner = self.displayed_games[self.selected_game].get_banner()
        x = screen_width - 270
        y = 70
        self.screen.blit(banner, (x, y))

    def draw_game_info(self, screen_width):
        if self.selected_game is None:
            return

        game = self.displayed_games[self.selected_game]
        game_info = wrap_text(game.get_info(), FONT, 220)
        x = screen_width - 520
        y = 70
        
        pygame.draw.rect(self.screen, GRAY, (x, y, 240, 560))
        for i, line in enumerate(game_info.split("\n")):
            self.screen.blit(FONT.render(line, True, BLACK), (x + 10, y + 10 + i * 20))

    def draw_notes(self, screen_width, screen_height):
        x = screen_width - 270
        y = 440
        pygame.draw.rect(self.screen, GRAY, (x, y, 240, 240))
        pygame.draw.rect(self.screen, BLACK, (x + 10, y + 10, 220, 220), 1)
        lines = self.note_input.split("\n")[-9:]
        for i, line in enumerate(lines):
            self.screen.blit(FONT.render(line, True, BLACK), (x + 15, y + 20 + i * 20))

    def draw_game_actions(self, screen_width):
        buttons = self.get_game_action_buttons(screen_width)
        selected = (self.displayed_games[self.selected_game]
                    if self.selected_game is not None else None)
        is_favorite = selected is not None and (selected.get_platform(), selected.get_id()) in self.favorite_ids
        pygame.draw.rect(self.screen, BLUE if is_favorite else DARK_GRAY, buttons["favorite"])
        favorite_label = "Favorited" if is_favorite else "Add to Favorites"
        favorite_text = FONT.render(favorite_label, True, WHITE)
        self.screen.blit(favorite_text, favorite_text.get_rect(center=buttons["favorite"].center))
        pygame.draw.rect(self.screen, GREEN, buttons["launch"])
        launch_text = FONT.render("Launch", True, WHITE)
        self.screen.blit(launch_text, launch_text.get_rect(center=buttons["launch"].center))

    def run(self):
        # Show loading screen
        self.screen.fill(EAST_BAY)
        loading_text = FONT.render("Launcher is loading...", True, WHITE)
        loading_size = loading_text.get_size()
        loading_pos = ((self.screen.get_size()[0] - loading_size[0]) // 2, (self.screen.get_size()[1] - loading_size[1]) // 2)
        self.screen.blit(loading_text, loading_pos)
        pygame.display.flip()
        self.clock.tick(60)

        # Load games
        self.games = Core.load_games_from_disk()
        self.displayed_games = self.games.copy()
        self.selected_game = 0 if self.games else None
        self.note_input = self.games[0].get_notes() if self.games else ""
        self.refresh_status = "Refreshing libraries..."
        self.refresh_libraries()

        running = True
        while running:
            try:
                refresh_errors = self.refresh_results.get_nowait()
            except queue.Empty:
                refresh_errors = None
            if refresh_errors is not None:
                selected_game = (self.displayed_games[self.selected_game]
                                 if self.selected_game is not None and self.displayed_games else None)
                new_games = Core.load_new_games(self.games)
                self.games.extend(new_games)
                self.games.sort(key=lambda game: game.get_name().upper())
                self.apply_game_filter(selected_game)
                self.refresh_status = ("Refresh failed: " + "; ".join(refresh_errors)
                                       if refresh_errors else "Libraries refreshed")

            screen_width, screen_height = self.screen.get_size()

            # Draw BG
            self.screen.fill(EAST_BAY)
            pygame.draw.rect(self.screen, BLACK, (0, 0, screen_width, 101))
            pygame.draw.rect(self.screen, DARK_BAY, (0, 0, screen_width, 100))
            pygame.draw.rect(self.screen, CHAMBRAY, (screen_width - 550, 0, 550, screen_height))
            pygame.draw.rect(self.screen, BLACK, (screen_width - 550, 0, 2, screen_height))

            self.draw_nav_bar(screen_width)
            self.max_visible = (screen_height - self.list_top_gap) // self.line_height - 1
            self.draw_game_list(screen_width, screen_height)
            self.draw_game_banner(screen_width)
            self.draw_game_info(screen_width)
            self.draw_notes(screen_width, screen_height)
            self.draw_game_actions(screen_width)

            now = pygame.time.get_ticks()
            if self.backspace_held:
                if now - self.backspace_timer > self.backspace_repeat_delay:
                    if (now - self.backspace_timer) % self.backspace_repeat_rate < 15:
                        self.note_input = self.note_input[:-1]
                        self.displayed_games[self.selected_game].set_notes(self.note_input)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    Core.save_game_notes(self.games)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    buttons = self.get_nav_buttons(screen_width)
                    action_buttons = self.get_game_action_buttons(screen_width)
                    clicked_filter = next(
                        (name for name, rect in self.filter_buttons.items() if rect.collidepoint(mx, my)),
                        None
                    )
                    if clicked_filter is not None:
                        selected = (self.displayed_games[self.selected_game]
                                    if self.selected_game is not None else None)
                        self.active_filter = clicked_filter
                        self.apply_game_filter(selected)
                    elif action_buttons["favorite"].collidepoint(mx, my):
                        if self.selected_game is not None:
                            game = self.displayed_games[self.selected_game]
                            favorite_key = (game.get_platform(), game.get_id())
                            if favorite_key in self.favorite_ids:
                                Core.unfavorite_game(game.get_id(), game.get_platform())
                                self.favorite_ids.remove(favorite_key)
                            else:
                                Core.favorite_game(favorite_key[1], favorite_key[0])
                                self.favorite_ids.add(favorite_key)
                            self.apply_game_filter(game, preserve_scroll=True)
                    elif buttons["add_game"].collidepoint(mx, my):
                        new_game = add_game_dialog()
                        if new_game is not None:
                            self.games.append(new_game)
                            self.apply_game_filter(new_game)
                    elif buttons["add_account"].collidepoint(mx, my):
                        print("Add Account clicked")
                    elif buttons["remove_game"].collidepoint(mx, my):
                        if self.selected_game is None:
                            continue
                        game = self.displayed_games[self.selected_game]
                        Core.remove_game(game)
                        self.displayed_games.remove(game)
                        self.games.remove(game)

                        self.selected_game = 0
                    elif action_buttons["launch"].collidepoint(mx, my):
                        if self.selected_game is not None:
                            self.displayed_games[self.selected_game].start()
                    else:
                        if self.list_top_gap <= my <= self.list_top_gap + self.max_visible * self.line_height:
                            rel_y = (my - self.list_top_gap) // self.line_height
                            index = self.scroll_offset + rel_y
                            if 0 <= index < len(self.displayed_games):
                                self.selected_game = index
                                self.note_input = self.displayed_games[index].get_notes()

                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        if self.scroll_offset > 0:
                            self.scroll_offset -= 1
                            if self.selected_game > self.scroll_offset + self.max_visible - 1:
                                self.selected_game = self.scroll_offset + self.max_visible - 1
                    elif event.y < 0:
                        if self.scroll_offset + self.max_visible < len(self.displayed_games):
                            self.scroll_offset += 1
                            if self.selected_game < self.scroll_offset:
                                self.selected_game = self.scroll_offset

                elif event.type == pygame.KEYDOWN:
                    if self.selected_game is None:
                        continue
                    if event.key == pygame.K_BACKSPACE:
                        self.backspace_held = True
                        self.backspace_timer = now
                        self.note_input = self.note_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.note_input += "\n"
                    elif event.key == pygame.K_DOWN:
                        if self.selected_game < len(self.displayed_games) - 1:
                            self.selected_game += 1
                            if self.selected_game >= self.scroll_offset + self.max_visible:
                                self.scroll_offset += 1
                            self.note_input = self.displayed_games[self.selected_game].get_notes()
                    elif event.key == pygame.K_UP:
                        if self.selected_game > 0:
                            self.selected_game -= 1
                            if self.selected_game < self.scroll_offset:
                                self.scroll_offset -= 1
                            self.note_input = self.displayed_games[self.selected_game].get_notes()
                    else:
                        self.note_input += event.unicode
                    self.displayed_games[self.selected_game].set_notes(self.note_input)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_BACKSPACE:
                        self.backspace_held = False

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


