// Colorea las estrellas según la valoración media
function colorearEstrellas(cantidad){
    $($('.starrating label').get().reverse()).each(function (e) {
      if (e < cantidad) {
        $(this).css("color", "#F9A31A ");
      }
    });
}

// COMENTARIOS
$('.form-respuesta').hide();

$('.btn-responder').click(function () {
    let elemento = $(this).parent().children('div.form-respuesta');
    elemento.slideToggle('slow');
});

// Mostrar imagen de los pasos en grande
$('#pasos img').click(function () {
    console.log("eee");
    if ($(window).width() >= 992) {
      var src = $(this).attr('src');
      $('#img-preview').attr('src', src);
      $('#modal-img-preview').modal('show');
    }

});