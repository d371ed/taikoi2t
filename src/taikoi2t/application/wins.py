import cv2

from taikoi2t.implements.image import crop, get_roi_bbox
from taikoi2t.models.image import BoundingBox, Image, RelativeBox

__PLAYER_WINS_RELATIVE = RelativeBox(left=1 / 12, top=1 / 5, right=1 / 6, bottom=1 / 4)


def check_player_wins(source: Image, modal: BoundingBox) -> bool:
    cropped = crop(source, get_roi_bbox(modal, __PLAYER_WINS_RELATIVE))
    mean_saturation: int = cv2.mean(cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV))[1]
    # 'Win' has more vivid color than 'Lose'
    return mean_saturation > 50
