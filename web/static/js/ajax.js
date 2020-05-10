$(document).ready(function(){
    
    // Guardar receta
    $('.btn-guardar').click(function(){
      var id = $(this).attr('id');
      var url = $(this).attr('data-catid');
      var btn = $(this);
      
      $.ajax({
        type: "GET",
        url: url,
        data: {receta_id: id},
        success: function( data ){
          var clase = btn.children($('.fa-bookmark')).attr('class');

          if (clase.includes('far')){
            btn.children().removeClass('far').addClass('fas');
          } else {
            btn.children().removeClass('fas').addClass('far');
          }
        },
      })
    });

    // Valorar receta
    $('.btn-valorar').click(function () {
      var id = $(this).attr('data-recetaid');
      var url = $(this).attr('data-url');
      var valoracion = $('input[type=radio]:checked').val();
    
    $.ajax({
      type: 'GET',
      url: url,
      data: { receta_id: id, valoracion: valoracion },
      success: function (data) {
        if (data == "existe") {
          $('#modal-valorar').modal('show');
        } else {
          $('#valoracion_media').html(data);
        }
      }
    })
  });

  $('#modal-submit').click(function () {
    var id = $(this).attr('data-recetaid');
    var url = $(this).attr('data-url');
    var valoracion = $('input[type=radio]:checked').val();

    $.ajax({
      type: 'GET',
      url: url,
      data: { receta_id: id, valoracion: valoracion },
      success: function (data) {
        $('#valoracion_media').html(data);
        $('#modal-valorar').modal('hide');
      }
    })
  });

});