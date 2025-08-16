import os

DETECTION_MODEL = os.getenv('DETECTION_MODEL', 'PekingU/rtdetr_v2_r50vd')
LABELS = set(os.getenv('DETECTION_LABEL_SET', 'car,person').split(','))
CROSSING_LINE=500