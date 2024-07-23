import os
import asyncio

import cv2
from datetime import datetime
import numpy as np
import tensorflow
import keras
from keras.models import load_model

CASCADE_ClASIFIER = 'DS/models/haarcascade_ua_license_plate.xml'
MODEL = "DS/models/model_ua_license_plate.keras"

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

model = load_model(MODEL, compile=False)
plate_cascade = cv2.CascadeClassifier(CASCADE_ClASIFIER)


async def detect_plate(img, text=''): 
    """
    Функція призначена для виявлення та обробки номерних знаків на зображенні.
    
    Параметри:
    img (numpy.array): Зображення, на якому потрібно виявити та обробити номерні знаки.
    text (str, optional): Текст, який можна додати на зображення навколо номерного знаку.
    
    Повертає:
    numpy.array: Зображення з виділеними номерними знаками та, за бажанням, доданим текстом.
    numpy.array or None: Зображення області номерного знаку для подальшої обробки або None, якщо номерний знак не був виявлений.
    """
    plate_img = img.copy()  # Копіюємо вхідне зображення для обробки
    roi = img.copy()  # Копіюємо вхідне зображення для виділення області номерного знаку
    
    # Виявлення номерних знаків на зображенні
    plate_rect = plate_cascade.detectMultiScale(plate_img, scaleFactor=1.3, minNeighbors=8)
    
    # Ініціалізуємо змінну plate перед використанням
    plate = None
    
    # Обробка кожного виявленого номерного знаку
    for (x, y, w, h) in plate_rect:
        # Витягаємо область номерного знаку для подальшої обробки
        roi_ = roi[y:y+h, x:x+w, :]
        plate = roi[y:y+h, x:x+w, :]
        
        # Малюємо прямокутник навколо номерного знаку на вихідному зображенні
        cv2.rectangle(plate_img, (x-15, y), (x+w-3, y+h-5), (179, 206, 226), 3)
     
    # Додавання тексту 
    if text != '':
        plate_img = cv2.putText(plate_img, text, (15,15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        plate_img = cv2.putText(plate_img, text, (15,15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            
    # Повертаємо оброблене зображення з виділеними номерними знаками та область номерного знаку
    return plate_img, plate


async def find_contours(dimensions, img):
    """
    Функція призначена для знаходження контурів символів на зображенні номерного знака.
    
    Параметри:
        dimensions (list): Список, що містить набір розмірів контурів символів: 
                           lower_width, upper_width, lower_height та upper_height.
        img (numpy.ndarray): Вхідне зображення, на якому потрібно знайти контури символів.
        
    Повертає:
        numpy.ndarray: Масив, що містить зображення контурів символів, відсортованих за координатою x.
    """
    cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]

    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

    x_cntr_list = []
    target_contours = []
    img_res = []
    for cntr in cntrs:
        # Detect contour in binary image and return the coordinates of rectangle enclosing it
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        # Check the dimensions of the contour to filter out the characters by contour's size
        if intWidth > lower_width and intWidth < upper_width and intHeight > lower_height and intHeight < upper_height:
            x_cntr_list.append(intX)  # Store the x coordinate of the character's contour, to be used later for indexing the contours

            char_copy = np.zeros((44, 24))
            # Extract each character using the enclosing rectangle's coordinates
            char = img[intY:intY+intHeight, intX:intX+intWidth]
            char = cv2.resize(char, (20, 40))

            # Make result formatted for classification: invert colors
            char = cv2.subtract(255, char)

            # Resize the image to 24x44 with black border
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0

            img_res.append(char_copy)  # List that stores the character's binary image (unsorted)
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        img_res_copy.append(img_res[idx])  # Store character images according to their index
    img_res = np.array(img_res_copy)

    return img_res


async def segment_characters(image):
    """
    Знаходить символи на зображенні номерного знака.

    Параметри:
     - image: Зображення номерного знака, з якого будуть вилучені символи.

    Повертає:
     - char_list: Список контурів символів, знайдених на зображенні.
    """
    # Попередньо оброблюємо зображення номерного знака
    img_lp = cv2.resize(image, (333, 75))
    img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)
    _, img_binary_lp = cv2.threshold(img_gray_lp, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_binary_lp = cv2.erode(img_binary_lp, (3,3))
    img_binary_lp = cv2.dilate(img_binary_lp, (3,3))

    LP_WIDTH = img_binary_lp.shape[0]
    LP_HEIGHT = img_binary_lp.shape[1]

    # Робимо межі білими
    img_binary_lp[0:3,:] = 255
    img_binary_lp[:,0:3] = 255
    img_binary_lp[72:75,:] = 255
    img_binary_lp[:,330:333] = 255

    # Приблизні розміри контурів символів обрізаного номерного знака
    dimensions = [LP_WIDTH * WIDTH_LOWER,
                  LP_WIDTH * WIDTH_UPPER,
                  LP_HEIGHT * HEIGH_LOWER,
                  LP_HEIGHT * HEIGH_UPPER]


    char_list = await find_contours(dimensions, img_binary_lp)

    return char_list


async def fix_dimension(img):
    """
    Функція для вирівнювання розмірів зображення до розмірів (28, 28, 3).

    Параметри:
    img (numpy.ndarray): Вхідне зображення з розмірами (n, m), де n та m - цілі числа.

    Повертає:
    numpy.ndarray: Зображення з розмірами (28, 28, 3), де 3 - кількість каналів (RGB).
    """
    new_img = np.zeros((28,28,3))
    for i in range(3):
        new_img[:,:,i] = img
    return new_img


async def show_results(char):
    """
    Функція для показу результатів розпізнавання символів на номерному знаку.

    Параметри:
    char (list): Список зображень символів номерного знаку.

    Повертає:
    str: Рядок, що містить розпізнану номерну знаку, складену з окремих символів.
    """
    dic = {}
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, c in enumerate(characters):
        dic[i] = c

    output = []
    for i, ch in enumerate(char): # ітеруємося по символах
        img_ = cv2.resize(ch, (28, 28), interpolation=cv2.INTER_AREA)
        img = await fix_dimension(img_)
        img = img.reshape(1, 28, 28, 3) # підготовка зображення для моделі
        y_proba = model.predict(img, verbose=0)[0] # отримуємо ймовірності для кожного класу
        y_ = np.argmax(y_proba) # вибираємо клас з найвищою ймовірністю
        character = dic[y_] # отримуємо символ, відповідний прогнозованому класу
        output.append(character) # зберігаємо результат у списку

    plate_number = ''.join(output) # об'єднуємо всі символи у рядок

    return plate_number


async def plate_recognize(photo):
    """
    Розпізнавання номерного знаку на зображенні.

    :param photo: Шлях до зображення автомобіля з номерним знаком.
    :type photo: str
    :return: Кортеж, що містить зображення з рамкою навколо номерного знаку та розпізнані символи.
    :rtype: tuple
    """
    img = cv2.imread(photo)

    # Поточні час і дата
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Виявлення номерного знаку на зображенні
    output_img, plate = await detect_plate(img, text=current_datetime_str)
    
    # Переведення зображення у вибраний формат
    _, img_buffer = cv2.imencode(f'.{OUTPUT_FORMAT}', output_img)
    img_bytes = img_buffer.tobytes()

    if plate is None:
        return img_bytes, None
    
    char = await segment_characters(plate)# Виявлення символів номерного знаку
    recognized_symbols = await show_results(char)# Розпізнавання символів номерного знаку

    return img_bytes, recognized_symbols


async def main():
    # Отримання списку файлів у каталозі DS/img/
    img_dir = 'DS/images/'
    img_files = os.listdir(img_dir)

    # Створення каталогу для збереження розпізнаних знаків
    results_dir = 'DS/results/'
    os.makedirs(results_dir, exist_ok=True)

    # Створення каталогу для збереження нерозпізнаних знаків
    unrecognized_dir = 'DS/unrecognized/'
    os.makedirs(unrecognized_dir, exist_ok=True)

    # Проходження по кожному файлу у каталозі
    for img_file in img_files:
        # Повний шлях до поточного файлу
        img_path = os.path.join(img_dir, img_file)
        
        # Виклик функції plate_recognize() для розпізнавання номерного знаку
        result_img, recognized_symbols = await plate_recognize(img_path)
        
        # Якщо номерний знак був розпізнаний, зберегти результат
        if recognized_symbols:
            # Шлях для збереження результату
            result_filename = os.path.join(results_dir, f"{recognized_symbols}.jpg")
            cv2.imwrite(result_filename, result_img)
            print(f"Результат для файлу {img_file} був збережений у {result_filename}")
        else:
            # Якщо номерний знак не був розпізнаний, зберегти його у каталозі DS/unrecognized/
            unrecognized_filename = os.path.join(unrecognized_dir, img_file)
            cv2.imwrite(unrecognized_filename, result_img)
            print(f"Нерозпізнаний знак у файлі {img_file} був збережений у {unrecognized_filename}")

# Запуск асинхронної функції main()
asyncio.run(main())
