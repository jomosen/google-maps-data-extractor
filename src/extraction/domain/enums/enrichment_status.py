from enum import IntFlag, auto

class EnrichmentStatus(IntFlag):
    NONE = 0
    WEBSITE = auto()  # 1
    GBP = auto()      # 2
    SOCIAL = auto()   # 4
    COMPLETE = WEBSITE | GBP | SOCIAL  # 7