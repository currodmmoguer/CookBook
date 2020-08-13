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
});

$("#modal-submit").click(function () {
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
$("#btn-notification").click(function () {
  var url = $(this).attr("data-url");
  var badge = $(this).find(".badge");

  $.ajax({
    type: "GET",
    url: url,
    success: function () {
      badge.attr("hidden", "");
    },
  });
});
