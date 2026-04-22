// Librairie d'affichage d'infobulles


// on charge la feuille de style de la bulle.
document.write('<style type="text/css">@import url(/css/infobulle.css);</style>');
// on formate la bulle.
document.write('<div id="bulle" class="infos_bulle"></div>');
// on met � jour la position de la bulle.
document.onmousemove = move_bulle;

var bulle_visible=false; // La variable i nous dit si la bulle est visible ou non

function move_bulle(e) // Fonction de suivi de la souris
{
  if(bulle_visible){
    if(navigator.appName!="Microsoft Internet Explorer"){
      $("#bulle").get(0).style.left = 5+e.pageX+"px";
      $("#bulle").get(0).style.top = 15+e.pageY+"px";
    }else{
//        window.lastX=event.clientX;
//        window.lastY=event.clientY;
        $("#bulle").get(0).style.left = 5+event.clientX+document.documentElement.scrollLeft+"px";
        $("#bulle").get(0).style.top = 15+event.clientY+document.documentElement.scrollTop+"px";
    }

  }
}

function open_bulle(content)
{
  if(bulle_visible==false){
    $("#bulle").get(0).style.visibility = "visible"; // Si la bulle est cacher on la rend visible.
    $("#bulle").get(0).innerHTML = content; // on copie le contenu dans la bulle
	move_bulle($("#bulle").get(0)); // positionnement initial (correctif X.Dusart)
    bulle_visible=true;
  }
}

function close_bulle()
{
  if(bulle_visible==true){
    $("#bulle").get(0).style.visibility = "hidden"; // Si la bulle est visible on la cache
    bulle_visible=false;
  }
}
