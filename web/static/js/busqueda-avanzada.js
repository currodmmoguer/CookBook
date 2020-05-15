/**
 * Actualiza los atributos id y name de todos los div form-row
 */
function updatelesmentIndex() {
  $("div.form-row").each(function (index) {
    var name = "form-" + index + "-ingrediente";
    var id = "id_" + name;
    $(this).find("input").attr({ name: name, id: id });
  });
}

/**
 * Crea un nuevo campo de texto vacío y lo añade al último de la lista
 * @param {Objeto} selector Campo de texto
 * @param {Texto} prefix Prefijo
 */
function cloneMore(selector, prefix) {
  var newElement = $(selector).clone(true);
  var total = $("#id_" + prefix + "-TOTAL_FORMS").val();

  // Añade los atributos id y name y vacía el campo de texto
  var name = newElement.find("input").attr("name").replace("-" + (total - 1) + "-", "-" + total + "-");
  var id = "id_" + name;
  newElement.find("input").attr({ name: name, id: id }).val("");

  total++;
  $("#id_" + prefix + "-TOTAL_FORMS").val(total);

  //Se quita para que no salga el cuadrado rojo del validator
  newElement.find("input").removeAttr("required");

  // Añade el campo de texto detrás del último
  $(selector).after(newElement);

  var row = $(".form-row:not(:last)");

  // Cambia el botón del campo de texto
  row.find("button.add-form-row")
    .removeClass("add-form-row")
    .addClass("remove-form-row")
    .attr('title', 'Quitar ingrediente')
    .html("-");

  newElement.find("input").focus();
  newElement.find("input").attr("required", "true");

}

/**
 * Elimina el campo de texto selecionado.
 *
 * @param {texto} prefix Prefijo
 * @param {objeto} btn Botón eliminar
 */
function deleteForm(prefix, btn) {
  var total = parseInt($("#id_" + prefix + "-TOTAL_FORMS").val());

  if (total > 1) {
    btn.parents(".form-row").remove();
    $("#id_" + prefix + "-TOTAL_FORMS").val($(".form-row").length);
    updatelesmentIndex(); // Actualiza los campos de texto
  }
}

/**
 * Escuchador cuando se hace clic en un botón +
 */
$(document).on("click", ".add-form-row", function (e) {
  e.preventDefault();
  cloneMore(".form-row:last", "form");
});

/**
 * Escuchador cuando se hace clic en un botón -
 */
$(document).on("click", ".remove-form-row", function (e) {
  e.preventDefault();
  deleteForm("form", $(this));
});
