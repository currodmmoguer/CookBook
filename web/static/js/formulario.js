$(document).ready(function () {
  var campos = $(
    ".beauty-form .form-input input, .beauty-form .form-input textarea"
  );
  //console.log(campos)
  var placeholders = {};

  campos.each(function () {
    if ($(this).val() != "") {
      // Si el campo tiene texto escrito, al siguiente elemento (label) le añade la clase indicada
      $(this).next().addClass("with-text");
    } else {
      $(this).next().removeClass("with-text");
    }

    if ($(this).attr("placeholder") != null) {
      // Añade los placeholder a un diccionario de datos
      placeholders[$(this).attr("id")] = $(this).attr("placeholder");
      $(this).attr("placeholder", "");
    }
  });

  /**
   * Detecta la pérdida del foco de un campo input o textarea
   * Comprueba si tiene texto escrito o no para añadir la clase indicada o no
   */
  campos.blur(function () {
    if ($(this).val() != "") {
      $(this).next().addClass("with-text");
    } else {
      $(this).next().removeClass("with-text");
      $(this).attr("placeholder", "");
    }
  });

  campos.focus(function () {
    $(this).attr("placeholder", placeholders[$(this).attr("id")]);
  });

  /**
   * Cuando se pulsa una tecla en un campo de texto password
   * Comprueba que los 2 campos de contraseña coincidad, tenga como mínimo 8 caracteres y no sea solo número
   */
  $("input[type=password]").keyup(function () {
    var pass1 = $("#id_password");
    var pass2 = $("#id_password2");

    if (
      pass1.val() == pass2.val() &&
      pass1.val().length >= 8 &&
      isNaN(pass1.val())
    ) {
      pass2.css("border-bottom", "3px solid green");
      //btn.prop('disabled', false);
    } else {
      pass2.css("border-bottom", "3px solid red");
      //btn.prop('disabled', true);
    }
  });
});

/**
 * Muestra una vista previa de una imagen subida en un formulario
 * @param {Objeto} input Campo de subir archivo
 * @param {Objeto} img Campo que hace referencia al elemento img de vista previa
 */
function readURL(input, img) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function (e) {
      if (typeof e.target.result == "undefined") {
        img.attr("src", "#");
      } else {
        img.attr("src", e.target.result);
      }
    };

    reader.readAsDataURL(input.files[0]);
  }
}

function recortarImage(img) {
  var image = document.getElementById("image-crop-modal");
  var cropBoxData;
  var canvasData;
  var datosTotal;
  

  

  $("#modal-crop").on("shown.bs.modal", function () {
    var image = document.getElementById("image-crop-modal");
    var cropper = new Cropper(image, {
      aspectRatio: 1 / 1,
      zoomable: false,
      autoCropArea: 1,
      ready: function () {
        console.log("Al abrir modal:")
        console.log(cropBoxData);
        cropper.setCropBoxData(cropBoxData).setCanvasData(canvasData);
        console.log(cropBoxData);
      },
    });
    

    $("#aceptar-recorte").click(function () {
      console.log(cropper);
      cropBoxData = cropper.getCropBoxData();
      canvasData = cropper.getCanvasData();
      datosTotal = cropper.getData();
      var canvas = document.getElementById("canvas");
      console.log(canvas);
      var contex = canvas.getContext("2d");
      contex.imageSmoothingEnabled = true;
      console.log("Aceptando:")
      //console.log(cropBoxData);
      //$('#img-perfil').attr('src', cropper.image.src);
      canvas.width = datosTotal.width;
      canvas.height = datosTotal.height;
      console.log(datosTotal);
      contex.drawImage(
        image,
        datosTotal.x,
        datosTotal.y,
        datosTotal.width,
        datosTotal.height,
        0,
        0,
        datosTotal.width,
        datosTotal.height
      );

      $("#val_img").val(
        datosTotal.x +
          ";" +
          datosTotal.y +
          ";" +
          datosTotal.width +
          ";" +
          datosTotal.height
      );
      $("#img-perfil").attr("hidden", "");
      $("#canvas").removeAttr("hidden");
      $('#image-crop-modal').removeAttr('src');
      //console.log(cropper);
      //cropper.destroy();
      //console.log(image);
      //console.log(cropper);

    });

    $('#close-modal-crop').click(function(){
      cropper.destroy();
      $('#image-crop-modal').removeAttr('src');
      //console.log(cropper);
    });
  });
}
