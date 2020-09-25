$(document).ready(function(){
    
    
    var campos = $('#beauty-form .form-input input, #beauty-form .form-input textarea');
    //console.log(campos)
    var placeholders = {}
    
    campos.each(function(){
        if ($(this).val() != ""){   // Si el campo tiene texto escrito, al siguiente elemento (label) le añade la clase indicada
            $(this).next().addClass('with-text');
        } else {
            $(this).next().removeClass('with-text');
        }

        if ($(this).attr('placeholder') != null ){ // Añade los placeholder a un diccionario de datos
            placeholders[$(this).attr('id')] = $(this).attr('placeholder')
            $(this).attr('placeholder', '');
        }
    });


    
    /**
     * Detecta la pérdida del foco de un campo input o textarea
     * Comprueba si tiene texto escrito o no para añadir la clase indicada o no
     */
    campos.blur(function(){
        if ($(this).val() != ""){
            $(this).next().addClass('with-text');
        } else {
            $(this).next().removeClass('with-text');
            $(this).attr('placeholder', '');
        }
    });

    campos.focus(function (){
        $(this).attr('placeholder', placeholders[$(this).attr('id')]);
    });

    /**
     * Cuando se pulsa una tecla en un campo de texto password
     * Comprueba que los 2 campos de contraseña coincidad, tenga como mínimo 8 caracteres y no sea solo número
     */
    $('input[type=password]').keyup(function(){
        var pass1 = $('#password');
        var pass2 = $('#password2')
        
        if (pass1.val() == pass2.val() && pass1.val().length >= 8 && isNaN(pass1.val())){
            pass2.css('border-bottom', '3px solid green');
            //btn.prop('disabled', false);
        } else {
            pass2.css('border-bottom', '3px solid red');
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
        if (typeof e.target.result == "undefined"){
            img.attr('src', '#');
        } else {
            img.attr('src', e.target.result);
        }
        
      }
  
      reader.readAsDataURL(input.files[0])
    }

    
  }