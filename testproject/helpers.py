import random


def random_letter_color_challenge(idx, char):
    # Generate colorful but balanced RGB values
    red = random.randint(64, 200)
    green = random.randint(64, 200)
    blue = random.randint(64, 200)

    # Ensure at least one channel is higher to make it colorful
    channels = [red, green, blue]
    random.shuffle(channels)
    channels[0] = random.randint(150, 255)

    # Format the color as a hex string
    return f"#{channels[0]:02X}{channels[1]:02X}{channels[2]:02X}"
