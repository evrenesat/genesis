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
    let klses = grp.jQuery('body').attr('class').split(' ');
    for (let kls of klses) {
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

function print_barcode_iframe() {
    // this method will be called from iframe
    // ie: window.parent.print_barcode_iframe()

    // set portrait orientation
    jsPrintSetup.setPrinter('ZDesigner GC420t');
    // jsPrintSetup.setOption('orientation', jsPrintSetup.kPortraitOrientation);
    // set top margins in millimeters
    jsPrintSetup.setOption('marginTop', 0);
    jsPrintSetup.setOption('marginBottom', 0);
    jsPrintSetup.setOption('marginLeft', 0);
    jsPrintSetup.setOption('marginRight', 0);
    // set page header
    jsPrintSetup.setOption('headerStrLeft', '');
    jsPrintSetup.setOption('headerStrCenter', '');
    jsPrintSetup.setOption('headerStrRight', '');
    // set empty page footer
    jsPrintSetup.setOption('footerStrLeft', '');
    jsPrintSetup.setOption('footerStrCenter', '');
    jsPrintSetup.setOption('footerStrRight', '');
    // clears user preferences always silent print value
    // to enable using 'printSilent' option
    jsPrintSetup.clearSilentPrint();
    // Suppress print dialog (for this context only)
    jsPrintSetup.setOption('printSilent', 1);
    // Do Print
    // When print is submitted it is executed asynchronous and
    // script flow continues after print independently of completetion of print process!
    jsPrintSetup.printWindow(window.frames[0]);
    // next commands
}

function print_invoice_iframe() {
    // this method will be called from iframe
    // ie: window.parent.print_barcode_iframe()

    // set portrait orientation
    jsPrintSetup.setPrinter('EPSON LX-350 ESC/P');
    // jsPrintSetup.setOption('orientation', jsPrintSetup.kPortraitOrientation);
    // set top margins in millimeters
    jsPrintSetup.setOption('marginTop', 0);
    jsPrintSetup.setOption('marginBottom', 0);
    jsPrintSetup.setOption('marginLeft', 0);
    jsPrintSetup.setOption('marginRight', 0);
    // set page header
    jsPrintSetup.setOption('headerStrLeft', '');
    jsPrintSetup.setOption('headerStrCenter', '');
    jsPrintSetup.setOption('headerStrRight', '');
    // set empty page footer
    jsPrintSetup.setOption('footerStrLeft', '');
    jsPrintSetup.setOption('footerStrCenter', '');
    jsPrintSetup.setOption('footerStrRight', '');
    // clears user preferences always silent print value
    // to enable using 'printSilent' option
    jsPrintSetup.clearSilentPrint();
    // Suppress print dialog (for this context only)
    jsPrintSetup.setOption('printSilent', 1);
    // Do Print
    // When print is submitted it is executed asynchronous and
    // script flow continues after print independently of completetion of print process!
    jsPrintSetup.printWindow(window.frames[0]);
    // next commands
}
function popup_error(msg) {
    alert(msg);
}
function print_report_iframe() {
    // this method will be called from iframe
    // ie: window.parent.print_barcode_iframe()

    // set portrait orientation
    jsPrintSetup.setPrinter('report');
    // jsPrintSetup.setOption('orientation', jsPrintSetup.kPortraitOrientation);
    // jsPrintSetup.setPaperSizeData(9);
    console.log(jsPrintSetup.getPaperMeasure());
    // set top margins in millimeters
    jsPrintSetup.setOption('marginTop', 10);
    jsPrintSetup.setOption('marginBottom', 0);
    // jsPrintSetup.setOption('marginLeft', 0);
    // jsPrintSetup.setOption('marginRight', 0)
    // set page header
    jsPrintSetup.setOption('headerStrLeft', '');
    jsPrintSetup.setOption('headerStrCenter', '');
    jsPrintSetup.setOption('headerStrRight', '');
    // set empty page footer
    jsPrintSetup.setOption('footerStrLeft', '');
    jsPrintSetup.setOption('footerStrCenter', '');
    jsPrintSetup.setOption('footerStrRight', '');
    // clears user preferences always silent print value
    // to enable using 'printSilent' option
    jsPrintSetup.clearSilentPrint();
    // Suppress print dialog (for this context only)
    jsPrintSetup.setOption('printSilent', 1);
    // Do Print
    // When print is submitted it is executed asynchronous and
    // script flow continues after print independently of completetion of print process!
    jsPrintSetup.printWindow(window.frames[0]);
    // next commands
}

function lock_unlock_analyse_states() {
    $('#state_set-group select').each(function () {
        var selbox = $(this);
        let id = selbox.attr('id').replace('definition', '') + 'id';
        if (id.indexOf('_prefix') == -1 && $('#' + id).val()) {
            selbox.attr("disabled", true);
            selbox.after($('<input type=hidden>').val(selbox.val()).attr('name', selbox.attr('name')));
            selbox.closest('.definition').dblclick(function () {
                alert("Çok gerekmedikçe mevcut bir durum kaydını değiştirmek yerine yeni bir kayıt eklemeyi tercih ediniz.");
                selbox.attr("disabled", false);
                selbox.siblings('input').remove();
            })
        }
    });
}
function swap_add_another_status_row() {
    let add_new = $('#state_set-group div.grp-dynamic-form.grp-module.grp-tbody').not('.has_original');
    let th = add_new.siblings('.grp-thead');
    th.after(add_new.detach()[0]);
}

var object_id = get_editing_id();
function patch_edit_views() {

    // change text of _save
    grp.jQuery('input[name="_continue"]').val(grp.jQuery('input[name="_save"]').val());
    // hide empty (looking) <li> elements of hided "_save" and "_addanother" buttons.
    grp.jQuery('body:not(.grp-popup) input[name="_save"], body:not(.grp-popup) input[name="_addanother"]').parent().hide()


    // get rid of those empty cells
    grp.jQuery('div.c-1').map(function () {
        self = grp.jQuery(this);
        if (self.html() == "&nbsp;") self.hide();
    })

    if (is_editing('analyse') && object_id) {
        add_footer_button({url: '/lab/analyse_barcode/' + object_id + '/', name: 'Barkod Yazdır'});
        var is_finished = grp.jQuery('div.finished img[alt=True]').length;
        var group_membership = $('input#id_group_relation').val();

        modify_parameter_list_edit('div#parametervalue_set-group div.form-row.has_original');

        swap_add_another_status_row();
        setTimeout(lock_unlock_analyse_states, 0);

        if (group_membership) {


            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/admin/lab/parametervalue/?q=' + group_membership + '#pop_up=1',
                        iframeWidth: 1000, iframeHeight: 600
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
                        iframeWidth: 900, iframeHeight: 600
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
                        iframeWidth: 900, iframeHeight: 600
                    });
                },
                name: 'Rapor Görüntüle'
            });
        }
    }
    if (is_editing('admission')) {
        setTimeout(function () { // allow grapelli to do it's magic
            grp.jQuery('#id_patient-autocomplete').parent().attr('style', 'max-width:440px !important');
        }, 0);
        if (object_id) {
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

            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/admin/lab/parametervalue/?q=' + object_id + '#pop_up=1',
                        iframeWidth: 1000, iframeHeight: 600
                    });
                },
                name: 'Sonuç Gir'
            });

            add_footer_button({
                onclick: function () {
                    $.featherlight({
                        iframe: '/com/print_invoice/' + object_id + '/#noprint',
                        iframeWidth: 1000, iframeHeight: 600,
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
                        iframeWidth: 1100, iframeHeight: 600
                    });
                },
                name: 'Analizleri Listele',
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


function create_selectbox(optionList, toElem) {
    var combo = $("<select class='comboin'></select>");

    $.each(optionList, function (i, el) {
        combo.append("<option>" + el + "</option>");
    });
    $(combo).change(function () {
        console.log("Change", toElem);
        toElem.val($(this).val());
    })

    return combo;
}

function modify_parameter_list_edit(selector) {
    $(selector).each(function () {

        let tr = $(this);
        window.tr = tr;
        console.log(tr);
        console.log(tr.find('input.keydata').val());
        let keyData = JSON.parse(tr.find('input.keydata').val());
        if (keyData.presets.length) {
            let txt_field = tr.find('input.vTextField');
            txt_field.hide();
            var combo = create_selectbox(keyData.presets, txt_field);
            combo.val(txt_field.val());
            txt_field.after(combo);
            let manual_button = $('<input class="manualb" type="button" value="  ❄  ">');
            manual_button.click(function () {
                if (!keyData.auto_preset && txt_field.css('display') == 'none') {
                    alert("Öntanımlı değerler dışında bir değer girmek üzeresiniz!")
                }
                combo.toggle();
                txt_field.toggle();
            })
            txt_field.after(manual_button);
        }
    })
}


function handle_dashboard() {


    grp.jQuery("div#advanced_settings").click(function () {
        grp.jQuery("div.hide_it").toggleClass('show_it');
    })


}

function get_selected_record_ids() {
    return grp.jQuery('input.action-select:checked').map(function () {
        return this.value;
    }).get().join(',')
}


function patch_list_views() {

    if (_actions_icnt == "1" && location.search.indexOf('q=') > -1) {
        location.pathname = location.pathname + $('.action-select').val() + '/'
    }

    if (is_listing('analyse')) {
        add_footer_button({
            onclick: function () {
                grp.jQuery('#_ifrm').attr('src',
                    '/lab/multiple_reports/?ids=' + get_selected_record_ids());
            }, name: 'Seçili Analizler İçin Rapor Yazdır'
        });

        add_footer_button({
            onclick: function () {
                $.featherlight({
                    iframe: '/lab/multiple_reports/?ids=' + get_selected_record_ids() + '#noprint',
                    iframeWidth: 1000, iframeHeight: 600,
                });
            }, name: 'Seçili Analizler İçin Rapor Göster'
        });


    }
    if (is_listing('parametervalue')) {
        modify_parameter_list_edit('table#result_list tr.grp-row')

    }
}

function patch_everywhere() {
    // add link to dashboard for admin logo
    grp.jQuery('h1#grp-admin-title').click(function () {
        window.location = '/admin'
    });

    // align True/False check marks to center
    grp.jQuery('img[alt="False"],img[alt="True"]').parent().attr('style', 'text-align:center;');

    if (window.location.hash.indexOf('pop_up=1') > -1) {
        $('#grp-navigation, #grp-context-navigation, #grp-content-title, div.grp-module:first').hide();
        $('#grp-content').css('top', '20px');
    }

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
