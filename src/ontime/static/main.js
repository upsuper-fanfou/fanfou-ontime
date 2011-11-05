$(function() {
    // 处理所有时间
    $('.time').each(function() {
        var $t = $(this);
        var time = $t.attr('time');
        if (! time) return;
        var t = time.split(/[:\s-]/);
        time = Date.UTC(parseInt(t[0]), parseInt(t[1]) - 1, parseInt(t[2]),
                        parseInt(t[3]), parseInt(t[4]), parseInt(t[5]));
        time = new Date(time);
        $t.text(OT.dt.formatDateTime(time, true));
    });
});
