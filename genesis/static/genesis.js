/**
 * Created by evren on 12/10/16.
 */

function add_footer_button(params) {
    params.id = params.id || Math.random().toString().substring(2);
    params.target = params.target || '_ifrm';
    if (params.onclick) {
        params.url = 'javascript:void(0);'
    }
    grp.jQuery('footer ul:first').append('<li><a id="' + params.id + '" class="grp-button" href="' + params.url + '" target="' + params.target + '">' + params.name + '</a></li>');
    if (params.onclick) {
        grp.jQuery('#' + params.id).click(params.onclick);
    }

}

function is_editing(name) {
    var klses = grp.jQuery('body').attr('class').split(' ');
    for (var kls of klses) {
        if (kls.indexOf('-') > 0 && kls.split('-')[1] == name) {
            return true;
        }
    }
}
function is_listing(name) {
    return Boolean(grp.jQuery('a[href*="/admin/lab/' + name + '/add/"].grp-add-link').length && grp.jQuery('body.grp-change-list').length)
}

function get_editing_id() {
    return parseInt(document.documentURI.split('/change/')[0].split('/').pop())
}

function add_value_span($obj, $sibling) {
    add_after = $sibling || $obj;
    add_after.after($('<span class="info_label"></span>').html($obj.text() || $obj.val())).addClass('hide_it_f');
}
function lock_unlock_analyse_states() {
    // prevent changing of existing analyse  states
    // ( double click on container div allows editing with a warning)
    no_of_wg = $('#id_no_of_groups').val();
    if (no_of_wg == 1) {
        $('div.grp-td.group').hide();
        $('div.grp-td.current_state').hide();
        $('div.grp-th.son-durum').hide();
        $('div.grp-th.grup').hide();
    } else if (no_of_wg == 2) {
        $('div.grp-td.group input[type=radio][value=3]').parent().hide();
    }
    $('div[id^=state_set].has_original div.grp-tr').each(function () {
        var row = $(this);
        row.find('input[type=radio][checked=checked]').each(function () {
            inrad = $(this);
            add_value_span(inrad, inrad.closest('ul'));
        });
        select = row.find('select');
        add_value_span(select.find('option:selected'), select);
        add_value_span(row.find('textarea'));
        row.dblclick(function () {
            alert("Mecbur kalmadıkça değiştirmek yerine yeni bir kayıt eklemeyi tercih ediniz.");
            row.find('.hide_it_f').removeClass('hide_it_f');
            row.find('.info_label').addClass('hide_it_f');
        })
    });
}

function get_pk(obj, $obj) {
    // returns pk of object from id of widgets formatted like this: id="id_state_set-1-definition"
    obj = obj || $obj[0]
    try {
        return obj.id.match(/-(\d*)-/)[1]
    } catch (e) {
        return -1;
    }
}


function create_selectbox(optionList, toElem, selections, is_multiple) {
    var combo = $("<select class='comboin'></select>");
    if (is_multiple) {
        combo.attr('multiple', 'multiple');
    }
    combo.append($("<option value=''> --- </option>"));
    $.each(optionList, function (i, el) {
        var option = $("<option>" + el + "</option>");
        if (selections.indexOf(el) > -1) {
            option.attr('selected', true);
        }
        combo.append(option);
    });
    $(combo).change(function () {
        console.log("Change", toElem);
        toElem.val(is_multiple ? combo.val().join(',') : combo.val());
    });

    return combo;
}

function modify_parameter_list_edit(selector, data_field_selector) {
    $(selector).each(function () {

        var tr = $(this);
        window.tr = tr;
        console.log(tr);
        console.log(tr.find('input.keydata').val());
        var keyData = JSON.parse(tr.find('input.keydata').val());
        if (keyData.presets.length) {
            var txt_field = tr.find('input.vTextField');
            txt_field.hide();
            var combo = create_selectbox(keyData.presets, txt_field, txt_field.val().split(','), keyData.is_multiple);
            // combo.val(txt_field.val());
            txt_field.after(combo);
            var manual_button = $('<input class="manualb" type="button" value="  ❄  ">');
            manual_button.click(function () {
                if (!keyData.auto_preset && txt_field.css('display') == 'none') {
                    alert("Öntanımlı değerler dışında bir değer girmek üzeresiniz!")
                }
                combo.toggle();
                txt_field.toggle();
            })
            combo.after(manual_button);
        }
    })
}


function create_selectbox_for_analyse_state() {
    var selbox = $(this);
    pk = get_pk(this);
    remove_selectbox();
    if (selbox.val()) {
        $.get('/lab/api/analyse_state_comments_for_statetype/' + selbox.val(), function (data, st, xhr) {
            window._last_selbox_id = pk;
            create_autocomplete_widget(data, $('#id_state_set-' + pk + '-comment'));
        });
    }
}

function remove_selectbox(txt_field) {
    if (window._last_selbox_id) {
        txt_field = $('#id_state_set-' + window._last_selbox_id + '-comment');
        txt_field.show();
        txt_field.siblings('select,input').remove();
        window._last_selbox_id = null;
    }
}


function create_autocomplete_widget(data, txt_field) {
    if (data.presets.length) {
        txt_field.hide();
        var combo = create_selectbox(data.presets, txt_field, txt_field.val().split(','), data.is_multiple);
        // combo.val(txt_field.val());
        txt_field.after(combo);
        var manual_button = $('<input class="manualb" type="button" value="  ❄  ">');
        manual_button.click(function () {
            if (!data.auto_preset && txt_field.css('display') == 'none') {
                alert("Öntanımlı değerler dışında bir değer girmek üzeresiniz!")
            }
            combo.toggle();
            txt_field.toggle();
        })
        combo.after(manual_button);
    }
}

function swap_add_another_status_row() {
    // move top the analyse change_form add new state line
    var add_new = $('#state_set-group div.grp-dynamic-form.grp-module.grp-tbody').not('.has_original');
    var th = add_new.siblings('.grp-thead');
    th.after(add_new.detach()[0]);
    $('div#state_set-group div.grp-dynamic-form').not('.has_original').not('.grp-transparent').find('div.grp-td.current_state > div > img').css('opacity', 0.3);
}

var object_id = get_editing_id();

function show_fieldsets() {
    if (window.location.hash.indexOf('show_fieldset=') > -1) {
        fieldsets = window.location.hash.split('show_fieldset=')[1].split(',');
        // debugger;
        $('.analyse_box').addClass('grp-closed');
        for (var fieldset of fieldsets) {
            $('.analyse_box.' + fieldset).removeClass('grp-closed');
        }
    }
}
function only_show_fieldsets() {
    if (window.location.hash.indexOf('only_show_fieldset=') > -1) {
        fieldsets = window.location.hash.split('only_show_fieldset=')[1].split(',');
        // debugger;
        $('.analyse_box, header').addClass('hide_fieldset');
        for (var fieldset of fieldsets) {
            $('.analyse_box.' + fieldset).removeClass('hide_fieldset');
        }
    }
}

function patch_fk_plus_icons() {
    $('a.icons-add-another').remove();
    $('a.grp-icon.grp-add-handler').remove();
    $('a.icons-tools-viewsite-link').remove();
    // $('a.icons-add-another').each(function () {
    //     $a = $(this);
    //     var hrf = $a.attr('href');
    //     $a.click(function () {
    //         window.open(hrf + '?_changelist_filters=_to_field%3Did%26_popup%3D1&_popup=1&_to_field=id','', "width=600, height=600");
    //         return false;
    //     }).attr('href', '').attr('target', '');
    // });
}

function patch_edit_views() {

    // change text of _save

    // hide empty (looking) <li> elements of hided "_save" and "_addanother" buttons.
    // grp.jQuery('body:not(.grp-popup) input[name="_save"], body:not(.grp-popup) input[name="_addanother"]').parent().hide()
    grp.jQuery('body:not(.grp-popup) input[name="_save"]').parent().hide()


    // get rid of those empty cells
    grp.jQuery('div.c-1').map(function () {
        self = grp.jQuery(this);
        if (self.html() == "&nbsp;") self.hide();
    })
    show_fieldsets();
    only_show_fieldsets();
    setTimeout(patch_fk_plus_icons, 0);

    if (is_editing('analyse') && object_id) {
        add_footer_button({
            url: '/lab/analyse_barcode/' + object_id + '/',
            name: 'Barkod Yazdır'
        });
        var is_finished = grp.jQuery('div.finished img[alt=True]').length;
        var group_membership = $('input#id_group_relation').val();

        modify_parameter_list_edit('div#parametervalue_set-group div.form-row.has_original');

        lock_unlock_analyse_states();
        setTimeout(swap_add_another_status_row, 0);

        $("select[id$=-definition]:not([id*=prefix])").change(create_selectbox_for_analyse_state);

        // fade check mark image of new state form


        if (group_membership) {


            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/admin/lab/parametervalue/?q=' + group_membership + '#pop_up=1',
                        iframeWidth: 1100, iframeHeight: 600
                    });
                },
                name: 'Tüm Paneli Görüntüle'
            });

            add_footer_button({
                url: '/lab/report_for_panel/' + group_membership + '/',
                name: 'Panel Rapor Yazdır',
            });

            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/lab/report_for_panel/' + group_membership + '/',
                        iframeWidth: 1100, iframeHeight: 600
                    });
                },
                name: 'Panel Rapor Görüntüle',
            });


        }

        if (is_finished) {

            add_footer_button({
                url: '/lab/analyse_report/' + object_id + '/',
                name: 'Rapor Yazdır'
            });

            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/lab/analyse_report/' + object_id + '/#noprint',
                        iframeWidth: 1100, iframeHeight: 600
                    });
                },
                name: 'Rapor Görüntüle'
            });
        }
    }
    if (is_editing('admission')) {
        var customer_is_patient = $('#id_payment_set-0-patient').val();

        grp.jQuery('input[name="_continue"]').val('Kaydet ve Düzenle');
        grp.jQuery('input[name="_addanother"]').val('Kaydet');
        function link_payment_responsible() {

            var _patient = $('#id_payment_set-0-patient').val();
            var _institute = $('#id_payment_set-0-institution').val();
            $('div.grp-td.patient').find('select').val(_patient);
            $('div.grp-td.institution').find('select').val(_institute);
        }

        $('#payment_set-group a.grp-add-handler').click(function () {
            setTimeout(link_payment_responsible, 0);
        });

        setTimeout(function () { // allow grapelli to do it's magic
            grp.jQuery('#id_patient-autocomplete').parent().attr('style', 'max-width:440px !important');
        }, 0);
        if (object_id) {
            add_footer_button({
                url: '/lab/admission_barcode/' + object_id + '/?print_analyses=1',
                name: 'Barkod-Set Yazdır'
            });
            add_footer_button({
                url: '/lab/admission_barcode/' + object_id + '/',
                name: 'Barkod Yazdır'
            });

            grp.jQuery.getJSON('/com/invoice_id_of_admission/' + object_id + '/', function (data, status, xhr) {
                if (data['id']) {
                    add_footer_button({
                        url: '/com/print_invoice/' + object_id + '/',
                        name: 'Faturayı TEKRAR Bas: #' + data['id']
                    });
                } else {
                    grp.jQuery.getJSON('/com/next_invoice_id/', function (data, status, xhr) {
                        add_footer_button({
                            url: '/com/print_invoice/' + object_id + '/',
                            name: 'Fatura Bas: #' + data['id']
                        });
                    });
                }
            });

            // add_footer_button({
            //     onclick: function () {
            //         $.featherlight({
            //             iframe: '/admin/lab/parametervalue/?q=' + object_id + '#pop_up=1',
            //             iframeWidth: 1100, iframeHeight: 600
            //         });
            //     },
            //     name: 'Sonuç Gir'
            // });

            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/com/print_invoice/' + object_id + '/#noprint',
                        iframeWidth: 1100, iframeHeight: 600,
                        afterClose: function () {
                            window.location.reload()
                        }
                    });
                },
                name: 'Faturayı Görüntüle'
            });


            add_footer_button({
                // url: '/admin/lab/analyse/?admission__id__exact=' + object_id,
                onclick: function () {
                    $.featherlight({
                        iframe: '/admin/lab/analyse/?admission__id__exact=' + object_id + '#pop_up=1',
                        iframeWidth: window.innerWidth * 0.93, iframeHeight: 600,
                    });
                },
                name: 'Testleri Listele',
                target: '_self'
            });
        } else {

            grp.jQuery('.tamamland, .finished, .onayland, .approved').hide()

        }

    }
    if (is_editing('invoice')) {
        debugger;
        if (object_id) {
            add_footer_button({
                url: '/com/print_invoice_by_id/' + object_id + '/',
                name: 'Fatura Yazdır'
            });
        } else {
            // TODO: request and show next invoice ID

        }

    }

    if (is_editing('analysetype')) {
        tiny_tinymce('id_footnote');
    }
    if (is_editing('reporttemplate')) {
        add_footer_button({
            onclick: function () {
                switch_tinymce();
            },
            name: 'Editörü Aç / Kapat'
        });
    }

}

function dashbox(box_id, data, url) {
    var _data = data || {};
    var _url = url || '/lab/get_admissions_by_analyses/';
    var box = $('#' + box_id);
    $.get(_url, _data, function (result) {
        // result = JSON.parse(result);
        for (var itm of result.admissions) {
            box.append($('<li class="grp-row grp-add-link"></li>').html(itm.title + ' | ' + itm.state).click(
                function () {
                    $.featherlight({
                        iframe: '/admin/lab/admission/' + itm.id + '/#pop_up=1',
                        iframeWidth: 1140, iframeHeight: 600
                    });
                }
            ));
        }
    });
}

function handle_dashboard() {

    if ($('body').hasClass('dashboard')) {
        grp.jQuery("div#advanced_settings").click(function () {
            grp.jQuery("div.hide_it").toggleClass('show_it');
        })


        dashbox('new_admissions', {accepted: 'False'});
        dashbox('finished_admissions', {finished: 'True', approved: 'False'});
        dashbox('approved_admissions', {approved: 'True'});

    }
}

function check_all_records() {
    $('input.action-select').attr('checked', true);
}

function get_selected_record_ids() {
    return grp.jQuery('input.action-select:checked').map(function () {
        return this.value;
    }).get().join(',')
}

TIME_DIFF = 10 * 60; // sec
function patch_list_views() {
    try {
        // open the edit view if current listing has only 1 object
        if (_actions_icnt == "1" && location.search.indexOf('q=') > -1) {
            location.pathname = location.pathname + $('.action-select').val() + '/'
        }
    } catch (e) {
        // ignoring popup windows which doesn't have actions
    }


    function change_color() {
        colors = ['#f4f4f4', '#bdcfd0', '#d0bdc6', '#b0d2ae', '#eccfa8'];
        idx = 0;
        while (colors[idx] == window.__color) {
            idx = Math.floor(Math.random() * colors.length);
        }
        window.__color = colors[idx];
    }

    if (is_listing('state')) {
        // paint background of analyse states to different colors according to their timestamp
        // TODO:
        $('input#grp-changelist-search').attr('disabled', true);
        setTimeout('$("input#grp-changelist-search").attr("disabled", false)', 200);
        window.__color = 'gray';
        var last_time = 0;
        $('td.field-tdt').each(function () {
            var td = $(this);
            tmstmp = parseInt(td.text());
            var change_it = (last_time - tmstmp) > TIME_DIFF;
            if (change_it) change_color();
            last_time = tmstmp;
            td.parent().children().css('background', window.__color);

        });
    }
    if (is_listing('analyse')) {
        add_footer_button({
            onclick: function () {
                grp.jQuery('#_ifrm').attr('src',
                    '/lab/multiple_reports/?ids=' + get_selected_record_ids());
            }, name: 'Seçilenler için Rapor Yazdır'
        });

        add_footer_button({
            onclick: function () {
                $.featherlight({
                    iframe: '/lab/multiple_reports/?ids=' + get_selected_record_ids() + '#noprint',
                    iframeWidth: 1100, iframeHeight: 600,
                });
            }, name: 'Seçilenler için Rapor Göster'
        });


    }
    if (is_listing('setting')) {
        printers = jsPrintSetup.getPrintersList().split(',');
        $('td.field-key').each(function () {
            console.log($(this).closest('tr').find('input.vTextField'))
        })

    }
    if (is_listing('parametervalue')) {
        modify_parameter_list_edit('table#result_list tr.grp-row')

    }
    add_footer_button({
        onclick: function () {
            check_all_records();
        }, name: ' ✓ '
    });
    if (window.location.hash.indexOf('hide_header') > -1) {
        $('header').remove();
        $('#grp-content').css('top', '0');
    }
}

function patch_everywhere() {
    // add link to dashboard for admin logo
    grp.jQuery('h1#grp-admin-title').click(function () {
        window.location = '/admin'
    });

    $('input.vDateField').each(function () {
        date_formatter(this);
    })

    // align True/False check marks to center
    grp.jQuery('img[alt="False"],img[alt="True"]').parent().addClass('iconcenter');

    if (window.location.hash.indexOf('pop_up=1') > -1) {
        $('#grp-navigation, #grp-context-navigation, #grp-content-title, div.grp-module:first').hide();
        $('#grp-content').css('top', '20px');
    }

}
function date_formatter(selector) {
    $jqDate = $(selector);
    $jqDate.bind('keyup', 'keydown', function (e) {

        //To accomdate for backspacing, we detect which key was pressed - if backspace, do nothing:
        if (e.which !== 8) {
            var numChars = $jqDate.val().length;
            if (numChars === 2 || numChars === 5) {
                var thisVal = $jqDate.val();
                thisVal += '/';
                $jqDate.val(thisVal);
            }
        }
    });
}

grp.jQuery('document').ready(function () {

    grp.jQuery('#_ifrm').attr('src', '');


    if ($('body.grp-change-list').length) {
        patch_list_views();
    }
    if ($('body.grp-change-form').length) {
        patch_edit_views();
    }
    handle_dashboard();

    patch_everywhere();
});
