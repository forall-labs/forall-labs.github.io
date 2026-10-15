// Sends every form on the site through FormSubmit's AJAX endpoint and swaps
// the form for its confirmation panel, so nobody leaves the page. Without
// JavaScript the form still posts normally and FormSubmit redirects to
// /thanks/ (the _next field).
(function () {
  var forms = document.querySelectorAll("form[data-form]");
  if (!forms.length) return;

  // /contact/?topic=support preselects the matching option.
  var topic = new URLSearchParams(location.search).get("topic");
  if (topic) {
    var select = document.querySelector('select[name="topic"]');
    var option = select && select.querySelector('option[data-topic="' + topic + '"]');
    if (option) select.value = option.value;
  }

  forms.forEach(function (form) {
    var button = form.querySelector('[type="submit"]');
    var label = button.textContent;
    var error = form.querySelector(".form-error");
    var success = document.getElementById(form.getAttribute("data-success"));

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.reportValidity()) return;

      // Repeated names (checkbox groups) are joined into one readable value.
      var data = {};
      new FormData(form).forEach(function (value, key) {
        data[key] = key in data ? data[key] + ", " + value : value;
      });

      button.disabled = true;
      button.textContent = "Sending…";
      error.hidden = true;

      fetch(form.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (res) {
          return res.json().catch(function () { return {}; }).then(function (out) {
            if (!res.ok || String(out.success) !== "true") throw new Error(out.message || res.status);
          });
        })
        .then(function () {
          form.hidden = true;
          success.hidden = false;
          success.focus();
          success.scrollIntoView({ block: "center", behavior: "smooth" });
        })
        .catch(function () {
          error.hidden = false;
          button.disabled = false;
          button.textContent = label;
        });
    });
  });
})();
