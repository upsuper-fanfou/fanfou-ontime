(function($) {

    function focusInput() {
        $(this).nextAll('input').focus();
    }

    function stopPropagation(e) {
        e.stopPropagation();
    }

    $.widget('ot.tzpicker', {
        options: {
            value: 480,
            onSelect: function(timeoffset) {},
            timezones: {
                '-660': '中途岛 纽埃岛 萨摩亚',
                '-600': '夏威夷 阿留申',
                '-570': '马克萨斯群岛',
                '-540': '阿拉斯加标准时间',
                '-480': '太平洋标准时间',
                '-420': '北美山区标准时间',
                '-360': '北美中部标准时间',
                '-300': '北美东部标准时间',
                '-270': '委内瑞拉',
                '-240': '大西洋标准时间',
                '-210': '纽芬兰岛标准时间',
                '-180': '阿根廷 巴西 乌拉圭 格陵兰',
                '-60': '佛得角',
                0: '欧洲西部时间 格林尼治标准时间',
                60: '欧洲中部时间',
                120: '欧洲东部时间',
                180: '莫斯科时间',
                210: '伊朗',
                240: '毛里求斯 阿拉伯联合酋长国',
                270: '阿富汗',
                300: '亚美尼亚 马尔代夫 巴基斯坦',
                330: '印度 斯里兰卡',
                345: '尼泊尔',
                360: '孟加拉国 不丹',
                390: '缅甸',
                420: '柬埔寨 老挝 泰国 越南',
                480: '北京时间 新加坡 马来西亚',
                540: '日本 韩国 朝鲜 东帝汶',
                570: '澳洲中部标准时间',
                600: '澳洲东部标准时间',
                660: '瓦努阿图 所罗门群岛',
                690: '诺福克岛',
                720: '斐济 新西兰 图瓦卢',
                780: '汤加'
            }
        },
        _create: function() {
            var $elem = this.element;
            if ($elem.hasClass('hasTzpicker'))
                return;
            $elem.addClass('hasTzpicker');

            var inst = this;
            var tzp_id = Math.random().toString().replace('.', '');
            this.tzp_id = tzp_id;

            var $div = $('<div />');
            $div.addClass('ui-widget ui-widget-content ui-helper-clearfix ui-corner-all')
                .addClass('ui-datepicker-inline ui-datepicker ui-timepicker-div')
                .attr('id', 'ui_tzpicker_' + tzp_id);
            var $header = $('<div />');
            $header.addClass('ui-widget-header ui-helper-clearfix ui-corner-all')
                   .append($('<div />').addClass('ui-datepicker-title').text('选择时区'));
            $div.append($header);

            var $dl = $('<dl />');
            $dl.append($('<dt />').text('时区').attr('id', 'ui_tzpicker_str_label_' + tzp_id))
               .append($('<dd />').attr('id', 'ui_tzpicker_str_' + tzp_id))
               .append($('<dt />').text('选择').attr('id', 'ui_tzpicker_tz_label_' + tzp_id))
               .append($('<dd />').attr('id', 'ui_tzpicker_tz_' + tzp_id))
               .append($('<dt />').text('主要').attr('id', 'ui_tzpicker_list_label_' + tzp_id))
               .append($('<dd />').attr('id', 'ui_tzpicker_list_' + tzp_id).addClass('tzlist'));
            $div.append($dl);

            $elem.append($div);
            $div.show();

            this.tz_slider = $dl.find('#ui_tzpicker_tz_' + tzp_id).slider({
                orientation: 'horizontal',
                min: -720,
                max: 840,
                step: 15,
                slide: function(e, ui) {
                    inst._update(ui.value);
                }
            });

            this._update(this.options.value);
        },
        _update: function(value) {
            this.tz_slider.slider('option', 'value', value);
            this.element.find('#ui_tzpicker_str_' + this.tzp_id)
                .text(OT.dt.formatTimezone(value));
            var tz = this.options.timezones[value];
            this.element.find('#ui_tzpicker_list_' + this.tzp_id)
                .html(tz ? tz : '&nbsp;');
            this.options.onSelect(value, this);
        },
        _setOption: function(key, value) {
            this.options[key] = value;
            if (key == 'value')
                this._update(value);
        },
        destroy: function() {
            this.element.removeClass('hasTzpicker');
            this.element.empty();
            $.Widget.prototype.destroy.call(this);
        }
    });

    $.widget('ot.intpicker', {
        options: {
            value: 0,
            onSelect: function(period, inst) {}
        },
        _create: function() {
            var $elem = this.element;
            if ($elem.hasClass('hasIntpicker'))
                return;
            $elem.addClass('hasIntpicker');
    
            var inst = this;
            var itp_id = Math.random().toString().replace('.', '');
            this.itp_id = itp_id;
    
            var $div = $('<div />');
            $div.addClass('ui-widget ui-widget-content ui-helper-clearfix ui-corner-all')
                .addClass('ui-datepicker-inline ui-datepicker ui-timepicker-div')
                .attr('id', 'ui_intpicker_' + itp_id);
            var $header = $('<div />');
            $header.addClass('ui-widget-header ui-helper-clearfix ui-corner-all')
                   .append($('<div />').addClass('ui-datepicker-title').text('设置循环'));
            $div.append($header);

            function cycleUpdate() {
                if ($('#ui_intpicker_cycle_' + itp_id).prop('checked')) {
                    var num = $('#ui_intpicker_num_' + itp_id).val();
                    var unit = $('#ui_intpicker_unit_' + itp_id).val();
                    if (num)
                        inst._update(parseInt(num) * parseInt(unit), true);
                }
            }

            var $ul = $('<ul />');
            $ul.append($('<li />')
                    .append(
                        $('<input type="radio" />')
                        .attr('id', 'ui_intpicker_nocycle_' + itp_id)
                        .attr('name', 'cycle_' + itp_id)
                        .change(function() {
                            if (this.checked) inst._update(0);
                        }))
                    .append(
                        $('<label />')
                        .attr('for', 'ui_intpicker_nocycle_' + itp_id)
                        .text('不循环')))
               .append($('<li />')
                    .append(
                        $('<input type="radio" />')
                        .attr('id', 'ui_intpicker_cycle_' + itp_id)
                        .attr('name', 'cycle_' + itp_id)
                        .focus(focusInput)
                        .click(focusInput)
                        .change(cycleUpdate))
                    .append(
                        $('<label />')
                        .attr('for', 'ui_intpicker_cycle_' + itp_id)
                        .text('循环：每'))
                    .append(
                        $('<input type="number" />')
                        .attr('id', 'ui_intpicker_num_' + itp_id)
                        .focus(function(e) {
                            $('#ui_intpicker_cycle_' + itp_id).prop('checked', true);
                        })
                        .bind('input', function(e) { setTimeout(cycleUpdate, 10); }))
                    .append(
                        $('<select />')
                        .attr('id', 'ui_intpicker_unit_' + itp_id)
                        .append($('<option />').val(1).text('分钟'))
                        .append($('<option />').val(60).text('小时'))
                        .append($('<option />').val(1440).text('天'))
                        .append($('<option />').val(10080).text('周'))
                        .change(cycleUpdate)
                        .bind('input', function(e) { setTimeout(cycleUpdate, 10); })
                        ));
            $div.append($ul);

            $div.keypress(stopPropagation)
                .keyup(stopPropagation)
                .keydown(stopPropagation)
                .mousedown(stopPropagation)
                .change(stopPropagation);
                .bind('input', stopPropagation);
            $elem.append($div);
            $div.show();
    
            this._update(this.options.value);
        },
        _update: function(value, noupdate) {
            var itp_id = this.itp_id;
            if (! noupdate) {
                var period = OT.td.getPeriod(value);
                if (! period.cycle) {
                    $('#ui_intpicker_nocycle_' + itp_id).prop('checked', true);
                } else {
                    $('#ui_intpicker_cycle_' + itp_id).prop('checked', true);
                    $('#ui_intpicker_num_' + itp_id).val(period.num);
                    $('#ui_intpicker_unit_' + itp_id).val(period.unit);
                }
            }
            this.options.onSelect(value, this);
        },
        _setOption: function(key, value) {
            this.options[key] = value;
            if (key == 'value')
                this._update(value);
        },
        destroy: function() {
            this.element.removeClass('hasIntpicker');
            this.element.empty();
            $.Widget.prototype.destroy.call(this);
        }
    });

    $.widget('ot.pripicker', {
        options: {
            value: 0,
            onSelect: function(value, inst) {}
        },
        _create: function() {
            var $elem = this.element;
            if ($elem.hasClass('hasPripicker'))
                return;
            $elem.addClass('hasPripicker');

            var inst = this;
            var pp_id = Math.random().toString().replace('.', '');
            this.pp_id = pp_id;

            var $div = $('<div />');
            $div.addClass('ui-widget ui-widget-content ui-helper-clearfix ui-corner-all')
                .addClass('ui-datepicker-inline ui-datepicker ui-timepicker-div')
                .attr('id', 'ui_pripicker_' + pp_id);
            var $header = $('<div />');
            $header.addClass('ui-widget-header ui-helper-clearfix ui-corner-all')
                   .append($('<div />').addClass('ui-datepicker-title').text('设置优先级'));
            $div.append($header);

            var $dl = $('<dl />');
            $dl.append($('<dt />').text('优先级').attr('id', 'ui_pripicker_str_label_' + pp_id))
               .append($('<dd />').attr('id', 'ui_pripicker_str_' + pp_id))
               .append($('<dt />').text('选择').attr('id', 'ui_pripicker_pri_label_' + pp_id))
               .append($('<dd />').attr('id', 'ui_pripicker_pri_' + pp_id))
            $div.append($dl);

            $elem.append($div);
            $div.show();

            this.pri_slider = $dl.find('#ui_pripicker_pri_' + pp_id).slider({
                orientation: 'horizontal',
                min: -10,
                max: 10,
                step: 1,
                slide: function(e, ui) {
                    inst._update(-ui.value);
                }
            });

            this._update(this.options.value);
        },
        _update: function(value) {
            this.pri_slider.slider('option', 'value', -value);
            this.element.find('#ui_pripicker_str_' + this.pp_id)
                .text(OT.pri.getPriority(value));
            this.options.onSelect(value, this);
        },
        _setOption: function(key, value) {
            this.options[key] = value;
            if (key == 'value')
                this._update(value);
        },
        destroy: function() {
            this.element.removeClass('hasPripicker');
            this.element.empty();
            $.Widget.prototype.destroy.call(this);
        }
    });

    $.widget('ot.topicker', {
        options: {
            value: 10,
            onSelect: function(timeout, inst) {}
        },
        _create: function() {
            var $elem = this.element;
            if ($elem.hasClass('hasTopicker'))
                return;
            $elem.addClass('hasTopicker');
    
            var inst = this;
            var top_id = Math.random().toString().replace('.', '');
            this.top_id = top_id;

            var $div = $('<div />');
            $div.addClass('ui-widget ui-widget-content ui-helper-clearfix ui-corner-all')
                .addClass('ui-datepicker-inline ui-datepicker ui-timepicker-div')
                .attr('id', 'ui_topicker_' + top_id);
            var $header = $('<div />');
            $header.addClass('ui-widget-header ui-helper-clearfix ui-corner-all')
                   .append($('<div />').addClass('ui-datepicker-title').text('设置超时'));
            $div.append($header);

            function timeoutUpdate() {
                if ($('#ui_topicker_timeout_' + top_id).prop('checked')) {
                    var num = $('#ui_topicker_num_' + top_id).val();
                    var unit = $('#ui_topicker_unit_' + top_id).val();
                    if (num)
                        inst._update(parseInt(num) * parseInt(unit), true);
                }
            }

            var $ul = $('<ul />');
            $ul.append($('<li />')
                    .append(
                        $('<input type="radio" />')
                        .attr('id', 'ui_topicker_timeout_' + top_id)
                        .attr('name', 'timeout_' + top_id)
                        .focus(focusInput)
                        .click(focusInput)
                        .change(timeoutUpdate))
                    .append(
                        $('<input type="number" />')
                        .attr('id', 'ui_topicker_num_' + top_id)
                        .focus(function(e) {
                            $('#ui_topicker_timeout_' + top_id).prop('checked', true);
                        })
                        .keypress(function(e) { setTimeout(timeoutUpdate, 10); }))
                    .append(
                        $('<select />')
                        .attr('id', 'ui_topicker_unit_' + top_id)
                        .append($('<option />').val(1).text('分钟'))
                        .append($('<option />').val(60).text('小时'))
                        .append($('<option />').val(1440).text('天'))
                        .append($('<option />').val(10080).text('周'))
                        .change(timeoutUpdate)
                        .keypress(function(e) { setTimeout(timeoutUpdate, 10); }))
                    .append(
                        $('<label />')
                        .attr('for', 'ui_topicker_timeout_' + top_id)
                        .text('内有效')))
               .append($('<li />')
                    .append(
                        $('<input type="radio" />')
                        .attr('id', 'ui_topicker_notimeout_' + top_id)
                        .attr('name', 'timeout_' + top_id)
                        .change(function() {
                            if (this.checked) inst._update(0);
                        }))
                    .append(
                        $('<label />')
                        .attr('for', 'ui_topicker_nocycle_' + top_id)
                        .text('永远有效')))
            $div.append($ul);

            $div.keypress(stopPropagation)
                .keyup(stopPropagation)
                .keydown(stopPropagation)
                .mousedown(stopPropagation)
                .change(stopPropagation);
            $elem.append($div);
            $div.show();
    
            this._update(this.options.value);
        },
        _update: function(value, noupdate) {
            var top_id = this.top_id;
            if (! noupdate) {
                var timeout = OT.td.getTimeout(value);
                if (! timeout.timeout) {
                    $('#ui_topicker_notimeout_' + top_id).prop('checked', true);
                } else {
                    $('#ui_topicker_timeout_' + top_id).prop('checked', true);
                    $('#ui_topicker_num_' + top_id).val(timeout.num);
                    $('#ui_topicker_unit_' + top_id).val(timeout.unit);
                }
            }
            this.options.onSelect(value, this);
        },
        _setOption: function(key, value) {
            this.options[key] = value;
            if (key == 'value')
                this._update(value);
        },
        destroy: function() {
            this.element.removeClass('hasTopicker');
            this.element.empty();
            $.Widget.prototype.destroy.call(this);
        }
    });

})(jQuery);
