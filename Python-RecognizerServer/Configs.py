import cv2


# Server Config
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 20000
LISTEN_NUM = 10

CONNECT_STATE_HELLO = 0
CONNECT_STATE_BYE = 1


# Recognizer Mode
RECOGNIZER_MODE= "IMAGE"


# RECOGNIZER_MODE = 0 → IMAGE
AVERAGE_SIZE = 5
THRESHOLD = 0.01
DRAWING_FPS = 20
INFERENCE_FPS = 4
DEVICE = "cuda:0"
MODEL_CONFIG = "Recognizer/ImageModule/model_config.py"
CHECKPOINT = "Recognizer/ImageModule/checkpoint.pth"
LABEL = "Recognizer/ImageModule/label.txt"

# RECOGNIZER_MODE = 1 → IMU



# RECOGNIZER_MODE = 2 → Both


# Definiation
NOT_CHOOSE = -1

MODE_UNMOVABLE = 0
MODE_MOVABLE = 1

OPPONENT_DISABLE = 0
OPPONENT_ENABLE = 1

TASK_NUMBERADD = 0
TASK_COLORCHANGE = 1

DRIBBLING_POUND = 0
DRIBBLING_CROSSOVER = 1
DRIBBLING_ONESIDELEG = 2
DRIBBLING_BEHIND = 3

STATE_START = 0
STATE_PAUSE = 1
STATE_FINISH = 2

DRIBBLING_TYPE = ["pound dribble", "cross over dribble", "one side leg dribble", "behind dribble"]
DRIBBLING_MAPPING = {"pound dribble":0, "cross over dribble":1, "one side leg dribble":2, "behind dribble":3}


# Camera Visualize
FONT_FACE = cv2.FONT_HERSHEY_COMPLEX_SMALL 
FONT_SCALE = 1
FONT_COLOR_NORMAL = (255, 255, 255)
FONT_COLOR_HIGHTLIGHT = (0, 255, 255)
FONT_COLOR_MSG = (128, 128, 128)
FONT_THICKNESS = 1
FONT_LINETYPE = 1



user_choosen_mode = NOT_CHOOSE
user_choosen_opponent = NOT_CHOOSE
user_choosen_task = NOT_CHOOSE
user_choosen_dribbling = NOT_CHOOSE
user_serial_id = 2022041021245853
training_state = NOT_CHOOSE

connect_state = NOT_CHOOSE


# Attention Visualization

ATTENTION_WIDTH = 4096
ATTENTION_HEIGHT = 2048
ATTENTION_VIDEO_SIZE = (1024, 512)

train_num = 1
# train_id = 1
round_num = 3
# round_id = 1
