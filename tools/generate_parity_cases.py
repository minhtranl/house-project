"""
Generate parity test cases from the Python reference implementation.

The web version in ../web/model.js is a hand port of the model in
../IndoorCO2-steady_state.py. This script runs the Python original over a
grid of inputs and writes the results to ../web/parity-cases.json, which
../web/parity-test.html then replays against the JavaScript port.

Run it after any change to the model in either language:

    python tools/generate_parity_cases.py

It loads the reference file by executing only the part above the Tkinter
section, so no GUI is created and tkinter is never imported.
"""

import itertools
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_FILE = PROJECT_ROOT / "IndoorCO2-steady_state.py"
OUTPUT_FILE = PROJECT_ROOT / "web" / "parity-cases.json"

# Everything below this marker builds the Tkinter interface.
CUT_MARKER = "def calculate():"


def load_reference_model():
    """
    Execute the model half of the reference file and return its two
    public functions, without importing tkinter or opening a window.
    """

    source = REFERENCE_FILE.read_text(encoding="utf-8")

    if CUT_MARKER not in source:
        raise RuntimeError(
            f"Could not find {CUT_MARKER!r} in {REFERENCE_FILE.name}. "
            "The reference file has been restructured; update CUT_MARKER."
        )

    model_source = source.split(CUT_MARKER)[0]

    # Drop the tkinter imports: only the maths below them is needed.
    model_source = "\n".join(
        line
        for line in model_source.splitlines()
        if not line.startswith(("import tkinter", "from tkinter"))
    )

    namespace = {}
    exec(compile(model_source, str(REFERENCE_FILE), "exec"), namespace)

    return (
        namespace["calculate_steady_state_co2"],
        namespace["get_en16798_category"],
    )


def build_cases():
    calculate_steady_state_co2, get_en16798_category = load_reference_model()

    floor_areas = [12, 25, 100, 250]
    ceiling_heights = [2.4, 3, 4]
    outdoor_levels = [380, 400, 450]
    ach_values = [0.3, 0.7, 1.5, 4.0]
    occupancies = [0, 1, 2, 10, 30]
    generation_rates = [0.011, 0.018, 0.030]

    cases = []

    combinations = itertools.product(
        floor_areas,
        ceiling_heights,
        outdoor_levels,
        ach_values,
        occupancies,
        generation_rates,
    )

    for area, height, outdoor, ach, people, generation in combinations:

        volume, airflow, total_generation, steady_state = (
            calculate_steady_state_co2(
                floor_area=area,
                ceiling_height=height,
                outdoor_co2=outdoor,
                ach=ach,
                number_of_people=people,
                co2_generation_per_person=generation,
            )
        )

        category, description, _colour = get_en16798_category(
            indoor_co2=steady_state,
            outdoor_co2=outdoor,
        )

        cases.append(
            {
                "input": {
                    "floorArea": area,
                    "ceilingHeight": height,
                    "outdoorCo2": outdoor,
                    "ach": ach,
                    "numberOfPeople": people,
                    "co2GenerationPerPerson": generation,
                },
                "expected": {
                    "volume": volume,
                    "airflow": airflow,
                    "totalGeneration": total_generation,
                    "steadyStateCo2": steady_state,
                    "category": category,
                    "description": description,
                },
            }
        )

    return cases


def main():
    cases = build_cases()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(cases, indent=1),
        encoding="utf-8",
    )

    print(f"Wrote {len(cases)} cases to {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
