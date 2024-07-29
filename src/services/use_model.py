import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from keras.models import load_model
from matplotlib import pyplot as plt

import cv2
import numpy as np
import re

from src.conf.constants import IMAGES

# from colors import YELLOW, BLUE, LIGHTBLUE, CYAN, GRAY, RESET

YELLOW = "\033[33m"
BLUE = "\033[34m"
LIGHTBLUE = "\033[94m"
RED = "\033[31m"
RED_BACK = "\033[41m"
LIGHTRED = "\033[91m"
LIGHTRED_BACK = "\033[101m"
CYAN = "\033[36m"
GRAY = "\033[90m"
RESET = "\033[0m"
TAB = "\t"

# from datetime import datetime

PHOTO_FOLDER = "src/static/images/"
MODEL_CASCADE = "src/models/haarcascade_ua_license_plate.xml"
MODEL_KERAS = "src/models/model_ua_license_plate.keras"
TMP_DIR = "tmp"
TMP = "tmp/contour.jpg"
BOX_COLOR = (220, 220, 220)


# Проверка наличия папки и создание её, если она не существует
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
    
    
# Функції:


def display_image(img_, title="", recognized=True):
    """
    функція виводу зображень з заголовком
    """
    img_display = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 6))
    ax = plt.subplot(111)
    ax.imshow(img_display)
    plt.axis("off")
    plt.title(title, fontsize=20, color=(0.1, 0.2, 0.1) if recognized else (1, 0.0, 0.0))
    plt.show()


def draw_number_border(plate_img, plate_rect, color_=""):
    """малювання прямокутника по межі номера червоним кольором, якщо color_!= ''"""
    border_color = (0, 0, 200) if (color_) else (51, 181, 155)
    for x, y, w, h in plate_rect:
        cv2.rectangle(plate_img, (x + 2, y), (x + w - 3, y + h - 5), border_color, 3)


def detect_plate(img_, text=""):
    """
    Функція призначена для виявлення та обробки номерних знаків на зображенні.

    Параметри:
    img (numpy.array): Зображення, на якому потрібно виявити та обробити номерні знаки.
    text (str, optional): Текст, який можна додати на зображення навколо номерного знаку.

    Повертає:
    numpy.array: Зображення з виділеними номерними знаками та, за бажанням, доданим текстом.
    numpy.array or None: Зображення області номерного знаку для подальшої обробки або None, якщо номерний знак не був виявлений.
    """
    plate_img = img_.copy()  # перша копія зображення
    reg_of_intr = img_.copy()  # друга копія зображення
    # display_image(img_)
    # виявляє номерні знаки та повертає координати та розміри виявлених контурів номерних знаків
    plate_rect = plate_cascade.detectMultiScale(
        plate_img, scaleFactor=1.4, minNeighbors=7
    )

    if len(plate_rect) > 0:
        plate_rect = plate_rect[[len(plate_rect) - 1]]

    # виділення частини номерного знака для розпізнавання
    for x, y, w, h in plate_rect:
        plate_ = reg_of_intr[y : y + h, x : x + w, :]
        # малювання прямокутника по межі номера
        draw_number_border(plate_img, plate_rect)
        cv2.rectangle(plate_img, (x + 2, y), (x + w - 3, y + h - 5), (51, 181, 155), 3)
        cv2.rectangle(plate_img, (x + 2, y), (x + w - 3, y + h - 5), (51, 181, 155), 3)

    # Додавання тексту
    if text != "":
        plate_img = cv2.putText(
            plate_img,
            text,
            (x - w // 2, y - h // 2),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            0.5,
            (51, 181, 155),
            1,
            cv2.LINE_AA,
        )

    # Повертаємо оброблене зображення з виділеними номерними знаками та область номерного знаку
    return plate_img, plate_, plate_rect


def find_contours(dimensions, img_, echo=True):
    """
    Функція призначена для знаходження контурів символів на зображенні номерного знака.

    Параметри:
        dimensions (list): Список, що містить набір розмірів контурів символів:
                           lower_width, upper_width, lower_height та upper_height.
        img (numpy.ndarray): Вхідне зображення, на якому потрібно знайти контури символів.

    Повертає:
        numpy.ndarray: Масив, що містить зображення контурів символів, відсортованих за координатою x.
    """

    # Знайти всі контури на зображенні
    cntrs, _ = cv2.findContours(img_.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Отримати потенційні розміри
    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]

    # Check largest 5 or  15 contours for license plate or character respectively
    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

    ii = cv2.imread(tmp_file)

    x_cntr_list = []
    img_res = []
    # target_contours = []
    for cntr in cntrs:
        # detects contour in binary image and returns the coordinates of rectangle enclosing it
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        # checking the dimensions of the contour to filter out the characters by contour's size
        # if all(intWidth > lower_width, intWidth < upper_width, intHeight > lower_height, intHeight < upper_height):
        if (
            intWidth > lower_width
            and intWidth < upper_width
            and intHeight > lower_height
            and intHeight < upper_height
        ):
            # stores the x coordinate of the character's contour,
            # to used later for indexing the contours
            x_cntr_list.append(intX)

            char_copy = np.zeros((44, 24))
            # extracting each character using the enclosing rectangle's coordinates.
            char = img_[intY : intY + intHeight, intX : intX + intWidth]
            char = cv2.resize(char, (20, 40))

            cv2.rectangle(
                ii, (intX, intY), (intWidth + intX, intY + intHeight), (76, 202, 102), 2
            )
            if echo:
                plt.imshow(ii, cmap="gray")

            # Make result formatted for classification: invert colors
            char = cv2.subtract(255, char)

            # Resize the image to 24x44 with black border
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0

            # List that stores the character's binary image (unsorted)
            img_res.append(char_copy)

    # Return characters on ascending order with respect to the x-coord (most-left character first)
    # if echo:
    #     plt.show()

    # arbitrary function that stores sorted list of character indeces
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        # stores character images according to their index
        img_res_copy.append(img_res[idx])
    img_res = np.array(img_res_copy)

    return img_res


def segment_characters(image_, echo=True):
    """
    Знаходить символи на зображенні номерного знака.

    Параметри:
     - image: Зображення номерного знака, з якого будуть вилучені символи.

    Повертає:
     - char_list: Список контурів символів, знайдених на зображенні.
    """
    # Попередньо оброблюємо зображення номерного знака
    img_lp = cv2.resize(image_, (333, 75))  # Resize the image to a fixed size
    img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    # Apply binary thresholding
    _, img_binary_lp = cv2.threshold(
        img_gray_lp, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Apply erosion to remove noise
    img_binary_lp = cv2.erode(img_binary_lp, (3, 3))
    # Apply dilation to restore original size
    img_binary_lp = cv2.dilate(img_binary_lp, (3, 3))

    lp_width = img_binary_lp.shape[0]  # Get the width of the license plate
    lp_height = img_binary_lp.shape[1]  # Get the height of the license plate

    # Робимо межі білими (3 пікселі)
    img_binary_lp[0:3, :] = 255  # Minimum character height
    img_binary_lp[:, 0:3] = 255  # Maximum character height
    img_binary_lp[72:75, :] = 255  # Minimum character width
    img_binary_lp[:, 330:333] = 255  # Maximum character width

    # Приблизні розміри контурів символів обрізаного номерного знака
    dimensions = [lp_width / 6, lp_width / 2, lp_height / 10, 2 * lp_height / 3]

    if echo:
        plt.imshow(img_binary_lp, cmap="gray")  # Display the binary image
    if echo:
        plt.show()

    # Save the binary image to a file
    cv2.imwrite(tmp_file, img_binary_lp)

    # Get contours within cropped license plate
    char_list = find_contours(
        dimensions, img_binary_lp, echo=False
    )  # Find character contours

    return char_list  # Return the list of character contours


def fix_dimension(img):
    """
    Функція для вирівнювання розмірів зображення до розмірів (28, 28, 3).

    Параметри:
    img (numpy.ndarray): Вхідне зображення з розмірами (n, m), де n та m - цілі числа.

    Повертає:
    numpy.ndarray: Зображення з розмірами (28, 28, 3), де 3 - кількість каналів (RGB).
    """
    new_img = np.zeros((28, 28, 3))
    for i in range(3):
        new_img[:, :, i] = img
    return new_img


def correction_ua_number(text: str) -> str:
    # позиційна обробка ["1", "0", "7", '8'] <-> ["I", "O", "Z", 'B']
    # if len(text) == 8:
    # ризиковано: наприклад "00OOOO00" буде перетворено на "OO0000OO"
    # "88BBBB88" -> "BB8888BB", "10BIGG88" -> "IO8166BB"
    # "BOSS2000" -> "BO9920OO"
    text_list = list(text)

    for i in [0, 1, 6, 7]:
        text_list[i] = (
            text_list[i]
            .replace("1", "I")
            .replace("i", "I")
            .replace("|", "I")
            .replace("0", "O")
            .replace("7", "Z")
            .replace("8", "B")
            .replace("5", "B")
        )

    for i in [2, 3, 4, 5]:
        text_list[i] = (
            text_list[i]
            .replace("I", "1")
            .replace("|", "1")
            .replace("O", "0")
            .replace("J", "3")
            .replace("G", "6")
            .replace("A", "6")
            .replace("Z", "7")
            .replace("B", "8")
            .replace("Y", "9")
            .replace("S", "9")
        )

    text = "".join(text_list)
    return text


def validate_ukraine_plate(text):
    """
    Validate Ukrainian plate format
    """
    pattern = r"^[A-Z]{2}\d{4}[A-Z]{2}$"
    return bool(re.match(pattern, text))


def prediction_number(char):
    """
    Функція для розпізнавання символів на номерному знаку.
    Параметри:
    char (list): Список зображень символів номерного знаку.
    Повертає:
    str: Рядок, що містить розпізнану номерну знаку, складену з окремих символів.
    """
    dic = {}
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, c in enumerate(characters):
        dic[i] = c

    output = []
    for i, ch in enumerate(char):  # ітеруємося по символах
        img_ = cv2.resize(ch, (28, 28), interpolation=cv2.INTER_AREA)
        img = fix_dimension(img_)
        img = img.reshape(1, 28, 28, 3)  # підготовка зображення для моделі

        # отримуємо ймовірності для кожного класу
        y_proba = model.predict(img, verbose=0)[0]

        y_ = np.argmax(y_proba)  # вибираємо клас з найвищою ймовірністю
        character = dic[y_]  # отримуємо символ, відповідний прогнозованому класу
        output.append(character)  # зберігаємо результат у списку

    plate_number_result = "".join(output)  # об'єднуємо всі символи у рядок

    return plate_number_result


def make_final_image(
    img_, recognized_text="", recognized=True, font_scale=2, font_thickness=3
):

    # Font settings for OpenCV
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Calculate the position for the text near the bottom of the image
    img_height, _ = img_.shape[:2]
    text_position = (50, img_height - 50)

    # Calculate the size of the text box
    (text_width, text_height), baseline = cv2.getTextSize(
        recognized_text, font, font_scale, font_thickness
    )

    # Calculate the coordinates for the white rectangle
    box_coords = (
        (text_position[0] - 10, text_position[1] + baseline - text_height - 30),
        (text_position[0] + text_width + 10, text_position[1] + baseline - 10),
    )

    # Draw the white rectangle
    cv2.rectangle(img_, box_coords[0], box_coords[1], BOX_COLOR, cv2.FILLED)

    color = (0, 155, 0) if recognized else (0, 0, 200)
    # Add recognized text to the image
    img_output = cv2.putText(
        # Copy the image to avoid modifying the original one ???
        # img_.copy(),
        img_,
        recognized_text,
        text_position,
        font,
        font_scale,
        color,
        font_thickness,
        cv2.LINE_AA,
    )
    return img_output


def processing(photo, echo=True, log_on=False):
    """
    основна функція розпізнавання номеру
    """
    # car_photo = os.path.join(current_dir, PHOTO_FOLDER, photo)
    # car_photo_imread = cv2.imread(photo)
    nparr = np.frombuffer(photo, np.uint8)
    car_photo_imread  = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    plate_rect = []
    if log_on:
        print(f"{GRAY}{photo = }{RESET}")

    try:
        output_img, plate, plate_rect = detect_plate(car_photo_imread)
        license_plate_symbols = segment_characters(plate, echo=False)
        plate_number_ = prediction_number(license_plate_symbols)
        print(plate_number_)
    except UnboundLocalError:
        output_img = car_photo_imread
        plate_number_ = "NOT RECOGNIZED"

    plate_number_before_ua = plate_number_
    if len(plate_number_) == 8:
        plate_number_ = correction_ua_number(plate_number_)
        if log_on and plate_number_ != plate_number_before_ua:
            print(CYAN, TAB, plate_number_, "<<< corrected by ua_nm", RESET)

    if not validate_ukraine_plate(plate_number_):
        recognized = False
        if len(plate_rect) > 0:
            draw_number_border(output_img, plate_rect, color_=RED)
    else:
        recognized = True

    if echo:
        img_result = make_final_image(
            output_img, recognized_text=plate_number_, recognized=recognized
        )
        display_image(
            img_result,
            title="Номерний знак" + (" НЕ" if not recognized else "") + " розпізнано",
            recognized=recognized,
        )
    return plate_number_, recognized


# loading the data required for detecting the license plates using cascade classifier.
current_dir = os.getcwd()

plate_cascade_path = os.path.join(current_dir, MODEL_CASCADE)
plate_cascade = cv2.CascadeClassifier(plate_cascade_path)

model_keras = os.path.join(current_dir, MODEL_KERAS)
model = load_model(model_keras, compile=False)

tmp_file = os.path.join(current_dir, TMP)

if __name__ == "__main__":

    # # all photos from [IMAGES]
    # images_for_demo = IMAGES

    # slices - for testing
    images_for_demo = IMAGES[0:11] + IMAGES[-3:]

    for image in images_for_demo:
        plate_number, recognize = processing(image, echo=True, log_on=True)
        if recognize:
            print(YELLOW, TAB, plate_number, RESET)
        else:
            print(RED, TAB, plate_number, "<<< requires attention", RESET)
            print("тут зробимо мануальний ввод номера")
            # input("Enter correct number >>> ")
