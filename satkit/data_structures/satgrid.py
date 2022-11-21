from collections import OrderedDict
from typing import Union

from textgrids import Interval, TextGrid, Tier, Transcript
from textgrids.templates import (long_header, long_interval, long_point,
                                 long_tier)
from typing_extensions import Self


class SatInterval:
    """TextGrid Interval representation to enable editing with GUI."""

    @classmethod
    def from_textgrid_interval(cls, 
        interval: Interval, 
        prev: Union[None, Self], 
        next: Union[None, Self]=None) -> Self:
        """
        Copy the info of a Python TextGrids Interval into a new SatInterval.
        
        Only xmin and text are copied from the original Interval. xmax is
        assumed to be handled by either the next SatInterval or the constructing
        method if this is the last Interval. 

        Since SatIntervals are doubly linked, an attempt will be made to link
        prev and next to this interval. 
        
        Returns the newly created SatInterval.
        """
        return cls(
            begin=interval.xmin,
            text=interval.text,
            prev=prev,
            next=next)

    def __init__(self, 
            begin: float, 
            text: Union[None, Transcript], 
            prev: Union[None, Self]=None,
            next: Union[None, Self]=None) -> None:
        self.begin = begin
        self.text = text

        self.prev = prev
        if self.prev:
            self.prev.next = self

        self.next = next
        if self.next:
            self.next.prev = self

    @property
    def mid(self) -> Union[float, None]:
        """
        Middle time point of the interval.
        
        This is a property that will return None
        if this Interval is the one that marks
        the last boundary.
        """
        if self.text:
            return (self.begin+self.next.begin)/2
        else:
            return None

    def is_legal_value(self, time:float) -> bool:
        """
        Check if the given time is between the previous and next boundary.
        
        Usual caveats about float testing apply. Tests used do not include
        equality with either bounding boundary, but that may or may not be
        trusted to be the actual case.

        Returns True, if time is  between the previous and next boundary.
        """
        return time < self.next.begin and time > self.prev.begin


class SatTier(list):
    """TextGrid Tier representation to enable editing with GUI."""

    @classmethod 
    def from_textgrid_tier(cls, tier:Tier) -> Self:
        """
        Copy a Python TextGrids Tier as a SatTier.
        
        Returns the newly created SatTier.
        """
        return cls(tier)

    def __init__(self, tier: Tier) -> None:
        last_interval = None
        prev = current = None
        for interval in tier:
            current = SatInterval.from_textgrid_interval(interval, prev)
            self.append(current)
            prev = current 
            last_interval = interval
        self.append(SatInterval(last_interval.xmax, None, prev))

    @property
    def begin(self) -> float:
        """
        Begin timestamp.
        
        Corresponds to a TextGrid Interval's xmin.

        This is a property and the actual value is generated from the first
        SatInterval of this SatTier.
        """
        return self[0].begin

    @property
    def end(self) -> float:
        """
        End timestamp.
        
        Corresponds to a TextGrid Interval's xmin.

        This is a property and the actual value is generated from the last
        SatInterval of this SatTier.
        """
        # This is slightly counter intuitive, but the last interval is infact
        # empty and only represents the final boundary. So its begin is 
        # the final boundary.
        return self[-1].begin

    @property
    def is_point_tier(self) -> bool:
        """Is this Tier a PointTier."""
        return False


class SatGrid(OrderedDict):
    """
    TextGrid representation which makes editing easier.
    
    SatGrid is a OrderedDict very similar to Python textgrids TextGrid, but made
    up of SatTiers that in turn contain intervals or points as doubly linked
    lists instead of just lists. See there relevant classes for more details.
    """

    def __init__(self, textgrid: TextGrid) -> None:
        for tier_name in textgrid:
            self[tier_name] = SatTier.from_textgrid_tier(textgrid[tier_name])
    
    def as_textgrid(self):
        pass

    @property
    def begin(self) -> float:
        """
        Begin timestamp.
        
        Corresponds to a TextGrids xmin.

        This is a property and the actual value is generated from the first
        SatTier of this SatGrid.
        """
        key = list(self.keys())[0]
        return self[key].begin

    @property
    def end(self) -> float:
        """
        End timestamp.
        
        Corresponds to a TextGrids xmax.

        This is a property and the actual value is generated from the first
        SatTier of this SatGrid.
        """
        # First Tier
        key = list(self.keys())[0]
        # Return the end of the first Tier.
        return self[key].end
        
    def format_long(self) -> str:
        '''Format self as long format TextGrid.'''
        global long_header, long_tier, long_point, long_interval
        out = long_header.format(self.begin, self.end, len(self))
        tier_count = 1
        for name, tier in self.items():
            if tier.is_point_tier:
                tier_type = 'PointTier'
                elem_type = 'points'
            else:
                tier_type = 'IntervalTier'
                elem_type = 'intervals'
            out += long_tier.format(tier_count,
                                    tier_type,
                                    name,
                                    self.begin,
                                    self.end,
                                    elem_type,
                                    len(tier)-1)
            for elem_count, elem in enumerate(tier, 1):
                if tier.is_point_tier:
                    out += long_point.format(elem_count,
                                             elem.xpos,
                                             elem.text)
                elif elem.next:
                    out += long_interval.format(elem_count,
                                                elem.begin,
                                                elem.next.begin,
                                                elem.text)
                else:
                    # The last interval does not contain anything.
                    # It only marks the end of the file and final 
                    # interval's end. That info got already used by
                    # elem.next.begin above.
                    pass
        return out