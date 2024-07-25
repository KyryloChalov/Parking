import cv2
# import os
import re

import matplotlib.pyplot as plt

from constants import IMAGES, NOT_NUMBER

# позиційна обробка ["1", "0", "7", '8'] <-> ["I", "O", "Z", 'B']
def correction_ua_number(text):
    # if len(text) == 8:
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
            .replace("Z", "7")
            .replace("B", "8")
        )

    text = "".join(text_list)
    return text


# Validate Ukrainian plate format
def validate_ukraine_plate(text):
    pattern = r"^[A-Z]{2}\d{4}[A-Z]{2}$"
    return bool(re.match(pattern, text))


# обробка тексту, що розпізнано на номері
def processing_number_text(result):
    text_up = ""

    for line in result:

        for word in line:

            text = word[1][0].strip().replace("\n", "").replace(" ", "")

            if len(text) == 8:
                text = correction_ua_number(text)

            if text in NOT_NUMBER:
                continue

            # для американських номерів (в 2 ряди)
            if re.match(r"^[A-Z]{4}$", text):
                text_up = text
            elif re.match(r"^\d{4}$", text) and re.match(r"^[A-Z]{4}$", text_up):
                text = text_up[:2] + text + text_up[2:]
                text_up = ""

            # милиця - щоб повертати номери, які визначено як українські
            output_text = text

            if re.match(r"^[A-Z0-9]+$", text):
                if validate_ukraine_plate(text):
                    print(f"Detected License Plate: \033[33m{text}\033[0m")  # Yellow
                else:
                    print(f" Invalid License Plate: \033[31m{text}\033[0m")  # Red
        # print(f"{output_text = }")
    return output_text


# Extract license plate text using PaddleOCR
def extract_license_plate_text(image_path):

    # OCR debug - сірим кольором
    print("\033[90m", end="")
    result = ocr.ocr(image_path)
    print("\033[0m", end="")

    return processing_number_text(result)


# display image function
def display(img_, title=""):
    """
    функція виводу зображень з заголовком
    """
    img = cv2.cvtColor(img_, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 6))
    ax = plt.subplot(111)
    ax.imshow(img)
    plt.axis("off")
    plt.title(title, fontsize=20)
    plt.show()


# display result function
def display_result(
    img_,
    title="",
    recognized_text="",
    font_scale=2,
    font_thickness=3,
):

    BOX_COLOR = (255, 255, 255)
    # Copy the image to avoid modifying the original one
    img = img_.copy()
    # Font settings for OpenCV
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Position for the ocr-text near the top of the image
    text_position = (50, 100)  # Starting position for the text

    # Calculate the size of the text box
    (text_width, text_height), baseline = cv2.getTextSize(
        recognized_text, font, font_scale, font_thickness
    )

    # Calculate the coordinates for the white rectangle
    box_coords = (
        (text_position[0] - 10, text_position[1] + baseline - text_height - 30),
        (text_position[0] + text_width + 10, text_position[1] + baseline - 10),
    )

    # Draw the 'BOX_COLOR' rectangle
    cv2.rectangle(img, box_coords[0], box_coords[1], BOX_COLOR, cv2.FILLED)

    # Add recognized text to the image
    img = cv2.putText(
        img,
        recognized_text,
        text_position,
        font,
        font_scale,
        (255, 0, 0),
        font_thickness,
        cv2.LINE_AA,
    )

    display(img, title=title)

# Process each image and extract license plate text
num_photo = 0
for image in IMAGES:

    clear_number = image.split(".")[0].split("_")[0]
    image_path = cv2.imread("../images/" + image)

    # Check if the image is loaded correctly
    if image_path is None:
        print(
            f"\033[31mError: \033[0mFile \033[37m {image} \033[0m could not be loaded"
        )
        break

    num_photo += 1
    print("\n", 80 * "=", "\033[90m", num_photo, "\033[0m")
    print(f"      Processing image: \033[33m{clear_number}\033[0m")

    plate_number_ocr = extract_license_plate_text(image_path)  # ocr

    display_result(
        image_path,
        title=clear_number + " - дійсний номерний знак",
        recognized_text=plate_number_ocr,
    )
