init python:

    def fae_ILY(set_time=None):
        
        if set_time is None:
            set_time = datetime.datetime.now()
        persistent._fae_last_ily = set_time



    def time_love(pass_time):
        
        check_time = datetime.datetime.now()
        
        if persistent._fae_last_ily is None or persistent._fae_last_ily > check_time:
            persistent._fae_last_ily = None
            
            return False
        
        return (check_time - persistent._fae_last_ily) <= pass_time


init 2 python:

    def fae_timePastSince(timekeeper, passed_time, _now=None):
        
        if timekeeper is None:
            return True
        
        elif _now is None:
            _now = datetime.datetime.now()
        
        
        if not isinstance(timekeeper, datetime.datetime):
            timekeeper = datetime.datetime.combine(timekeeper, datetime.time())
        
        return timekeeper + passed_time <= _now
