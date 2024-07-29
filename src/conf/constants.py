import enum

NAME_MIN_LENGTH = 3
NAME_MAX_LENGTH = 30

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
EMAIL_MAX_LENGTH = 150

PASSWORD_MIN_LENGTH = 5
PASSWORD_MAX_LENGTH = 255

TOKEN_MAX_LENGTH = 255

LICENSE_PLATE_MAX_LENGTH = 8
RATE_NAME_MAX_LENGHT = 50
COMMENT_MAX_LENGTH = 250
MESSAGE_MAX_LENGTH = 250

NOT_NUMBER = [
    "UA",
    "JA",
    "11",
    "10",
    "16",
    "RXETD",
    "21",
    "22",
    "I",
    "Q",
    "X",
    "II",
    "AS",
    "F923",
    "SS00",
    "RANGEROVER",
    "RANGE",
    "ROVER",
    "KIA",
]

IMAGES = []
IMAGE_PATH = ''
# IMAGE_PATH_LENGTH = 250

AVATAR_PATH_LENGTH = 250

# ALLOWED_CROP_MODES = ("fill", "thumb", "fit", "limit", "pad", "scale", None)
ACCESS_TOKEN_TIME_LIVE = 60 # 30


# class CropMode(str, enum.Enum):
#     fill = "fill"
#     thumb = "thumb"
#     fit = "fit"
#     limit = "limit"
#     pad = "pad"
#     scale = "scale"


# class EffectMode(str, enum.Enum):
#     vignette = "vignette"
#     sepia = "sepia"
#     pixelate = "pixelate:1"
#     cartoonify = "cartoonify"


# class Effect(str, enum.Enum):
#     al_dente = "art:al_dente"
#     audrey = "art:audrey"
#     eucalyptus = "art:eucalyptus"
#     zorro = "art:zorro"
#     frost = "art:frost"
#     hokusai = "art:hokusai"
#     incognito = "art:incognito"
#     peacock = "art:peacock"
#     primavera = "art:primavera"
#     quartz = "art:quartz"
DAYS_IN_MONTH = 30
