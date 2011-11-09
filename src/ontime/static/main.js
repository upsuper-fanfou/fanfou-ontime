$(function() {
    // 处理所有时间
    $('.time').each(function() {
        var $t = $(this);
        var time = $t.attr('time');
        if (! time) return;
        time = OT.dt.parseTime(time);
        $t.text(OT.dt.formatDateTime(time, true));
    });
});
