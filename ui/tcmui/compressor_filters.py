import slimmer
from compressor.filters import FilterBase, FilterError

class SlimmerCSSFilter(FilterBase):
    def output(self, **kwargs):
        return slimmer.css_slimmer(self.content)
