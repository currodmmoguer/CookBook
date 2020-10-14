// Seguir/Dejar de seguir
$(".seguir").click(function(){
  var idUser = $(this).attr("data-user");
  var url = $(this).attr("data-url");
  var button = this;
  $.ajax({
    type: "GET",
    url: url,
    data: {user_id: idUser},
    success: function(data) {
      // Cambia el texto del botón
      // Cambiar el número de seguidores
      if (data == "siguiendo"){
        $(button).html("Dejar de seguir");
      } else if (data == "dejado"){
        $(button).html("Seguir");
      }
    },
  });
});

// Guardar receta
$(".btn-guardar").click(function () {
  var id = $(this).attr("id");
  var url = $(this).attr("data-url");
  var btn = $(this);

  $.ajax({
    type: "GET",
    url: url,
    data: { receta_id: id },
    success: function (data) {
      var clase = btn.children($(".fa-bookmark")).attr("class");
      
      // Cambia la clase el icono de guardar para que esté marcado o desmarcado
      if (clase.includes("far")) {
        btn.children().removeClass("far").addClass("fas");
      } else {
        btn.children().removeClass("fas").addClass("far");
      }
    },
  });
});

// Valorar receta
$(".btn-valorar").click(function () {
  var id = $(this).attr("data-recetaid");
  var url = $(this).attr("data-url");
  var valoracion = $("input[type=radio]:checked").val();
  if (valoracion != undefined) {
    $.ajax({
      type: "GET",
      url: url,
      data: { receta_id: id, valoracion: valoracion },
      success: function (data) {
        // Si ya ha valorado antes la receta, abre un modal para modificarla
        if (data == "existe") {
          $("#modal-valorar").modal("show");
        } else {
          $("#valoracion_media").html(data);
        }
      },
    });
  } else {
    alert("Tienes que valorar");
  }
  
});

$("#modal-submit-valorar").click(function () {
  var id = $(this).attr("data-recetaid");
  var url = $(this).attr("data-url");
  var valoracion = $("input[type=radio]:checked").val();

  $.ajax({
    type: "GET",
    url: url,
    data: { receta_id: id, valoracion: valoracion },
    success: function (data) {
      $("#valoracion_media").html(data);
      $("#modal-valorar").modal("hide");
    },
  });
});

// Enviar sugerencia
$("#submit-sugerencia").click(function () {
  var url = $(this).attr("data-url");
  var categoria = $("#sugerenciaModal").find("#id_tipo").val();
  var sugerencia = $("#sugerenciaModal").find("#id_sugerencia").val();

  $.ajax({
    type: "GET",
    url: url,
    data: {
      categoria: categoria,
      sugerencia: sugerencia,
    },
    success: function (data) {
      $("#sugerenciaModal").modal("toggle");
      $("#sugerenciaModal").find("#id_sugerencia").val("");
    },
  });
});

// Notificaciones
$(document).ready(function(){
  $.ajax({
    type: "GET",
    url: "/hay_notificaciones/",
    success: function(e){
      if (e === "si-notificacion") {
        $('#badge-not').removeAttr("hidden");
      } 
    },
  });

});
