settings = {}
with open ("settings.txt", 'r') as file:
    for line in file.readlines():
        setting, value = line.split("=")
        setting = setting.strip()
        value = value.strip()
        try:
            value = int(value)
        except:
            pass
        settings[setting] = value

TITLE = settings['TITLE']
WIDTH = settings['WIDTH']
HEIGHT = settings['HEIGHT']
DEBUG = bool(settings['DEBUG'])
font = settings['FONT']