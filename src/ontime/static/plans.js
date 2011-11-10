$(function() {
    var $doc = $(document);

    function getTimeDiff(minutes) {
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
    }

    function getPeriod(minutes) {
        if (minutes == 0) {
            return { cycle: false, text: '不循环' };
        } else {
            var ret = getTimeDiff(minutes);
            ret.cycle = true;
            ret.text = '每' + ret.num + ret.name;
            return ret;
        }
    }
    $('#stream span.period').each(function() {
        var $t = $(this);
        var period = parseInt($t.attr('period'));
        var text = getPeriod(period).text;
        $t.text(text);
    });

    function getPriority(pri) {
        if (pri <= -10) {
            return '最高优先级';
        } else if (pri <= -5) {
            return '高优先级';
        } else if (pri >= 5) {
            return '低优先级';
        } else if (pri >= 10) {
            return '最低优先级';
        } else {
            return '普通优先级';
        }
    }

    function getTimeout(minutes) {
        if (minutes == 0) {
            return { text: '永远有效' };
        } else {
            var ret = getTimeDiff(minutes);
            ret.text = ret.num + ret.name + '内有效';
            return ret;
        }
    }

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

        function generatePicker($a, $picker, has_class, load_picker) {
            $a.click(function(e) {
                var hadPicker = $picker.hasClass(has_class);
                $doc.click();
                e.stopPropagation();
                
                if (! hadPicker) {
                    var off = $a.position();
                    $picker.css({
                        top: off.top + 'px',
                        left: (off.left + $a.outerWidth()) + 'px'
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
                onSelect: function(dateText, inst) {
                    form.setDate(dateText);
                }
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
                onSelect: function(timeoffset, inst) {
                    form.setTimezone(timeoffset);
                }
            });
        });

        $(document).click(function() {
            $datepicker.datepicker('destroy');
            $timepicker.timepicker('destroy');
            $tzpicker.tzpicker('destroy');
        });

        $form.submit(function(e) {
            if (! $status.val()) {
                alert('请输入消息内容');
                e.preventDefault();
            }
        });

        this.$form = $form;
        this.empty = function() {
            var now = new Date();
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
            $a_period.text(getPeriod(minutes).text);
        };
        this.setPriority = function(pri) {
            $i_pri.val(pri);
            $a_pri.text(getPriority(pri));
        };
        this.setTimeout = function(minutes) {
            $i_timeout.val(minutes);
            $a_timeout.text(getTimeout(minutes).text);
        };
    }

    var form;
    if ($('#new_plan').length) {
        form = new PlanForm($('#new_plan form'));
        form.empty();
    } else if ($('#edit_plan').length) {
        form = new PlanForm($('#edit_plan form'));
    }

    $('#stream').click(function(e) {
        var $target = $(e.target);
        var $par = $target.parents('li');
        var plan_id = $par.attr('plan_id');
        if ($target.hasClass('edit')) {
            var time = $('.time', $par).attr('time');
            time = OT.dt.parseTime(time);
            $('[name=id]', form.$form).val(plan_id);
            form.setStatus($('p', $par).text());
            form.setDate(OT.dt.formatDate(time));
            form.setTime(OT.dt.formatTime(time));
            // FIXME
            form.setTimezone(OT.dt.timeoffset);
            form.setPeriod(0);
            form.setPriority(0);
            form.setTimeout(10);
            $('#edit_plan').dialog({
                width: $('#stream').width() + 36,
                modal: true
            });
            // TODO
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