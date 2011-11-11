$(function() {
    var $doc = $(document);

    $('#stream span.period').each(function() {
        var $t = $(this);
        var period = parseInt($t.attr('period'));
        var text = OT.td.getPeriod(period).text;
        $t.text(text);
    });

    function PlanForm($form) {
        var form = this;
        var $status = $('[name=status]', $form);
        var $i_date = $('[name=date]', $form);
        var $i_time = $('[name=time]', $form);
        var $i_tz = $('[name=timezone]', $form);
        var $i_period = $('[name=period]', $form);
        var $i_pri = $('[name=priority]', $form);
        var $i_timeout = $('[name=timeout]', $form);
        var $a_date = $('a.date', $form);
        var $a_time = $('a.time', $form);
        var $a_tz = $('a.timezone', $form);
        var $a_period = $('a.period', $form);
        var $a_pri = $('a.priority', $form);
        var $a_timeout = $('a.timeout', $form);
        var $datepicker = $('.datepicker', $form);
        var $timepicker = $('.timepicker', $form);
        var $tzpicker = $('.tzpicker', $form);
        var $intpicker = $('.intpicker', $form);
        var $pripicker = $('.pripicker', $form);
        var $topicker = $('.topicker', $form);

        function generatePicker($a, $picker, has_class, load_picker) {
            $a.click(function(e) {
                var hadPicker = $picker.hasClass(has_class);
                $doc.click();
                e.stopPropagation();
                e.preventDefault();
                
                if (! hadPicker) {
                    var off = $a.position();
                    $picker.css({
                        top: off.top + 'px',
                        left: (off.left + 35) + 'px'
                    });
                    load_picker();
                }
            });
            $picker.click(function(e) { e.stopPropagation(); });
        }

        generatePicker($a_date, $datepicker, 'hasDatepicker', function() {
            $datepicker.datepicker({
                minDate: new Date(),
                defaultDate: $i_date.val(),
                onSelect: form.setDate
            });
        });
        generatePicker($a_time, $timepicker, 'hasDatepicker', function() {
            var time = $i_time.val().split(':');
            $timepicker.timepicker({
                timeOnly: true,
                showButtonPanel: false,
                stepHour: 1,
                stepMinute: 1,
                hour: parseInt(time[0]),
                minute: parseInt(time[1]),
                onSelect: function(timeText, inst) {
                    // Timepicker 在第一次点击小时条的时候
                    // 会传入一个空字符串
                    if (timeText)
                        form.setTime(timeText);
                }
            });
        });
        generatePicker($a_tz, $tzpicker, 'hasTzpicker', function() {
            $tzpicker.tzpicker({
                value: $i_tz.val(),
                onSelect: form.setTimezone
            });
        });
        generatePicker($a_period, $intpicker, 'hasIntpicker', function() {
            $intpicker.intpicker({
                value: $i_period.val(),
                onSelect: form.setPeriod
            });
        });
        generatePicker($a_pri, $pripicker, 'hasPripicker', function() {
            $pripicker.pripicker({
                value: $i_pri.val(),
                onSelect: form.setPriority
            });
        });
        generatePicker($a_timeout, $topicker, 'hasTopicker', function() {
            $topicker.topicker({
                value: $i_timeout.val(),
                onSelect: form.setTimeout
            });
        });

        $(document).click(function() {
            $datepicker.datepicker('destroy');
            $timepicker.timepicker('destroy');
            $tzpicker.tzpicker('destroy');
            $intpicker.intpicker('destroy');
            $pripicker.pripicker('destroy');
            $topicker.topicker('destroy');
        });

        $form.submit(function(e) {
            if (! $status.val()) {
                alert('请输入消息内容');
                e.preventDefault();
            }
        });

        this.$form = $form;
        this.empty = function() {
            var now = Date.now() + OT.dt.timeoffset * 60000;
            now = new Date(now);
            this.setStatus('');
            this.setDate(OT.dt.formatDate(now));
            this.setTime(OT.dt.formatTime(now));
            this.setTimezone(OT.dt.timeoffset);
            this.setPeriod(0);
            this.setPriority(0);
            this.setTimeout(10);
        };
        this.setStatus = function(status) {
            $status.val(status);
        };
        this.setDate = function(date) {
            $i_date.val(date);
            $a_date.text(date);
        };
        this.setTime = function(time) {
            $i_time.val(time);
            $a_time.text(time);
        };
        this.setTimezone = function(timeoff) {
            $i_tz.val(timeoff);
            $a_tz.text(OT.dt.formatTimezone(timeoff));
        };
        this.setPeriod = function(minutes) {
            $i_period.val(minutes);
            $a_period.text(OT.td.getPeriod(minutes).text);
        };
        this.setPriority = function(pri) {
            $i_pri.val(pri);
            $a_pri.text(OT.pri.getPriority(pri));
        };
        this.setTimeout = function(minutes) {
            $i_timeout.val(minutes);
            $a_timeout.text(OT.td.getTimeout(minutes).text);
        };
    }

    var form;
    if ($('#new_plan').length) {
        var $form = $('#new_plan form');
        form = new PlanForm($form);
        form.empty();

        var $status = $('[name=status]', $form);
        var $left = $('#title span strong');
        setInterval(function() {
            var left = 140 - $status.val().length;
            if (left != $left.text())
                $left.text(left);
        }, 30);
    } else if ($('#edit_plan').length) {
        form = new PlanForm($('#edit_plan form'));
    }

    $('#stream').click(function(e) {
        var $target = $(e.target);
        var $par = $target.parents('li');
        var plan_id = $par.attr('plan_id');
        if ($target.hasClass('edit')) {
            $('[name=id]', form.$form).val(plan_id);
            form.setStatus($('p', $par).text());

            var $time = $('.time', $par);
            var time = OT.dt.parseTime($time.attr('time'),
                                       parseInt($time.attr('timeoffset')));
            form.setDate(OT.dt.formatDate(time));
            form.setTime(OT.dt.formatTime(time));
            var timeoffset = parseInt($time.attr('timeoffset'));
            form.setTimezone(timeoffset);

            var $period = $('.period', $par);
            if ($period.length)
                form.setPeriod(parseInt($period.attr('period')));
            else
                form.setPeriod(0);

            var pri = $('.priority', $par).attr('priority');
            form.setPriority(parseInt(pri));

            var timeout = $('.timeout', $par).attr('timeout');
            form.setTimeout(parseInt(timeout));

            $('#edit_plan').dialog({
                width: $('#stream').width() + 36,
                modal: true
            });
        } else if ($target.hasClass('delete')) {
            e.preventDefault();
            if (confirm('真的要删除这条计划吗？')) {
                var $form = $('#form_delete');
                $('[name=id]', $form).val(plan_id);
                $form.submit();
            }
        }
    });
});
