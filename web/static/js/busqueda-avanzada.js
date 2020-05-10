function updatelesmentIndex(forms) {
    console.log(forms);
    forms.each(function (index) {
      var name = "form-" + index + "-ingrediente";
      var id = "id_" + name;
      $(this).find("input").attr({ name: name, id: id });
    });
  }

  function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $("#id_" + prefix + "-TOTAL_FORMS").val();

    newElement.find("input").each(function () {
      var name = $(this)
        .attr("name")
        .replace("-" + (total - 1) + "-", "-" + total + "-");
      var id = "id_" + name;
      $(this).attr({ name: name, id: id }).val("");
    });

    total++;
    $("#id_" + prefix + "-TOTAL_FORMS").val(total);

    newElement.find("input").removeAttr("required");
    $(selector).after(newElement);

    var conditionRow = $(".form-row:not(:last)");

    conditionRow
      .find("button.add-form-row")
      .removeClass("btn-plus")
      .addClass("btn-minus")
      .removeClass("add-form-row")
      .addClass("remove-form-row")
      .html("-");

    newElement.find("input").focus();
    newElement.find("input").attr("required", "true");

    return false;
  }

  function deleteForm(prefix, btn) {
    var total = parseInt($("#id_" + prefix + "-TOTAL_FORMS").val());
    console.log(total);
    if (total > 1) {
      btn.parents(".form-row").remove();

      var forms = $(".form-row");
      $("#id_" + prefix + "-TOTAL_FORMS").val(forms.length);

      updatelesmentIndex(forms);
    }
    return false;
  }

  $(document).on("click", ".add-form-row", function (e) {
    e.preventDefault();
    cloneMore(".form-row:last", "form");
    return false;
  });

  $(document).on("click", ".remove-form-row", function (e) {
    e.preventDefault();
    deleteForm("form", $(this));
    return false;
  });