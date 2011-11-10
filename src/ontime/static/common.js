var OT = {};

OT.dt = (function() {
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    var timeoffset = -(now).getTimezoneOffset();

    // 特殊日期
    var spec_datestr = {
        '-3': '大前天',
        '-2': '前天',
        '-1': '昨天',
        0: '今天',
        1: '明天',
        2: '后天',
        3: '大后天',
    };

    function fixNumber(num, width) {
        var num = num.toString();
        var delta = width - num.length;
        while (delta > 0) {
            num = '0' + num;
            --delta;
        }
        return num;
    }
    function diffDate(time) {
        var day =
            new Date(time.getFullYear(), time.getMonth(), time.getDate());
        var delta = day.getTime() - today.getTime();
        return delta / 86400000;
    }

    return {
        timeoffset: timeoffset,
        formatTimezone: function(timeoffset) {
            var timezone = 'UTC';
            if (timeoffset > 0) {
                timezone += '+';
            } else if (timeoffset < 0) {
                timeoffset = -timeoffset;
                timezone += '-';
            }
            if (timeoffset != 0) {
                if (timeoffset % 60 == 0)
                    timezone += timeoffset / 60;
                else
                    timezone += Math.floor(timeoffset / 60) +
                        ':' + timeoffset % 60;
            }
            return timezone;
        },
        formatDate: function(date, is_convert) {
            var datestr;
            if (is_convert) {
                var datedelta = diffDate(date).toString();
                if (spec_datestr[datedelta] !== undefined)
                    datestr = spec_datestr[datedelta];
            }
            if (! datestr) {
                datestr = fixNumber(date.getFullYear(), 4) + '-' +
                          fixNumber(date.getMonth() + 1, 2) + '-' +
                          fixNumber(date.getDate(), 2);
            }
            return datestr;
        },
        formatTime: function(time) {
            return fixNumber(time.getHours(), 2) + ':' +
                   fixNumber(time.getMinutes(), 2);
        },
        formatDateTime: function(time, is_convert) {
            return OT.dt.formatDate(time, is_convert) + ' ' +
                   OT.dt.formatTime(time) + ' ' +
                   '(' + OT.dt.formatTimezone(timeoffset) + ')';
        },
        parseTime: function(time) {
            var t = time.split(/[:\s-]/);
            time = Date.UTC(
                parseFloat(t[0]), parseFloat(t[1]) - 1, parseFloat(t[2]),
                parseFloat(t[3]), parseFloat(t[4]), parseFloat(t[5]));
            return new Date(time);
        },
    };
})();

OT.td = (function() {
    return {
        getTimeDiff: function(minutes) {
            var ret = {};
            if (minutes % 10080 == 0) {
                ret.unit = 10080; ret.name = '周';
            } else if (minutes % 1440 == 0) {
                ret.unit = 1440; ret.name = '天';
            } else if (minutes % 60 == 0) {
                ret.unit = 60; ret.name = '小时';
            } else {
                ret.unit = 1; ret.name = '分钟';
            }
            ret.num = minutes / ret.unit;
            return ret;
        },
        getPeriod: function(minutes) {
            if (minutes == 0) {
                return { cycle: false, text: '不循环' };
            } else {
                var ret = OT.td.getTimeDiff(minutes);
                ret.cycle = true;
                ret.text = '每' + ret.num + ret.name;
                return ret;
            }
        },
        getTimeout: function(minutes) {
            if (minutes == 0) {
                return { text: '永远有效' };
            } else {
                var ret = OT.td.getTimeDiff(minutes);
                ret.text = ret.num + ret.name + '内有效';
                return ret;
            }
        }
    };
})();

OT.pri = (function() {
    return {
        getPriority: function(pri) {
            if (pri <= -10) {
                return '最高优先级';
            } else if (pri <= -5) {
                return '高优先级';
            } else if (pri >= 10) {
                return '最低优先级';
            } else if (pri >= 5) {
                return '低优先级';
            } else {
                return '普通优先级';
            }
        }
    };
})();
