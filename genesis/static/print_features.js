
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
    $('#_ifrm').attr('src','about:blank');
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
    $('#_ifrm').attr('src','about:blank');
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
    $('#_ifrm').attr('src','about:blank');
    // next commands
}
