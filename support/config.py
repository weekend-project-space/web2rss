config = {}


def init_cofig(config_file_path='config.txt'):
    with open(config_file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            config[key] = value


def get_item(key):
    return config[key]
