import random
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Hangman", layout="centered")

# ---------------- LOGO ----------------
logo = r''' 
 _                                             
| |                                            
| |__   __ _ _ __   __ _ _ __ ___   __ _ _ __  
| '_ \ / _` | '_ \ / _` | '_ ` _ \ / _` | '_ \ 
| | | | (_| | | | | (_| | | | | | | (_| | | | |
|_| |_|\__,_|_| |_|\__, |_| |_| |_|\__,_|_| |_|
                    __/ |                      
                   |___/    '''
st.code(logo, language="")

# ---------------- HANGMAN STAGES ----------------
stages = [r'''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========
''', r'''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========
''', r'''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========
''', r'''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
''', r'''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
''', r'''
  +---+
  |   |
  O   |
      |
      |
      |
=========
''', r'''
  +---+
  |   |
      |
      |
      |
      |
=========
''']

# ---------------- WORD LIST (30 items) ----------------
word_list = [
    'abruptly','absurd','abyss','affix','askew','avenue','awkward','axiom','azure',
    'bagpipes','banjo','bayou','beekeeper','bikini','blitz','blizzard','boggle','bookworm',
    'boxcar','buffalo','buzzard','buzzing','caliph','cobweb','cockiness','croquet','crypt',
    'cycle','daiquiri','dirndl'
]

# ---------------- SIDEBAR SETTINGS ----------------
st.sidebar.header("Settings")
debug_show_word = st.sidebar.checkbox("Show chosen word (debug)", value=False)
st.sidebar.caption("Use 'Restart Game' to reset the session state.")

# ---------------- SESSION STATE INITIALIZATION ----------------
if "initialized" not in st.session_state:
    # pick a word
    st.session_state.chosen_word = random.choice(word_list)
    st.session_state.correct_letters = set()
    st.session_state.guessed_letters = set()
    st.session_state.lives = 6
    st.session_state.game_over = False
    st.session_state.message = ""

    # ---------------- HINT LETTER ----------------
    hint_letter = random.choice(list(st.session_state.chosen_word))
    st.session_state.correct_letters.add(hint_letter)
    st.session_state.initialized = True

# helper to restart
def restart_game():
    st.session_state.chosen_word = random.choice(word_list)
    st.session_state.correct_letters = set()
    st.session_state.guessed_letters = set()
    st.session_state.lives = 6
    st.session_state.game_over = False
    st.session_state.message = ""
    # add hint letter
    hint_letter = random.choice(list(st.session_state.chosen_word))
    st.session_state.correct_letters.add(hint_letter)

# ---------------- DEBUG ----------------
if debug_show_word:
    st.sidebar.info(f"Chosen word: **{st.session_state.chosen_word}**")

# ---------------- BUILD DISPLAY ----------------
def build_display():
    return "".join([c if c in st.session_state.correct_letters else "_" for c in st.session_state.chosen_word])

display = build_display()

# ---------------- UI LAYOUT ----------------
st.title("🪓 Hangman")
st.markdown("### Word to guess")
st.code(display, language="")

st.markdown(f"**Lives left:** {st.session_state.lives}")

# show ASCII stage
stage_index = max(0, min(6 - st.session_state.lives, len(stages) - 1))
st.code(stages[stage_index], language="")

# show guessed letters
if st.session_state.guessed_letters:
    st.write("Guessed letters:", " ".join(sorted(st.session_state.guessed_letters)))
else:
    st.write("Guessed letters: (none)")

# last action message
if st.session_state.message:
    st.info(st.session_state.message)

# ---------------- GUESS INPUT ----------------
with st.form(key="guess_form"):
    guess_input = st.text_input("Enter a single letter (a-z) or full-word guess:", max_chars=50)
    submit = st.form_submit_button("Submit Guess")

if submit and not st.session_state.game_over:
    guess = guess_input.strip().lower()

    if not guess:
        st.warning("Please enter something.")
    else:
        # whole-word guess
        if len(guess) > 1:
            if guess == st.session_state.chosen_word:
                st.session_state.correct_letters.update(set(st.session_state.chosen_word))
                st.session_state.message = "🎉 Correct! You guessed the whole word."
                st.session_state.game_over = True
            else:
                st.session_state.lives -= 1
                st.session_state.guessed_letters.add(guess)
                st.session_state.message = f"Whole-word guess '{guess}' is incorrect. Lost a life."
        else:
            # single-letter guess validation
            if not guess.isalpha():
                st.warning("Please enter a letter (a-z).")
            elif guess in st.session_state.guessed_letters:
                st.info(f"You've already guessed '{guess}'.")
                st.session_state.message = ""
            else:
                st.session_state.guessed_letters.add(guess)
                if guess in st.session_state.chosen_word:
                    st.session_state.correct_letters.add(guess)
                    st.session_state.message = f"Nice — '{guess}' is in the word."
                else:
                    st.session_state.lives -= 1
                    st.session_state.message = f"'{guess}' is not in the word. You lose a life."

    # update display and check win/lose
    display = build_display()
    if "_" not in display:
        st.session_state.game_over = True
        st.session_state.message = "🎉 YOU WIN — well done!"
    elif st.session_state.lives <= 0:
        st.session_state.game_over = True
        st.session_state.message = f"💀 YOU LOSE — the word was '{st.session_state.chosen_word}'."

# ---------------- RESTART BUTTON ----------------
if st.button("Restart Game"):
    restart_game()
    st.experimental_rerun()

# show final message if game over
if st.session_state.game_over:
    st.success(st.session_state.message)
