CASCADE_ClASIFIER = '../models/haarcascade_ua_license_plate.xml'
MODEL = "../models/model_ua_license_plate.keras"

# Формат збереження зображення після обробки
OUTPUT_FORMAT = 'png'

# коефіцієнти розпізнавання контурів номерного знака
SCALE_FACTOR = 1.15
MIN_NEIGHBORS = 7

# коефіцієнти розмірів контурів символів обрізаного номерного знака у функції detect_plate
WIDTH_LOWER = 1/10
WIDTH_UPPER = 2/3
HEIGH_LOWER = 1/10
HEIGH_UPPER = 3/5
