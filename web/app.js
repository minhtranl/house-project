/* ============================================================
 * User interface: input form, results panel and comfort gauge.
 * The physics lives in model.js.
 * ============================================================ */

(function () {
  "use strict";

  var model = window.Co2Model;

  /* --------------------------------------------------------
   * Input fields - mirrors `input_data` in the Python original.
   * `min`/`max` bound the slider only; the number box accepts
   * anything and is validated by the model.
   * -------------------------------------------------------- */

  var PARAMETERS = [
    { key: "floorArea",              label: "Floor area",                     unit: "m²",             value: 100,   min: 1,   max: 500, step: 1 },
    { key: "ceilingHeight",          label: "Ceiling height",                 unit: "m",                   value: 3,     min: 1.5, max: 10,  step: 0.1 },
    { key: "outdoorCo2",             label: "Outdoor CO₂ concentration", unit: "ppm",                 value: 400,   min: 300, max: 700, step: 5 },
    { key: "ach",                    label: "Air changes per hour",           unit: "h⁻¹",       value: 0.7,   min: 0.1, max: 10,  step: 0.1 },
    { key: "numberOfPeople",         label: "Number of occupants",            unit: "people",              value: 2,     min: 0,   max: 100, step: 1 },
    { key: "co2GenerationPerPerson", label: "CO₂ generation per person", unit: "m³/h/person",    value: 0.018, min: 0,   max: 0.1, step: 0.001 }
  ];

  var form = document.getElementById("input-form");
  var errorMessage = document.getElementById("error-message");
  var gauge = document.getElementById("gauge");
  var limitsLine = document.getElementById("limits-line");

  var results = {
    volume: document.getElementById("result-volume"),
    airflow: document.getElementById("result-airflow"),
    generation: document.getElementById("result-generation"),
    indoor: document.getElementById("result-indoor"),
    delta: document.getElementById("result-delta"),
    category: document.getElementById("result-category")
  };

  var numberInputs = {};

  /* --------------------------------------------------------
   * Build the form
   * -------------------------------------------------------- */

  PARAMETERS.forEach(function (parameter) {
    var row = document.createElement("div");
    row.className = "field";

    var label = document.createElement("label");
    label.className = "field-label";
    label.setAttribute("for", parameter.key);
    label.innerHTML = parameter.label;

    var number = document.createElement("input");
    number.type = "number";
    number.id = parameter.key;
    number.className = "field-number";
    number.step = String(parameter.step);
    number.value = String(parameter.value);
    number.setAttribute("inputmode", "decimal");

    var unit = document.createElement("span");
    unit.className = "field-unit";
    unit.innerHTML = parameter.unit;

    var range = document.createElement("input");
    range.type = "range";
    range.className = "field-range";
    range.min = String(parameter.min);
    range.max = String(parameter.max);
    range.step = String(parameter.step);
    range.value = String(parameter.value);
    range.setAttribute("aria-label", parameter.label + " slider");
    range.tabIndex = -1;

    number.addEventListener("input", function () {
      range.value = number.value;
      update();
    });

    range.addEventListener("input", function () {
      number.value = range.value;
      update();
    });

    row.appendChild(label);
    row.appendChild(number);
    row.appendChild(unit);
    row.appendChild(range);
    form.appendChild(row);

    numberInputs[parameter.key] = number;
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
  });

  /* --------------------------------------------------------
   * Formatting helpers
   * -------------------------------------------------------- */

  // Plain decimal, no thousands separator, matching the Python f-strings.
  function fixed(value, decimals) {
    return value.toFixed(decimals);
  }

  function readInputs() {
    var values = {};

    PARAMETERS.forEach(function (parameter) {
      var raw = numberInputs[parameter.key].value.trim();
      values[parameter.key] = raw === "" ? NaN : Number(raw);
    });

    return values;
  }

  function clearResults() {
    Object.keys(results).forEach(function (key) {
      results[key].innerHTML = "&mdash;";
    });

    results.indoor.className = "result-headline";
    results.category.className = "result-category";
    limitsLine.textContent = "";
    gauge.innerHTML = "";
  }

  /* --------------------------------------------------------
   * Main update cycle
   * -------------------------------------------------------- */

  function update() {
    var input = readInputs();
    var problem = model.validate(input);

    if (problem) {
      errorMessage.textContent = problem;
      errorMessage.hidden = false;
      clearResults();
      return;
    }

    errorMessage.hidden = true;

    var output = model.calculateSteadyStateCo2(input);
    var band = model.getEn16798Category(output.steadyStateCo2, input.outdoorCo2);
    var deltaCo2 = output.steadyStateCo2 - input.outdoorCo2;

    results.volume.textContent = fixed(output.volume, 1) + " m³";
    results.airflow.textContent = fixed(output.airflow, 1) + " m³/h";
    results.generation.textContent = fixed(output.totalGeneration, 4) + " m³/h";

    results.indoor.textContent = fixed(output.steadyStateCo2, 0) + " ppm";
    results.indoor.className = "result-headline cat-" + band.level;

    results.delta.textContent = fixed(deltaCo2, 0) + " ppm above outdoor";

    results.category.textContent = band.category + " — " + band.description;
    results.category.className = "result-category cat-" + band.level;

    limitsLine.innerHTML =
      "Limits for C<sub>out</sub> = " + fixed(input.outdoorCo2, 0) + " ppm: " +
      "&nbsp; I/II = " + fixed(input.outdoorCo2 + 550, 0) + " ppm" +
      " &nbsp;|&nbsp; II/III = " + fixed(input.outdoorCo2 + 800, 0) + " ppm" +
      " &nbsp;|&nbsp; III/IV = " + fixed(input.outdoorCo2 + 1350, 0) + " ppm";

    drawGauge(output.steadyStateCo2, input.outdoorCo2);
  }

  /* --------------------------------------------------------
   * EN 16798-1:2019 comfort-zone gauge.
   * Coordinates follow `draw_en16798_gauge` in the Python
   * original; the viewBox makes it scale to any width.
   * -------------------------------------------------------- */

  function drawGauge(indoorCo2, outdoorCo2) {
    var barLeft = 50;
    var barRight = 680;
    var barTop = 60;
    var barBottom = 125;
    var barWidth = barRight - barLeft;

    var limit1 = outdoorCo2 + 550;
    var limit2 = outdoorCo2 + 800;
    var limit3 = outdoorCo2 + 1350;
    var maximumDisplayCo2 = outdoorCo2 + 1800;

    function co2ToX(value) {
      var normalized = (value - outdoorCo2) / (maximumDisplayCo2 - outdoorCo2);
      normalized = Math.max(0, Math.min(1, normalized));
      return barLeft + normalized * barWidth;
    }

    var x1 = co2ToX(limit1);
    var x2 = co2ToX(limit2);
    var x3 = co2ToX(limit3);
    var markerX = co2ToX(indoorCo2);

    function band(left, right, fill) {
      return '<rect x="' + left + '" y="' + barTop +
        '" width="' + Math.max(0, right - left) +
        '" height="' + (barBottom - barTop) +
        '" fill="' + fill + '" stroke="#000" stroke-width="2"/>';
    }

    function bandLabel(left, right, lines, fill) {
      if (right - left < 34) {
        return "";
      }

      var centre = (left + right) / 2;
      var offset = lines.length > 1 ? -6 : 5;

      var tspans = lines.map(function (line, index) {
        return '<tspan x="' + centre + '" dy="' + (index === 0 ? 0 : 15) + '">' +
          line + "</tspan>";
      }).join("");

      return '<text x="' + centre + '" y="' + (85 + offset) +
        '" fill="' + fill + '" font-size="12" font-weight="bold" ' +
        'text-anchor="middle" dominant-baseline="middle">' + tspans + "</text>";
    }

    // The readout sits above the marker, but is pushed inwards when the
    // marker approaches an edge so the text never gets clipped.
    function readout(x, text) {
      var halfWidth = text.length * 3.6;
      var anchor = "middle";
      var textX = x;

      if (x - halfWidth < 4) {
        anchor = "start";
        textX = 4;
      } else if (x + halfWidth > 726) {
        anchor = "end";
        textX = 726;
      }

      return '<text x="' + textX + '" y="22" font-size="13" ' +
        'font-weight="bold" text-anchor="' + anchor +
        '" class="gauge-readout">' + text + "</text>";
    }

    function tick(x, text, bold) {
      return '<text x="' + x + '" y="158" font-size="11" text-anchor="middle"' +
        (bold ? ' font-weight="bold"' : "") +
        ' class="gauge-tick">' + text + "</text>";
    }

    gauge.innerHTML =
      band(barLeft, x1, "#008000") +
      band(x1, x2, "#FFF200") +
      band(x2, x3, "#FFA500") +
      band(x3, barRight, "#FF0000") +

      bandLabel(barLeft, x1, ["Category I", "High"], "#FFFFFF") +
      bandLabel(x1, x2, ["II"], "#000000") +
      bandLabel(x2, x3, ["Category III", "Moderate"], "#000000") +
      bandLabel(x3, barRight, ["Category IV", "Low"], "#FFFFFF") +

      tick(barLeft, fixed(outdoorCo2, 0), false) +
      tick(x1, fixed(limit1, 0), true) +
      tick(x2, fixed(limit2, 0), true) +
      tick(x3, fixed(limit3, 0), true) +
      tick(barRight, fixed(maximumDisplayCo2, 0) + "+ ppm", false) +

      '<line x1="' + markerX + '" y1="35" x2="' + markerX +
      '" y2="137" stroke="#000" stroke-width="5" class="gauge-marker"/>' +

      '<polygon points="' +
      (markerX - 8) + ",35 " + (markerX + 8) + ",35 " + markerX + ",48" +
      '" fill="#000" class="gauge-marker"/>' +

      readout(markerX, "Indoor CO₂ = " + fixed(indoorCo2, 0) + " ppm") +

      '<text x="365" y="192" font-size="11" font-style="italic" ' +
      'text-anchor="middle" class="gauge-caption">' +
      "EN 16798-1:2019 classification based on indoor CO₂ increase " +
      "above outdoor CO₂</text>";
  }

  update();
})();
