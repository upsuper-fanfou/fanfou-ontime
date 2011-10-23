$(function() {
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    // 获取时区
    var timeoffset = -(now).getTimezoneOffset();
    var timezone = 'UTC';
    if (timeoffset > 0) {
        timezone += '+';
    } else if (timeoffset < 0) {
        timezone += '-';
        timeoffset = -timeoffset;
    }
    if (timeoffset != 0) {
        if (timeoffset % 60 == 0) {
            timezone += timeoffset / 60;
        } else {
            timezone += Math.floor(timeoffset / 60) + ':' + timeoffset % 60;
        }
    }
    timezone = '(' + timezone + ')';


    function formatTime(time) {
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
        var datestr = fixNumber(time.getFullYear(), 4) + '-' +
                      fixNumber(time.getMonth() + 1, 2) + '-' +
                      fixNumber(time.getDate(), 2);
        var datedelta = diffDate(time);
        if (datedelta == 0) {
            datestr = '今天';
        } else if (datedelta == 1) {
            datestr = '明天';
        } else if (datedelta == 2) {
            datestr = '后天';
        } else if (datedelta == 3) {
            datestr = '大后天';
        } else if (datedelta == -1) {
            datestr = '昨天';
        } else if (datedelta == -2) {
            datestr = '前天';
        } else if (datedelta == -3) {
            datestr = '大前天';
        }
        var timestr = fixNumber(time.getHours(), 2) + ':' +
                      fixNumber(time.getMinutes(), 2);
        return datestr + ' ' + timestr + ' ' + timezone;
    }

    // 处理所有时间
    $('.time').each(function() {
        var $t = $(this);
        var time = $t.attr('time');
        if (! time) return;
        var t = time.split(/[:\s-]/);
        time = Date.UTC(parseInt(t[0]), parseInt(t[1]) - 1, parseInt(t[2]),
                        parseInt(t[3]), parseInt(t[4]), parseInt(t[5]));
        time = new Date(time);
        $t.text(formatTime(time));
    });
});
