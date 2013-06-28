import datetime
import time
import re


def _replace_star_with_bounds(s, lower, upper):
    return s.replace('*', '{0}-{1}'.format(lower, upper))


# This regex will match the following:
# '0' => ('0', '', None, None)
# '0/2' => ('0', '/2', None, '2')
# '0-2/2' => ('0', '-2/2', '2', '2')
# '0,2,4' => ('0', ',2,4', None, None)
# '*' => ('{lower}', '', '{upper}', None) - see _replace_with_bounds
# '*/2' => ('{lower}', '/2', {upper}, '/2')
# 0,2,4 => '0,2,4'
# return format: (start, middle, range, step)
# Note: 0,2,4/2 is not supported - further validation raises a ValueError
_cron_parser = re.compile(r'(\d+)((?:,\d+)+|(?:(?:-)(\d+))?(?:(?:/)(\d+))?)')

_mon_lookup = {'jan': '1', 'feb': '2', 'mar': '3', 'apr': '4',
               'may': '5', 'jun': '6', 'jul': '7', 'aug': '8',
               'sep': '9', 'oct': '10', 'nov': '11', 'dec': '12'}
_wkd_lookup = {'mon': '0', 'tue': '1', 'wed': '2',
               'thu': '3', 'fri': '4', 'sat': '5',
               'sun': '6'}


def _normalize(name, field, lower, upper):
    field = field.lower()
    field = _replace_star_with_bounds(field, lower, upper)

    for month in _mon_lookup.keys():
        if field.find(month) >= 0:
            if name == 'month':
                field = field.replace(month, _mon_lookup[month])
            else:
                msg = 'month names should not appear in {0}'
                raise ValueError(msg.format(name))

    for weekday in _wkd_lookup.keys():
        if field.find(weekday) >= 0:
            if name == 'dow':
                field = field.replace(weekday, _wkd_lookup[weekday])
            else:
                msg = 'weekday names should not appear in {0}'
                raise ValueError(msg.format(name))

    return field
                 

def _validate(field, name, lower, upper, rest, start, top):
    # validate comma input
    if rest.find(',') >= 0:
        if field.find('/') >= 0  or field.find('-') >= 0:
            msg = ('comma expressions are not allowed with range '
                   'or step expressions\n  in {0}').format(field)
            raise ValueError(msg)

    else:
        if top is not None and int(start) == int(top):
            msg = 'parsing {0}: {1} must be greater than {2}'
            raise ValueError(msg.format(name, top, start))

        if int(start) < int(lower):
            msg = 'parsing {0}: {1} must be greater than {2}'
            raise ValueError(msg.format(name, start, lower))

        if int(start) > int(upper):
            msg = 'parsing {0}: {1} must be less than {2}'
            raise ValueError(msg.format(name, start, upper))

        if top is not None and int(upper) < int(top):
            msg = 'parsing {0}: {1} must be less than {2}'
            raise ValueError(msg.format(name, top, upper))


def parse_field(field, bounds):
    name, lower, upper = bounds
    field_norm = _normalize(name, field, lower, upper)
    groups = _cron_parser.match(field_norm).groups()
    if not groups:
        raise ValueError('{0} is not a valid cron field spec'.format(field))
    start, rest, top, step = groups
    _validate(field, name, lower, upper, rest, start, top)

    # convert parse into ranges
    if rest == '' and top is None and step is None:  # 0
        return [int(start)]
    if rest and top is None and step is None:  # 0,2,4
        return [int(i) for i in (start + rest).split(',')]
    if top is not None and step is None:  # 0-2
        return range(int(start), int(top) + 1)
    if top is None and step is not None:  # 0/2
        return range(int(start), upper + 1, int(step))
    else:  # 0-15/2
        return range(int(start), int(top) + 1, int(step))


def parse(cron):
    fields = cron.split()
    if len(fields) < 6 or len(fields) > 7:
        msg = 'cron spec should have 6 or 7 fields: {0}'.format(cron)
        raise ValueError(msg)
    field_specs = (('seconds', 0, 59),
                   ('minutes', 0, 59),
                   ('hours', 0, 23),
                   ('dom', 1, 31),
                   ('month', 1, 12),
                   ('dow', 0, 6),
                   ('year', 0, 2999))
    parsed = [parse_field(f, b) for f, b in zip(fields, field_specs)]
    return parsed


def _carry_add_search(x, y, seq):
    """Given values x, y and a sequence seq, this method tries to find
    the first value larger than x in seq. If no such value is found,
    x is set to seq[0] and y is incremented by 1."""
    for i, val in enumerate(seq):
        if x <= val:
            return val, y

    return seq[0], y + 1


def _find_next_day(date, valid_days_of_month, valid_days_of_week,
                   valid_months, valid_years):
    '''Given a datetime and a constraint on what days of the month [1-31],
    what days of the week [0-6], what months, and what years it must
    be, searches through the calendar until such a day is
    found. Returns a datetime.
    '''
    wday = date.timetuple().tm_wday

    while (not wday in valid_days_of_week or
           not date.day in valid_days_of_month or
           not date.month in valid_months):
        dom, month = _carry_add_search(date.day, date.month,
                                       valid_days_of_month)
        month, year = _carry_add_search(month, date.year,
                                        valid_months)
        if year != date.year:
            dom = valid_days_of_month[0]
        if valid_years is not None and year not in valid_years:
            raise ValueError('Task not schedulable')
        date = datetime.datetime(year, month, dom, 0, 0, 0)
        wday = date.timetuple().tm_wday
        if not wday in valid_days_of_week:
            date = datetime.datetime(year, month, dom + 1,
                                     0, 0, 0)
            wday = date.timetuple().tm_wday

    return date


class Schedule(object):
    def __init__(self, form, submitted=None):
        self._submitted = (datetime.datetime.now() if not submitted
                           else submitted)
        self._format = form
        self._parsed = parse(form)
        
    @property
    def cron(self):
        return self._format

    @property
    def submitted(self):
        return self._submitted

    def _find_next(self, now):
        secs, mins, hrs, doms, mons, dows = self._parsed[:6]
        years = None
        if len(self._parsed) == 7:
            years = self._parsed[-1]
        y, m, d, h, minute, s, dow = now.timetuple()[:7]
        dom = now.day
        s2, minute = _carry_add_search(s, minute, secs)
        minute2, h = _carry_add_search(minute, h, mins)
        if minute2 != minute:
            s2 = secs[0]
        h2, d = _carry_add_search(h, d, hrs)
        if h2 != h:
            minute2 = mins[0]
            s2 = mins[0]
        start_date = datetime.datetime(y, m, d, h2, minute2, s2)
        date = _find_next_day(start_date, doms, dows, mons, years)
        if date.second == 0:
            s2 = secs[0]
        if date.minute == 0:
            minute2 = mins[0]
        if date.hour == 0:
            h2 = hrs[0]
        return datetime.datetime(date.year, date.month, date.day,
                                 h2, minute2, s2)

    def next(self):
        now = datetime.datetime.now()
        then = self._find_next(now)
        return then
