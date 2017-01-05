import time


class Date():
    TIME_STAMP_FORMATS = ["%Y",
                          "%Y-%m",
                          "%Y-%m-%d",
                          "%Y-%m-%dT%H",
                          "%Y-%m-%dT%H:%M",
                          "%Y-%m-%dT%H:%M:%S",
                          "%Y-%m-%dT%HZ",
                          "%Y-%m-%dT%H:%MZ",
                          "%Y-%m-%dT%H:%M:%SZ",
                          "%Y-%m-%d %H:%M:%S",
                          "%Y-00-00"]

    def __init__(self, year, month=None, day=None, hour=None, minute=None, second=None):
        from datetime import datetime
        datetime(year, 
                 month  if month  is not None else 1,
                 day    if day    is not None else 1,
                 hour   if hour   is not None else 0,
                 minute if minute is not None else 0,
                 second if second is not None else 0)

        self._year   = year
        self._month  = month
        self._day    = day
        self._hour   = hour
        self._minute = minute
        self._second = second

        Date._validateFormat(str(self))
        
    #------------------------------------------------------------------------------------------#  

    @property
    def year(self):
        return self._year
    
    @property
    def month(self):
        return self._month
    
    @property
    def day(self):
        return self._day
    
    @property
    def hour(self):
        return self._hour
    
    @property
    def minute(self):
        return self._minute
    
    @property
    def second(self):
        return self._second
    
    #------------------------------------------------------------------------------------------#  

    def __eq__(self, rhs):
        if not rhs:
            return False

        return (self.year   == rhs.year   and
                self.month  == rhs.month  and
                self.day    == rhs.day    and
                self.hour   == rhs.hour   and
                self.minute == rhs.minute and
                self.second == rhs.second)

    def __ne__(self, rhs):
        return not(self == rhs)

    def __lt__(self, rhs):
        if not rhs:
            return True

        for l, r in ((self.year,   rhs.year),
                     (self.month,  rhs.month),
                     (self.day,    rhs.day),
                     (self.hour,   rhs.hour),
                     (self.minute, rhs.minute),
                     (self.second, rhs.second)):
            if l < r:
                return True
            elif l > r:
                return False
        return False

    def __hash__(self):
        return hash(str(self))

    #------------------------------------------------------------------------------------------#  

    @staticmethod
    def _validateFormat(date_str):
        pdate = None
        for date_format in Date.TIME_STAMP_FORMATS:
            try:
                pdate = time.strptime(date_str, date_format)
                break
            except ValueError:
                continue

        if pdate is None:
            raise ValueError("Invalid date string: %s." %date_str)

        assert(pdate)
        return pdate, date_format


    @staticmethod
    def parse(date_str):
        date_str = date_str.strip('\x00')

        pdate, date_format = Date._validateFormat(date_str)

        kwargs = {}
        if "%m" in date_format:
            kwargs["month"]  = pdate.tm_mon
        if "%d" in date_format:
            kwargs["day"]    = pdate.tm_mday
        if "%H" in date_format:
            kwargs["hour"]   = pdate.tm_hour
        if "%M" in date_format:
            kwargs["minute"] = pdate.tm_min
        if "%S" in date_format:
            kwargs["second"] = pdate.tm_sec

        return Date(pdate.tm_year, **kwargs)
    
    #------------------------------------------------------------------------------------------#  

    def __str__(self):
        date_str = "%d" %self.year
        if self.month:
            date_str += "-%s" %str(self.month).rjust(2, '0')
            if self.day:
                date_str += "-%s" %str(self.day).rjust(2, '0')
                if self.hour is not None:
                    date_str += "T%s" %str(self.hour).rjust(2, '0')
                    if self.minute is not None:
                        date_str += ":%s" %str(self.minute).rjust(2, '0')
                        if self.second is not None:
                            date_str += ":%s" %str(self.second).rjust(2, '0')
        return date_str

