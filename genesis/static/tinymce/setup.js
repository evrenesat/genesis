/**
 * Created by evren on 07/10/16.
 */
function init_tinymce() {
    tinymce.init({
        selector: 'textarea',
        height: 700,
        width: 700,
        plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table contextmenu paste code'
        ],
        toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        content_css: '//www.tinymce.com/css/codepen.min.css'
    });

}

function switch_tinymce() {
    if (window.tinymce_on) {
        tinyMCE.remove();
        window.tinymce_on = false;
    } else {
        init_tinymce();
        window.tinymce_on = true;
    }

}


