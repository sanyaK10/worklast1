import random
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from art import text2art
# ============================================================
# ГЛАВА 1: КОНСТАНТИ І ФУНКЦІЇ ДЛЯ РИСУВАННЯ
# ============================================================
console = Console()
# Етапи малювання шибеника (від 0 до 6 помилок)
HANGMAN_STAGES = [
    """
    ------
    |    |
    |
    |
    |
    |
    --------
    """,
    """
    ------
    |    |
    |    O
    |
    |
    |
    --------
    """,
    """
    ------
    |    |
    |    O
    |    |
    |
    |
    --------
    """,
    """
    ------
    |    |
    |    O
    |   /|
    |
    |
    --------
    """,
    """
    ------
    |    |
    |    O
    |   /|\\
    |
    |
    --------
    """,
    """
    ------
    |    |
    |    O
    |   /|\\
    |   /
    |
    --------
    """,
    """
    ------
    |    |
    |    O
    |   /|\\
    |   / \\
    |
    --------
    """
]

# Назва файлів для збереження даних
WORDS_FILE = "words.txt"
HISTORY_FILE = "game_history.txt"

# Кількість спроб для гри
MAX_ATTEMPTS = 6

# ============================================================
# ГЛАВА 2: ФУНКЦІЇ ДЛЯ РОБОТИ З ФАЙЛАМИ
# ============================================================

def load_words_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [word.strip() for word in file.readlines()]

    except FileNotFoundError:
        console.print(f"[bold red]Файл '{filename}' не знайдено![/bold red]")
        return []


def save_game_to_history(player_name, secret_word,
                         guessed_word, attempts_left, is_won):

    game_result = "ПЕРЕМОГА" if is_won else "ПОРАЗКА"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as file:
            file.write(
                f"[{timestamp}] {player_name} | "
                f"Результат: {game_result} | "
                f"Слово: {secret_word} | "
                f"Вгадано: {guessed_word} | "
                f"Спроб лишилось: {attempts_left}\n"
            )

    except IOError:
        console.print("[bold red]Помилка збереження![/bold red]")

def view_game_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = file.readlines()
        if history:

            table = Table(
                title="ІСТОРІЯ ІГОР",
                box=box.ROUNDED,
                border_style="cyan"
            )
            table.add_column("№", style="yellow")
            table.add_column("Запис", style="white")
            for index, line in enumerate(history, start=1):
                table.add_row(str(index), line.strip())
            console.print(table)
        else:
            console.print("[yellow]Історія порожня![/yellow]")
    except FileNotFoundError:
        console.print("[yellow]Ще не було жодної гри![/yellow]")

# ============================================================
# ГЛАВА 3: ФУНКЦІЇ ДЛЯ ЛОГІКИ ГРИ
# ============================================================

def select_random_word(words_list):
    return random.choice(words_list).lower()


def initialize_guessed_word(secret_word):
    return " ".join("_" for _ in secret_word)


def display_game_state(guessed_word, wrong_guesses, attempts_left):

    # Вибираємо правильний етап малюнка
    wrong_attempts = MAX_ATTEMPTS - attempts_left

    console.print(
        Panel(
            HANGMAN_STAGES[wrong_attempts],
            title="[bold red]ШИБЕНИЦЯ[/bold red]",
            border_style="red"
        )
    )
    console.print(f"[bold cyan]Слово:[/bold cyan] {guessed_word}")
    if wrong_guesses:
        console.print(
            f"[bold red]Невірні букви:[/bold red] "
            f"{', '.join(sorted(wrong_guesses))}"
        )
    console.print(
        f"[bold green]Спроб лишилось:[/bold green] {attempts_left}"
    )

def update_guessed_word(secret_word, guessed_word, guessed_letter):
    word_list = guessed_word.split()
    for i, letter in enumerate(secret_word):
        if letter == guessed_letter:
            word_list[i] = letter
    return " ".join(word_list)

def get_player_guess(guessed_letters):
    while True:
        user_input = console.input(
            "\n[bold yellow]Введіть букву або слово:[/bold yellow] ").strip().lower()

        # Перевірка на порожне введення
        if not user_input:
            console.print("[red]Введіть щось![/red]")
            continue

        # Перевірка, чи це тільки букви
        if not user_input.isalpha():
            console.print("[red]Тільки букви![/red]")
            continue

        # Перевірка на дублікати
        if len(user_input) == 1 and user_input in guessed_letters:
            console.print(f"[red]Буква '{user_input}' вже була![/red]")
            continue

        return user_input

def process_guess(secret_word, guessed_word, user_guess,
                  guessed_letters, wrong_guesses, attempts_left):
    # ВИПАДОК 1: Гравець вгадує слово
    if len(user_guess) > 1:
        if user_guess == secret_word:
            console.print(
                f"\n[bold green]Ви вгадали слово: "
                f"{secret_word}![/bold green]"
            )
            return guessed_word.replace(" ", ""), attempts_left, False
        else:
            console.print(f"[red]Слово '{user_guess}' неправильне![/red]")
            attempts_left -= 1
            return guessed_word, attempts_left, True
    # ВИПАДОК 2: Гравець вгадує букву
    guessed_letters.add(user_guess)
    if user_guess in secret_word:
        console.print(f"[green]Буква '{user_guess}' є в слові![/green]")
        guessed_word = update_guessed_word(
            secret_word,
            guessed_word,
            user_guess
        )
    else:
        console.print(f"[red]Букви '{user_guess}' немає![/red]")
        wrong_guesses.add(user_guess)
        attempts_left -= 1
    return guessed_word, attempts_left, True

def play_game(words_list):

    # 1 Запитуємо ім'я гравця
    player_name = console.input(
        "[bold cyan]Введіть ваше ім'я:[/bold cyan] ").strip()

    if not player_name:
        player_name = "Невідомий гравець"

    console.print(
        Panel.fit(
            f"Привіт, [bold green]{player_name}[/bold green]!",
            border_style="green"
        )
    )
    # 2 Вибираємо слово
    secret_word = select_random_word(words_list)


    # 3 Ініціалізуємо змінні
    guessed_word = initialize_guessed_word(secret_word)
    guessed_letters = set()
    wrong_guesses = set()
    attempts_left = MAX_ATTEMPTS
    is_game_active = True
    is_won = False

    # 4 ГОЛОВНИЙ ЦИКЛ ГРИ
    while is_game_active and attempts_left > 0:

        display_game_state(
            guessed_word,
            wrong_guesses,
            attempts_left
        )
        user_guess = get_player_guess(guessed_letters)
        guessed_word, attempts_left, is_game_active = process_guess(
            secret_word,
            guessed_word,
            user_guess,
            guessed_letters,
            wrong_guesses,
            attempts_left
        )

        # Перевіряємо, чи гравець вгадав слово
        if guessed_word.replace(" ", "") == secret_word:
            is_game_active = False
            is_won = True

    # 5 КІНЕЦЬ ГРИ
    console.print("\n" + "=" * 50)
    if is_won:
        console.print(
            f"[bold green]ПЕРЕМОГА! "
            f"Слово було: {secret_word}[/bold green]" )
    else:
        console.print(
            f"[bold red]ПОРАЗКА! "
            f"Слово було: {secret_word}[/bold red]")
        display_game_state(
            secret_word,
            wrong_guesses,
            attempts_left
        )
    console.print("=" * 50)

    # Зберігаємо результат
    save_game_to_history(
        player_name,
        secret_word,
        guessed_word,
        attempts_left,
        is_won
    )

# ============================================================
# ГЛАВА 4: МЕНЮ ТА ГОЛОВНА ПРОГРАМА
# ============================================================

def display_main_menu():
    console.print(
        f"[bold blue]{text2art('HANGMAN')}[/bold blue]")
    menu = Table(
        box=box.DOUBLE_EDGE,
        border_style="cyan")
    menu.add_column("Опція", style="yellow")
    menu.add_column("Дія", style="green")
    menu.add_row("1", "Грати")
    menu.add_row("2", "Історія")
    menu.add_row("3", "Вихід")
    console.print(menu)


def main():
    console.print(
        "[bold cyan]Ласкаво просимо до гри "
        "'Шибениця'![/bold cyan]"
    )
    # Завантажуємо слова
    words_list = load_words_from_file(WORDS_FILE)
    if not words_list:
        console.print("[bold red]Немає слів для гри![/bold red]")
        return
    
    # ГОЛОВНИЙ ЦИКЛ МЕНЮ
    while True:
        display_main_menu()
        choice = console.input(
            "\n[bold yellow]Ваш вибір (1-3):[/bold yellow] ").strip()
        try:
            match choice:
                case "1":
                    # Грати нову гру
                    play_game(words_list)
                case "2":
                    # Переглянути історію
                    view_game_history()
                case "3":
                    # Вихід
                    console.print(
                        "\n[bold cyan]До зустрічі![/bold cyan]"
                    )
                    break
                case _:
                    console.print("[red]Виберіть 1, 2 або 3![/red]")

        except Exception as error:
            console.print(f"[bold red]Помилка: {error}[/bold red]")

# ============================================================
# ЗАПУСК ПРОГРАМИ
# ============================================================

if __name__ == "__main__":
    main()