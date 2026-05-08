import random
from datetime import datetime

# ============================================================
# ГЛАВА 1: КОНСТАНТИ И ФУНКЦІЇ ДЛЯ РИСУВАННЯ
# ============================================================

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
        with open(filename, 'r', encoding='utf-8') as file:
            words = [word.strip() for word in file.readlines()]
        return words
    except FileNotFoundError:
        print(f" Помилка: файл '{filename}' не знайдено!")
        print(f"   Будь ласка, створіть файл '{filename}' зі словами (одне слово на рядок)")
        return []


def save_game_to_history(player_name, secret_word, guessed_word, attempts_left, is_won):
    game_result = " ПЕРЕМОГА" if is_won else " ПОРАЗКА"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as file:
            file.write(f"[{timestamp}] {player_name} | Результат: {game_result} | ")
            file.write(f"Слово: {secret_word} | Вгадано: {guessed_word} | ")
            file.write(f"Спроб лишилось: {attempts_left}\n")
    except IOError:
        print(" Помилка при збереженні історії гри!")


def view_game_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as file:
            history = file.read()
        
        if history:
            print("\n" + "=" * 80)
            print(" ІСТОРІЯ ІГОР")
            print("=" * 80)
            print(history)
            print("=" * 80)
        else:
            print(" Історія ігор ще порожня!")
    except FileNotFoundError:
        print(" Ще не було жодної гри!")


# ============================================================
# ГЛАВА 3: ФУНКЦІЇ ДЛЯ ЛОГІКИ ГРИ
# ============================================================

def select_random_word(words_list):
    return random.choice(words_list).lower()


def initialize_guessed_word(secret_word):
    return " ".join(["_" for _ in secret_word])


def display_game_state(guessed_word, wrong_guesses, attempts_left):
    # Вибираємо правильний етап малюнка (залежит від кількості помилок)
    wrong_attempts = MAX_ATTEMPTS - attempts_left
    print(HANGMAN_STAGES[wrong_attempts])
    
    print(f"\n Слово: {guessed_word}")
    
    if wrong_guesses:
        print(f" Невірні букви: {', '.join(sorted(wrong_guesses))}")
    
    print(f"  Спроб лишилось: {attempts_left}")


def update_guessed_word(secret_word, guessed_word, guessed_letter):
    word_list = guessed_word.split()
    
    for i, letter in enumerate(secret_word):
        if letter == guessed_letter:
            word_list[i] = letter
    
    return " ".join(word_list)


def get_player_guess(guessed_letters):
    while True:
        user_input = input("\n Введіть букву або спробуйте вгадати слово: ").strip().lower()
        
        # Перевірка на порожне введення
        if not user_input:
            print("  Будь ласка, введіть щось!")
            continue
        
        # Перевірка, чи це буква або слово (тільки букви)
        if not user_input.isalpha():
            print("  Введіть тільки букви!")
            continue
        
        # Перевірка на дублікати (якщо це одна буква)
        if len(user_input) == 1 and user_input in guessed_letters:
            print(f"  Ви вже називали букву '{user_input}'!")
            continue
        
        return user_input


def process_guess(secret_word, guessed_word, user_guess, guessed_letters, wrong_guesses, attempts_left):
    # ВИПАДОК 1: Гравець вгадує все слово
    if len(user_guess) > 1:
        if user_guess == secret_word:
            print(f"\n Вітаємо! Ви вгадали слово: {secret_word}")
            return guessed_word.replace(" ", ""), attempts_left, False  # False = перестати грати (перемога)
        else:
            print(f" Помилка! Слово '{user_guess}' неправильне!")
            attempts_left -= 1
            return guessed_word, attempts_left, True
    
    # ВИПАДОК 2: Гравець вгадує одну букву
    else:
        guessed_letters.add(user_guess)
        
        if user_guess in secret_word:
            print(f" Правильно! Буква '{user_guess}' є в слові!")
            guessed_word = update_guessed_word(secret_word, guessed_word, user_guess)
            return guessed_word, attempts_left, True
        else:
            print(f" Буква '{user_guess}' немає в слові!")
            wrong_guesses.add(user_guess)
            attempts_left -= 1
            return guessed_word, attempts_left, True


def play_game(words_list):
    # 1️ Запитуємо ім'я гравця
    player_name = input("Введіть ваше ім'я: ").strip()
    if not player_name:
        player_name = "Невідомий гравець"
    
    print(f"\n Привіт, {player_name}! Давайте грати в Шибеницю!\n")
    
    # 2️ Вибираємо слово
    secret_word = select_random_word(words_list)
    
    # 3️ Ініціалізуємо змінні
    guessed_word = initialize_guessed_word(secret_word)
    guessed_letters = set()  # Множина вже названих букв
    wrong_guesses = set()    # Множина невірних букв
    attempts_left = MAX_ATTEMPTS
    is_game_active = True
    is_won = False
    
    # 4️ ГОЛОВНИЙ ЦИКЛ ГРИ
    while is_game_active and attempts_left > 0:
        display_game_state(guessed_word, wrong_guesses, attempts_left)
        
        user_guess = get_player_guess(guessed_letters)
        
        guessed_word, attempts_left, is_game_active = process_guess(
            secret_word, guessed_word, user_guess, 
            guessed_letters, wrong_guesses, attempts_left
        )
        
        # Перевіряємо, чи гравець вгадав все слово
        if guessed_word.replace(" ", "") == secret_word:
            is_game_active = False
            is_won = True
    
    # 5️ КІНЕЦЬ ГРИ
    print("\n" + "=" * 50)
    
    if is_won:
        print(f" ПЕРЕМОГА! Слово було: {secret_word}")
    else:
        print(f" ПОРАЗКА! Слово було: {secret_word}")
        display_game_state(secret_word, wrong_guesses, attempts_left)
    
    print("=" * 50)
    
    # Зберігаємо результат
    save_game_to_history(player_name, secret_word, guessed_word, attempts_left, is_won)


# ============================================================
# ГЛАВА 4: МЕНЮ ТА ГОЛОВНА ПРОГРАМА
# ============================================================

def display_main_menu():
    
    print("\n" + "=" * 50)
    print(" ГРА 'ШИБЕНИЦЯ'".center(50))
    print("=" * 50)
    print("1️  Грати нову гру")
    print("2️  Переглянути історію ігор")
    print("3  Вихід")
    print("=" * 50)


def main():
    print(" Ласкаво просимо до гри 'Шибениця'!")
    
    # Завантажуємо слова
    words_list = load_words_from_file(WORDS_FILE)
    
    if not words_list:
        print(" Неможливо почати гру без слів. Завершення програми.")
        return
    
    # ГОЛОВНИЙ ЦИКЛ МЕНЮ
    while True:
        display_main_menu()
        
        choice = input("Ваш вибір (1-3): ").strip()
        
        try:
            match choice:
                case "1":
                    # Грати нову гру
                    play_game(words_list)
            
                case"2":
                    # Переглянути історію
                    view_game_history()
            
                case"3":
                # Вихід
                    print("\n Дякуємо за гру! До зустрічі!")
                    break
            
                case _:
                    print("  Будь ласка, виберіть 1, 2 або 3!")
        
        except Exception as error:
            print(f" Сталась непередбачена помилка: {error}")
            print("   Спробуйте ще раз.")


# ============================================================
# ЗАПУСК ПРОГРАМИ
# ============================================================

if __name__ == "__main__":
    main()