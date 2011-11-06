$(function() {
    // 处理所有时间
    $('.time').each(function() {
        var $t = $(this);
        var time = $t.attr('time');
        if (! time) return;
        var t = time.split(/[:\s-]/);
        time = Date.UTC(
            parseFloat(t[0]), parseFloat(t[1]) - 1, parseFloat(t[2]),
            parseFloat(t[3]), parseFloat(t[4]), parseFloat(t[5]));
        time = new Date(time);
        $t.text(OT.dt.formatDateTime(time, true));
    });
});
