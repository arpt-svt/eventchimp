import random
import string


def generate_random_string(length):
    population = string.ascii_lowercase + string.digits
    random_list = random.choices(
        population=population,
        k=length
    )
    return "".join(random_list)
