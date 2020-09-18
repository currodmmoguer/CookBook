// Cuando se abre la pantalla, actualiza los pasos e ingredientes
$(document).ready(function () {
  updateElementIndexPaso();
  updateElementIndexIngrediente();
});

// SCRIPT PASOS 



/**
 * Actualiza todas las filas de pasos
 */
function updateElementIndexPaso() {
  var pasos = $('#totalPasos').children('.paso');
  
  pasos.each(function (pos) {
    var name = 'paso-' + pos + '-';
    $(this).find('.numPaso').html(pos + 1);
    $(this).find('textarea').attr('id', 'id_' + name + 'texto').attr('name', name + 'texto');
    $(this).find('label.form-label').attr('for', 'id_' + name + 'texto');
    $(this).find('input[type=file]').attr('id', 'id_' + name + 'imagen_paso').attr('name', name + 'imagen_paso');
    $(this).find('label.subir-foto').attr('for', 'id_' + name + 'imagen_paso');
    $(this).find('img').attr('id', 'vista_previa_imagen_paso_' + pos);
    $(this).attr('id', 'paso' + pos);
    
    if (pos % 2 == 0){

      $(this).css('background-color', '#fff');
    } else {
      $(this).css('background-color', '#f0f0f0');
    }

    
  });

}

/**
 * Crea una nueva fila paso y lo añade al final de la lista
 * @param {Objeto} selector Fila formset
 * @param {Texto} prefix Prefijo
 */
function cloneMorePaso(selector, prefix) {
  var newElement = $(selector).clone(true);
  var total = $('#id_' + prefix + '-TOTAL_FORMS').val();

  // Vacía los campos textarea y el input file
  newElement.find('textarea, input[type=file]').each(function () {
    $(this).val('');
  });

  // Vacía la imagen de vista previa
  newElement.find('img').attr('src', '#');

  total++;
  $('#id_' + prefix + '-TOTAL_FORMS').val(total);

  newElement.find('textarea').removeAttr("required");

  // Añade la nueva fila detrás del último
  $(selector).after(newElement);
  newElement.find("textarea").focus();
  newElement.find('textarea').attr("required", "");
  

  updateElementIndexPaso();
  console.log(newElement);
  return newElement;
}

/**
 * Elimina el campo de texto selecionado.
 *
 * @param {texto} prefix Prefijo
 * @param {objeto} btn Botón eliminar
 */
function deleteFormPaso(prefix, btn) {
  var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());

  if (total > 1) {
    btn.parents('.paso').remove();
    $('#id_' + prefix + '-TOTAL_FORMS').val($('.paso').length);
    updateElementIndexPaso();
  }

}

/**
$(document).on('click', '#buttonAddPaso', function (e) {
  alert("Aqui si");
  //e.preventDefault();
  cloneMorePaso('.paso:last', 'paso');
  
});


$(document).on('click', '.remove-form-row-paso', function (e) {
  e.preventDefault();
  deleteFormPaso('paso', $(this));
});
*/


// SCRIPT INGREDIENTES

function updateElementIndexIngrediente() {
  var ingredientes = $('#totalIngredientes').children('.ingrediente');
  
  ingredientes.each(function(pos) {

    // Añade el id al div.row
    $(this).attr('id', 'ingrediente' + pos);
    
    // Loop para todos los campos input y select dentro del div
    $(this).find('input, select').each(function () { 
      // Según el campo que sea, modifica sus atributos
      var name = 'ingrediente-' + pos + '-';

      if ($(this).attr('id').endsWith('ingrediente')) {  //Campo nombre ingrediente
        $(this).attr('id', 'id_' + name + 'ingrediente').attr('name', name + 'ingrediente');
        $(this).next().attr('for', 'id_' + name + 'ingrediente');

      } else if ($(this).attr('id').endsWith('cantidad')) {  //Campo cantidad
        $(this).attr('id', 'id_' + name + 'cantidad').attr('name', name + 'cantidad');
        $(this).next().attr('for', 'id_' + name + 'cantidad');
      
      } else if ($(this).attr('id').endsWith('unidad_medida')) { //Campo unidad de medida
        $(this).attr('id', 'id_' + name + 'unidad_medida').attr('name', name + 'unidad_medida');
      }

    });

    if (pos % 2 == 0){
      $(this).css('background-color', '#fff');
    } else {
      $(this).css('background-color', '#f0f0f0');
    }
  });
}

/**
 * Crea un nuevo campo de texto vacío y lo añade al último de la lista
 * @param {Objeto} selector Campo de texto
 * @param {Texto} prefix Prefijo
 */
function cloneMoreIngrediente(selector, prefix) {
  var newElement = $(selector).clone(true);
  var total = $('#id_' + prefix + '-TOTAL_FORMS').val();

  // Vacía los campos del formulario
  newElement.find('input, select').each(function () {
    $(this).val('');
    $(this).removeAttr("required");
    
  });


  total++;
  $('#id_' + prefix + '-TOTAL_FORMS').val(total);
  
  // Añade la nueva fila al final
  $(selector).after(newElement);
  newElement.find("input[id$='ingrediente']").focus();
  newElement.find("input, select").attr("required", "true");
  updateElementIndexIngrediente();
  
}

/**
 * Elimina el campo de texto selecionado.
 * (Igual q avanzado excepto paretns)
 * @param {texto} prefix Prefijo
 * @param {objeto} btn Botón eliminar
 */
function deleteForm(prefix, btn) {

  var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());


  if (total > 1) {
    btn.parents('.ingrediente').remove();
    console.log($('.ingrediente').length);
    $('#id_' + prefix + '-TOTAL_FORMS').val($('.ingrediente').length);
    updateElementIndexIngrediente();
  }
}

$(document).on('click', '#buttonAddIngredient', function (e) {
  e.preventDefault();
  cloneMoreIngrediente('.ingrediente:last', 'ingrediente');
});

$(document).on('click', '.remove-form-row-ingrediente', function (e) {
  e.preventDefault();
  deleteForm('ingrediente', $(this));
});






