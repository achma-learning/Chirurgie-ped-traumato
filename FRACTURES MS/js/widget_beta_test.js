/*Panneau coulissant du widget beta test*/
$(function()
{
         $('.widget-beta-test').tabSlideOut({
             tabHandle: '.handle',                              //class of the element that will be your tab
             pathToTabImage: '/img/feedbacktab.png',          //path to the image for the tab (optionaly can be set using css)
             imageHeight: '122px',                               //height of tab image
             imageWidth: '40px',                               //width of tab image
             tabLocation: 'left',                               //side of screen where tab lives, top, right, bottom, or left
             speed: 600,                                        //speed of animation
             action: 'click',                                   //options: 'click' or 'hover', action to trigger animation
             topPos: '150px',                                   //position from the top
             fixedPosition: true                               //options: true makes it stick(fixed position) on scroll
         });
});


function posterCommentaireWidgetBetaTestAjax(url)
{
    var browser = navigator.appName;
    var message = $("#feedback").val();
    var visiteur = $("#visiteur").val();
    visiteur = escape(visiteur);
    message = escape(message);
    $.ajax
    ({
        type : "POST",
        url : "/informations/ajax-envoi-widget-beta-test",
        data : "visiteur="+visiteur+"&message="+message+"&browser="+browser+"&position="+url,
        send : $('#chargement').html("<img src='img/load.gif' alt='chargement' />"),

                success : function(data)
                {
                    $("#feedback").val("");
                    $("#visiteur").val("");
                    $('#retour_widget').html(data);
                    setTimeout ("close()", 2500);
                },
                error :function(msg)
                {
                    alert( "Erreur  : " + msg );
                }
            });
}



function close()
{
     $(".handle").click();
}