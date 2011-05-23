from ..core.filters import FieldFilter



class TestCycleStatusFilter(FieldFilter):
    options = [
        (1, "draft"),
        (2, "active"),
        (3, "locked"),
        ]
