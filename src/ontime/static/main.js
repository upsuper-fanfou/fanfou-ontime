$(function() {
    // 处理所有时间
    $('.time').each(function() {
        var $t = $(this);
        var time = $t.attr('time');
        if (! time) return;
        var timeoffset = $t.attr('timeoffset');
        if (timeoffset)
            timeoffset = parseInt(timeoffset);
        else
            timeoffset = OT.dt.timeoffset;
        time = OT.dt.parseTime(time, timeoffset);
        $t.text(OT.dt.formatDateTime(time, true) + ' ' +
            OT.dt.formatTimezone(timeoffset, true));
    });
});
