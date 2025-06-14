import logging

import cv2

from taikoi2t.implements.image import crop, get_roi_bbox
from taikoi2t.models.image import BoundingBox, Image, RelativeBox

logger: logging.Logger = logging.getLogger("taikoi2t.wins")

__PLAYER_WINS_RELATIVE = RelativeBox(left=1 / 12, top=1 / 5, right=1 / 6, bottom=1 / 4)


def check_player_wins(colored_source: Image, modal: BoundingBox) -> bool:
    cropped = crop(colored_source, get_roi_bbox(modal, __PLAYER_WINS_RELATIVE))
    try:
        mean_saturation: int = cv2.mean(cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV))[1]
        # 'Win' has more vivid color than 'Lose'
        return mean_saturation > 50
    except Exception as e:
        logger.error(e)
        return False
