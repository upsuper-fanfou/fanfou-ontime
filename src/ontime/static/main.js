$(function() {
    // 处理所有时间
    $('.time').each(function() {
        var $t = $(this);
        var time = $t.attr('time');
        if (! time) return;
        var timeoffset = $t.attr('timeoffset');
        if (timeoffset)
            time = OT.dt.parseTime(time, parseInt(timeoffset));
        else
            time = OT.dt.parseTime(time);
        $t.text(OT.dt.formatDateTime(time, true) + ' ' +
            OT.dt.formatTimezone(timeoffset, true));
    });
});
