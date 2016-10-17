/**
 * Created by evren on 12/10/16.
 */

function add_footer_button(url, name, target) {
    target = target || '_ifrm';
    grp.jQuery('footer ul').append('<li><a class="grp-button" href="' + url + '" target="' + target + '">' + name + '</a></li>');
}

function is_editing(name) {
    return grp.jQuery('body').hasClass('lab-' + name);
}
function is_listing(name) {
    return Boolean(grp.jQuery('a[href$="/admin/lab/' + name + '/add/"]').length)
}

function get_editing_id() {
    return parseInt(document.documentURI.split('/change/')[0].split('/').pop())
}

function print_iframe() {
    // this method will be called from iframe
    // ie: window.parent.print_iframe()

    // set portrait orientation
    jsPrintSetup.setOption('orientation', jsPrintSetup.kPortraitOrientation);
    // set top margins in millimeters
    jsPrintSetup.setOption('marginTop', -4);
    jsPrintSetup.setOption('marginBottom', -4);
    jsPrintSetup.setOption('marginLeft', -4);
    jsPrintSetup.setOption('marginRight', -4);
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

function handle_analyse_edit() {

    if (is_editing('analyse') && object_id) {
        add_footer_button('/lab/analyse_barcode/' + object_id, 'Barkod Yazdır');
        var is_finished = grp.jQuery('#id_finished')[0].checked;
        if(is_finished){
            add_footer_button('/lab/analyse_report/' + object_id, 'Rapor Yazdır');
        }
    }

}

function handle_admission_edit() {

    if (is_editing('admission') && object_id) {
        add_footer_button('/admin/lab/analyse/?admission__id__exact=' + object_id, 'Analizleri Listele', '_self');
    }

}
function handle_dashboard() {


    grp.jQuery("div#advanced_settings").click(function () {
        grp.jQuery("div[id='app_kimlik doğrulama ve yetkilendirme'], div[id='app_lab']").toggle();
    })


}

grp.jQuery('document').ready(function () {

    handle_analyse_edit();
    handle_admission_edit();
    handle_dashboard();
    grp.jQuery('h1#grp-admin-title').click(function () {
        window.location = '/admin'
    })
});
