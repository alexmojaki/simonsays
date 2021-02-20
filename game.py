import random
import readchar
import collections

CHARS = "wasd"
VIEW_SIZE = 5
GENERATE_SIZE = 5
AFTER_MISTAKE = 5
BEFORE_MISTAKE = 5
HISTORIC_VIEW = 5

instructions = []
previous_instructions = collections.deque([], maxlen=HISTORIC_VIEW)
previous_inputs = collections.deque([], maxlen=HISTORIC_VIEW)
previous_i_s = collections.deque([], maxlen=HISTORIC_VIEW)


def generate_chars():
    instructions.extend(random.choices(CHARS, k=GENERATE_SIZE))


def to_padded_str(value):
    return str(value).ljust(2)


def spaced_join(values):
    return " ".join(map(to_padded_str, values))


def spaced_join_instructions(values):
    return spaced_join(map(to_arrow, values))


def to_arrow(c):
    return {
        "a": "←",
        "s": "↓",
        "d": "→",
        "w": "↑",
    }[c]


def print_screen():
    print("\033c", end="")  # clear sce # todo: non-linux solution
    print()
    check_marks = [
        "✔" if instruction == input_char else "✘"
        for instruction, input_char
        in zip(previous_instructions, previous_inputs)
    ]
    display_string = (
            spaced_join(check_marks)
            + "\n" + spaced_join(list(previous_i_s) + list(next_instructions()))
            + "\n" + spaced_join_instructions(list(previous_instructions) + list(next_instruction_chars()))
            + "\n" + spaced_join_instructions(previous_inputs)
    )
    display_width = max(map(len, display_string.split("\n")))
    display_string = f"i:{i}, streak:{streak}".rjust(display_width) + "\n" + display_string
    print(display_string)


generate_chars()
generate_chars()
generate_chars()

i = 0
streak = 0


def next_instructions():
    if current_mistake is None:
        for index in range(i, i + VIEW_SIZE):
            yield index % len(instructions)
    else:
        index = i
        for _ in range(VIEW_SIZE):
            yield index % len(instructions)
            if index == mistake_loop_end:
                index = mistake_loop_start
            else:
                index += 1


def next_instruction_chars():
    return map(lambda j: instructions[j], next_instructions())


current_mistake = None
next_mistake = None
mistake_loop_end = mistake_loop_start = None

while True:
    print_screen()
    key = readchar.readkey().lower()
    if key not in CHARS:
        print(f"Received {key}, quiting...")
        exit()
    previous_inputs.append(key)
    previous_i_s.append(i)
    previous_instructions.append(instructions[i])
    correct = key == instructions[i]

    if correct:
        streak += 1
        if i == current_mistake:
            if next_mistake is not None:
                current_mistake = next_mistake
                next_mistake = None
                mistake_loop_start = max(0, (current_mistake - BEFORE_MISTAKE)) % len(instructions)
            else:
                current_mistake = mistake_loop_end = mistake_loop_start = None
    else:
        streak = 0
        if current_mistake in (i, None):
            current_mistake = i
            mistake_loop_end = (i + AFTER_MISTAKE) % len(instructions)
            mistake_loop_start = max(0, (i - BEFORE_MISTAKE)) % len(instructions)
        else:
            next_mistake = i

    i = list(next_instructions())[1]

    if streak >= len(instructions) and i == 0:
        generate_chars()
