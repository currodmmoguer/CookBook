$(document).ready(function(){
  updateElementIndexPaso();
  updateElementIndexIngrediente();
});

// SCRIPT PASOS 



  function updateElementIndexPaso() {
    var pasos = $('#totalPasos');
    pasos = pasos.children('.paso');
    var pos = 0;
    
    pasos.each(function(index){
      
      $(this).find('.numPaso').html(pos+1);
      $(this).find('textarea').attr('id', 'id_paso-' + pos + '-texto').attr('name', 'paso-' + pos + '-texto');
      $(this).find('label.form-label').attr('for', 'id_paso-' + pos + '-texto');
      $(this).find('input[type=file]').attr('id', 'id_paso-' + pos + '-imagen_paso').attr('name', 'paso-' + pos + '-imagen_paso');
      $(this).find('label.subir-foto').attr('for', 'id_paso-' + pos + '-imagen_paso');
      $(this).attr('id', 'paso' + pos);
      pos++;
    });

  }
  function cloneMorePaso(selector, prefix) {
      var newElement = $(selector).clone(true);
      
      newElement.find('textarea, input[type=file]').each(function(){
        $(this).val('');
      });
      newElement.find('img').attr('src', '');

      var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
      total++;
      $('#id_' + prefix + '-TOTAL_FORMS').val(total);
      $(selector).after(newElement);
      updateElementIndexPaso();
      return false;
    }
  function deleteFormPaso(prefix, btn) {
      var total = $('#totalPasos').children('div.paso').length;
      if (total > 1){
          btn.parents('.paso').remove();
          var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
          total--;
          $('#id_' + prefix + '-TOTAL_FORMS').val(total);
          updateElementIndexPaso();
      }
      return false;
    }

 
  $(document).on('click', '#buttonAddPaso', function(e){
      e.preventDefault();
      cloneMorePaso('#paso0', 'paso');
      return false;
    });

  $(document).on('click', '.remove-form-row-paso', function(e){
      e.preventDefault();
      deleteFormPaso('paso', $(this));
      return false;
    });


// SCRIPT INGREDIENTES

  function updateElementIndexIngrediente(/*el, prefix, ndx*/) {
    var ingredientes = $('#totalIngredientes');
    ingredientes = ingredientes.children('.ingrediente');
    var pos = 0;

    ingredientes.each(function(index) {
      console.log("ingrediente " + pos)
      $(this).attr('id', 'ingrediente' + pos);

      $(this).find('input, select').each(function(i){ //Recoge todos
        
        if ($(this).attr('id').endsWith('ingrediente')){  //Campo nombre ingrediente
          $(this).attr('id', 'id_ingrediente-' + pos + '-ingrediente').attr('name', 'ingrediente-' + pos + '-ingrediente');
          $(this).next().attr('for', 'id_ingrediente-' + pos + '-ingrediente');

        } else if ($(this).attr('id').endsWith('cantidad')){  //Campo cantidad
          $(this).attr('id', 'id_ingrediente-' + pos + '-cantidad').attr('name', 'ingrediente-' + pos + '-cantidad');
          $(this).next().attr('for', 'id_ingrediente-' + pos + '-cantidad');
        } else if ($(this).attr('id').endsWith('unidad_medida')){ //Campo unidad de medida
          $(this).attr('id', 'id_ingrediente-' + pos + '-unidad_medida').attr('name', 'ingrediente-' + pos + '-unidad_medida');
          $(this).next().attr('for', 'id_ingrediente-' + pos + '-unidad_medida');
        }
        console.log($(this));
      });
      pos++;
    });
  }

  function cloneMoreIngrediente(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    console.log("nuevo")
    console.log(newElement)
    newElement.find('input, select').each(function() {
      $(this).val('');
    });
    

    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
    updateElementIndexIngrediente();
    return false;
  }
  function deleteForm(prefix, btn) {
    
  var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
  
  if (total > 1){
    console.log(btn);
    btn.parents('.ingrediente').remove();
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    total--;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
  }
  return false;
  }
  $(document).on('click', '#buttonAddIngredient', function(e){
    e.preventDefault();
    cloneMoreIngrediente('#ingrediente0', 'ingrediente');
    return false;
  });

  $(document).on('click', '.remove-form-row-ingrediente', function(e){
    e.preventDefault();
    deleteForm('ingrediente', $(this));
    return false;
  });

  function readURL(input) {
    if (input.files && input.files[0]){
      var reader = new FileReader();

      reader.onload = function(e){
        $('#blah').attr('src', e.target.result);
      }

      reader.readAsDataURL(input.files[0])
    }
  }

  $(document).on('change', '.paso input[type=file]', function(e){
    readURL(this);
  });

  
