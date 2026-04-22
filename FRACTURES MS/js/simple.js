/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

function resetForm(formId, withSubmit) {
    $(formId).find('input').each(function () {
        switch (this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                if ($(this).is(':visible')) {
                    $(this).val('');
                }
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;

        }
    });

    $(formId).find('select').each(function () {
        if ($(this).is(':visible')) {
            $(this).val('');
        }
    });

    //Tagit
    $(formId).find('ul.tagit').each(function() {
        $(formId).find('li.tagit-choice').each(function() {
            $(this).remove();
        })
        // Clean hidden select : remove all option
        $(this).next('select').find('option').remove('option');
    })

    $("div.advanced_search").find("div.filter").each(function() {
        if ($(this).is(":visible")) {
            $($(this).prev("div.filter-label").click());
        }
    })

    if (withSubmit == true) $(formId).submit();
}

/**
 * Slide toggle on a bow for
 */
function toggleBoxSearch(divId) {
    $('#'+divId).slideToggle("slow");
    $('#'+divId).prev('div').children('div').toggle('slow');
}

/**
*effect popup debut
*/

		function hideDiv(div) {
    if (document.getElementById) { // DOM3 = IE5, NS6
        document.getElementById(div).style.visibility = 'hidden';
    } else {
        if (document.layers) { // Netscape 4
            document.hideshow.visibility = 'hidden';
        } else { // IE 4
            document.all.hideshow.style.visibility = 'hidden';
        }
    }
}
 
function showDiv(div) {
    if (document.getElementById) { // DOM3 = IE5, NS6
        document.getElementById(div).style.visibility = 'visible';
    } else {
        if (document.layers) { // Netscape 4
            document.hideshow.visibility = 'visible';
        } else { // IE 4
            document.all.hideshow.style.visibility = 'visible';
        }
    }
}


		
/**
*effect popup fin
*/
/**
 * Smooth scrool top
 */
$(document).ready(function() {
    
    $("#email").keypress(function(event) {
        if ( event.which == 13 ) {
            $('input[type="submit"]').click();
        }
    });
    $("#password").keypress(function(event) {
        if ( event.which == 13 ) {
            $('input[type="submit"]').click();
        }
    });

    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('.scrollup').fadeIn();
        } else {
            $('.scrollup').fadeOut();
        }
    });

    $('.scrollup').click(function(){
        $("html, body").animate({
            scrollTop: 0
        }, 600);
        return false;
    });
});