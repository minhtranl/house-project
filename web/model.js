/* ============================================================
 * Steady-state indoor CO2 model
 * EN 16798-1:2019 comfort categories
 *
 * Direct port of the reference implementation in
 * ../IndoorCO2-steady_state.py. Keep the two in step:
 * parity-test.html checks this file against cases generated
 * from the Python original.
 * ============================================================ */

(function (global) {
  "use strict";

  /**
   * Calculate room volume, ventilation airflow and steady-state
   * indoor CO2 concentration.
   *
   * @param {object} input
   * @param {number} input.floorArea                 Floor area in m2.
   * @param {number} input.ceilingHeight             Ceiling height in m.
   * @param {number} input.outdoorCo2                Outdoor CO2 concentration in ppm.
   * @param {number} input.ach                       Air changes per hour in h^-1.
   * @param {number} input.numberOfPeople            Number of occupants.
   * @param {number} input.co2GenerationPerPerson    CO2 generation in m3/h/person.
   * @returns {{volume:number, airflow:number, totalGeneration:number, steadyStateCo2:number}}
   */
  function calculateSteadyStateCo2(input) {
    var volume = input.floorArea * input.ceilingHeight;
    var airflow = input.ach * volume;

    if (volume <= 0) {
      throw new RangeError("The room volume must be greater than zero.");
    }

    if (airflow <= 0) {
      throw new RangeError("The ventilation airflow must be greater than zero.");
    }

    var totalGeneration = input.numberOfPeople * input.co2GenerationPerPerson;

    var steadyStateCo2 =
      input.outdoorCo2 + (totalGeneration / airflow) * 1000000;

    return {
      volume: volume,
      airflow: airflow,
      totalGeneration: totalGeneration,
      steadyStateCo2: steadyStateCo2
    };
  }

  /**
   * Determine the indoor environmental category using the
   * EN 16798-1:2019 CO2 increase above outdoor concentration.
   *
   * Category I:   dCO2 <= 550 ppm
   * Category II:  550 < dCO2 <= 800 ppm
   * Category III: 800 < dCO2 <= 1350 ppm
   * Category IV:  dCO2 > 1350 ppm
   */
  function getEn16798Category(indoorCo2, outdoorCo2) {
    var deltaCo2 = indoorCo2 - outdoorCo2;

    if (deltaCo2 <= 550) {
      return {
        category: "Category I",
        description: "High indoor air quality",
        level: 1
      };
    }

    if (deltaCo2 <= 800) {
      return {
        category: "Category II",
        description: "Medium indoor air quality",
        level: 2
      };
    }

    if (deltaCo2 <= 1350) {
      return {
        category: "Category III",
        description: "Moderate indoor air quality",
        level: 3
      };
    }

    return {
      category: "Category IV",
      description: "Low indoor air quality",
      level: 4
    };
  }

  /**
   * Validate the six inputs, mirroring the checks in the Python original.
   * Returns null when everything is valid, otherwise the message to display.
   */
  function validate(input) {
    var checks = [
      [!isFinite(input.floorArea), "Floor area must be a number."],
      [input.floorArea <= 0, "Floor area must be greater than zero."],
      [!isFinite(input.ceilingHeight), "Ceiling height must be a number."],
      [input.ceilingHeight <= 0, "Ceiling height must be greater than zero."],
      [!isFinite(input.outdoorCo2), "Outdoor CO\u2082 concentration must be a number."],
      [input.outdoorCo2 < 0, "Outdoor CO\u2082 concentration cannot be negative."],
      [!isFinite(input.ach), "Air changes per hour must be a number."],
      [input.ach <= 0, "Air changes per hour must be greater than zero."],
      [!isFinite(input.numberOfPeople), "The number of occupants must be a number."],
      [input.numberOfPeople < 0, "The number of occupants cannot be negative."],
      [!isFinite(input.co2GenerationPerPerson), "The CO\u2082 generation rate must be a number."],
      [input.co2GenerationPerPerson < 0, "The CO\u2082 generation rate cannot be negative."]
    ];

    for (var i = 0; i < checks.length; i += 1) {
      if (checks[i][0]) {
        return checks[i][1];
      }
    }

    return null;
  }

  global.Co2Model = {
    calculateSteadyStateCo2: calculateSteadyStateCo2,
    getEn16798Category: getEn16798Category,
    validate: validate
  };
})(this);
