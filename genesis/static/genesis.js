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
    return grp.jQuery('body').hasClass('lab-' + name);
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
function popup_error(msg){
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
var object_id = get_editing_id();

function patch_edit_views() {
    // get rid of those empty cells
    grp.jQuery('div.c-1').map(function () {
        self = grp.jQuery(this);
        if (self.html() == "&nbsp;")self.hide();
    })

    if (is_editing('analyse') && object_id) {
        add_footer_button({url: '/lab/analyse_barcode/' + object_id + '/', name: 'Barkod Yazdır'});
        var is_finished = grp.jQuery('div.finished img[alt=True]').length;
        if (is_finished) {
            add_footer_button({url: '/lab/analyse_report/' + object_id + '/', name: 'Rapor Yazdır'});
        }
    }
    if (is_editing('admission')) {
        setTimeout(function() { // allow grapelli to do it's magic
            grp.jQuery('#id_patient-autocomplete').parent().attr('style', 'max-width:440px !important');
        }, 0);
        if (object_id) {
            add_footer_button({url: '/lab/admission_barcode/' + object_id + '/', name: 'Barkod Yazdır'});
            add_footer_button({url: '/com/print_invoice/' + object_id + '/', name: 'Fatura Bas'});
            add_footer_button({
                url: '/admin/lab/analyse/?group_relation__in=10,30&admission__id__exact=' + object_id,
                name: 'Analizleri Listele',
                target: '_self'
            });
        } else {

            grp.jQuery('.tamamland, .finished, .onayland, .approved').hide()

        }

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


function handle_dashboard() {


    grp.jQuery("div#advanced_settings").click(function () {
        grp.jQuery("div.hide_it").toggleClass('show_it');
    })


}

function print_multi_report() {
    analyzes = grp.jQuery('input.action-select:checked').map(function () {
        return this.value;
    }).get().join(',')
    grp.jQuery('#_ifrm').attr('src', '/lab/multiple_reports/?ids=' + analyzes)
}

function patch_list_views() {
    if (is_listing('analyse')) {
        add_footer_button({
            onclick: function () {
                print_multi_report()
            }, name: 'Seçili Analizler İçin Rapor Yazdır'
        });


    }
}

function patch_everywhere() {
    // add link to dashboard for admin logo
    grp.jQuery('h1#grp-admin-title').click(function () {
        window.location = '/admin'
    });

    // align True/False check marks to center
    grp.jQuery('img[alt="False"],img[alt="True"]').parent().attr('style', 'text-align:center;');

    // change text of _save
    grp.jQuery('input[name="_continue"]').val(grp.jQuery('input[name="_save"]').val());
    // hide empty (looking) <li> elements of hided "_save" and "_addanother" buttons.
    grp.jQuery('input[name="_save"], input[name="_addanother"]').parent().hide()
}
grp.jQuery('document').ready(function () {
    grp.jQuery('#_ifrm').attr('src', '');
    patch_list_views();
    patch_edit_views();
    handle_dashboard();

    patch_everywhere();
});
