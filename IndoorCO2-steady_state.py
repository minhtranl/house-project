import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# Steady-state indoor CO2 model
# EN 16798-1:2019 comfort categories
# ============================================================

def calculate_steady_state_co2(
    floor_area,
    ceiling_height,
    outdoor_co2,
    ach,
    number_of_people,
    co2_generation_per_person
):
    """
    Calculate room volume, ventilation airflow and steady-state
    indoor CO2 concentration.

    Parameters
    ----------
    floor_area : float
        Floor area in m².
    ceiling_height : float
        Ceiling height in m.
    outdoor_co2 : float
        Outdoor CO2 concentration in ppm.
    ach : float
        Air changes per hour in h⁻¹.
    number_of_people : int
        Number of occupants.
    co2_generation_per_person : float
        CO2 generation rate per person in m³/h/person.

    Returns
    -------
    volume : float
        Room volume in m³.
    airflow : float
        Outdoor ventilation airflow in m³/h.
    total_generation : float
        Total occupant CO2 generation in m³/h.
    steady_state_co2 : float
        Steady-state indoor CO2 concentration in ppm.
    """

    volume = floor_area * ceiling_height
    airflow = ach * volume

    if volume <= 0:
        raise ValueError("The room volume must be greater than zero.")

    if airflow <= 0:
        raise ValueError("The ventilation airflow must be greater than zero.")

    total_generation = (
        number_of_people * co2_generation_per_person
    )

    steady_state_co2 = (
        outdoor_co2
        + (total_generation / airflow) * 1_000_000
    )

    return (
        volume,
        airflow,
        total_generation,
        steady_state_co2
    )


def get_en16798_category(indoor_co2, outdoor_co2):
    """
    Determine the indoor environmental category using the
    EN 16798-1:2019 CO2 increase above outdoor concentration.

    Category I:   ΔCO2 <= 550 ppm
    Category II:  550 < ΔCO2 <= 800 ppm
    Category III: 800 < ΔCO2 <= 1350 ppm
    Category IV:  ΔCO2 > 1350 ppm
    """

    delta_co2 = indoor_co2 - outdoor_co2

    if delta_co2 <= 550:
        return (
            "Category I",
            "High indoor air quality",
            "green"
        )

    elif delta_co2 <= 800:
        return (
            "Category II",
            "Medium indoor air quality",
            "#FFD700"
        )

    elif delta_co2 <= 1350:
        return (
            "Category III",
            "Moderate indoor air quality",
            "orange"
        )

    else:
        return (
            "Category IV",
            "Low indoor air quality",
            "red"
        )


def calculate():
    """Read the inputs, calculate the results and update the display."""

    try:
        floor_area = float(entry_area.get())
        ceiling_height = float(entry_height.get())
        outdoor_co2 = float(entry_outdoor.get())
        ach = float(entry_ach.get())
        number_of_people = int(entry_people.get())
        generation_rate = float(entry_generation.get())

        if floor_area <= 0:
            raise ValueError("Floor area must be greater than zero.")

        if ceiling_height <= 0:
            raise ValueError("Ceiling height must be greater than zero.")

        if outdoor_co2 < 0:
            raise ValueError(
                "Outdoor CO2 concentration cannot be negative."
            )

        if ach <= 0:
            raise ValueError(
                "Air changes per hour must be greater than zero."
            )

        if number_of_people < 0:
            raise ValueError(
                "The number of occupants cannot be negative."
            )

        if generation_rate < 0:
            raise ValueError(
                "The CO2 generation rate cannot be negative."
            )

        (
            volume,
            airflow,
            total_generation,
            steady_state_co2
        ) = calculate_steady_state_co2(
            floor_area=floor_area,
            ceiling_height=ceiling_height,
            outdoor_co2=outdoor_co2,
            ach=ach,
            number_of_people=number_of_people,
            co2_generation_per_person=generation_rate
        )

        category, description, category_color = (
            get_en16798_category(
                indoor_co2=steady_state_co2,
                outdoor_co2=outdoor_co2
            )
        )

        delta_co2 = steady_state_co2 - outdoor_co2

        # EN 16798-1 limits depending on outdoor CO2
        limit_category_1 = outdoor_co2 + 550
        limit_category_2 = outdoor_co2 + 800
        limit_category_3 = outdoor_co2 + 1350

        # Update numerical results
        label_volume_value.config(
            text=f"{volume:.1f} m³"
        )

        label_airflow_value.config(
            text=f"{airflow:.1f} m³/h"
        )

        label_generation_value.config(
            text=f"{total_generation:.4f} m³/h"
        )

        label_indoor_co2_value.config(
            text=f"{steady_state_co2:.0f} ppm",
            foreground=category_color
        )

        label_delta_co2_value.config(
            text=f"{delta_co2:.0f} ppm above outdoor"
        )

        label_category_value.config(
            text=f"{category} — {description}",
            foreground=category_color
        )

        label_limits.config(
            text=(
                f"Limits for Cₒᵤₜ = {outdoor_co2:.0f} ppm:  "
                f"I/II = {limit_category_1:.0f} ppm   |   "
                f"II/III = {limit_category_2:.0f} ppm   |   "
                f"III/IV = {limit_category_3:.0f} ppm"
            )
        )

        draw_en16798_gauge(
            indoor_co2=steady_state_co2,
            outdoor_co2=outdoor_co2
        )

    except ValueError as error:
        messagebox.showerror(
            "Invalid input",
            str(error)
        )


def draw_en16798_gauge(indoor_co2, outdoor_co2):
    """
    Draw the EN 16798-1:2019 comfort-zone gauge.
    """

    canvas.delete("all")

    canvas_width = 720
    bar_left = 50
    bar_right = 680
    bar_top = 60
    bar_bottom = 125
    bar_width = bar_right - bar_left

    # EN 16798-1 indoor concentration limits
    category_1_limit = outdoor_co2 + 550
    category_2_limit = outdoor_co2 + 800
    category_3_limit = outdoor_co2 + 1350

    # Upper display limit for Category IV
    maximum_display_co2 = outdoor_co2 + 1800

    def co2_to_x(co2_value):
        """Convert a CO2 concentration into a horizontal coordinate."""

        normalized_value = (
            (co2_value - outdoor_co2)
            / (maximum_display_co2 - outdoor_co2)
        )

        normalized_value = max(
            0.0,
            min(1.0, normalized_value)
        )

        return bar_left + normalized_value * bar_width

    x_category_1 = co2_to_x(category_1_limit)
    x_category_2 = co2_to_x(category_2_limit)
    x_category_3 = co2_to_x(category_3_limit)

    # Category I
    canvas.create_rectangle(
        bar_left,
        bar_top,
        x_category_1,
        bar_bottom,
        fill="green",
        outline="black",
        width=2
    )

    # Category II
    canvas.create_rectangle(
        x_category_1,
        bar_top,
        x_category_2,
        bar_bottom,
        fill="#FFF200",
        outline="black",
        width=2
    )

    # Category III
    canvas.create_rectangle(
        x_category_2,
        bar_top,
        x_category_3,
        bar_bottom,
        fill="orange",
        outline="black",
        width=2
    )

    # Category IV
    canvas.create_rectangle(
        x_category_3,
        bar_top,
        bar_right,
        bar_bottom,
        fill="red",
        outline="black",
        width=2
    )

    # Category labels
    canvas.create_text(
        (bar_left + x_category_1) / 2,
        85,
        text="Category I\nHigh",
        fill="white",
        font=("Arial", 10, "bold")
    )

    canvas.create_text(
        (x_category_1 + x_category_2) / 2,
        85,
        text="II",
        fill="black",
        font=("Arial", 10, "bold")
    )

    canvas.create_text(
        (x_category_2 + x_category_3) / 2,
        85,
        text="Category III\nModerate",
        fill="black",
        font=("Arial", 10, "bold")
    )

    canvas.create_text(
        (x_category_3 + bar_right) / 2,
        85,
        text="Category IV\nLow",
        fill="white",
        font=("Arial", 10, "bold")
    )

    # Threshold labels
    canvas.create_text(
        bar_left,
        145,
        text=f"{outdoor_co2:.0f}",
        anchor="n",
        font=("Arial", 9)
    )

    canvas.create_text(
        x_category_1,
        145,
        text=f"{category_1_limit:.0f}",
        anchor="n",
        font=("Arial", 9, "bold")
    )

    canvas.create_text(
        x_category_2,
        145,
        text=f"{category_2_limit:.0f}",
        anchor="n",
        font=("Arial", 9, "bold")
    )

    canvas.create_text(
        x_category_3,
        145,
        text=f"{category_3_limit:.0f}",
        anchor="n",
        font=("Arial", 9, "bold")
    )

    canvas.create_text(
        bar_right,
        145,
        text=f"{maximum_display_co2:.0f}+ ppm",
        anchor="n",
        font=("Arial", 9)
    )

    # Indoor CO2 marker
    marker_x = co2_to_x(indoor_co2)

    canvas.create_line(
        marker_x,
        35,
        marker_x,
        137,
        fill="black",
        width=5
    )

    canvas.create_polygon(
        marker_x - 8,
        35,
        marker_x + 8,
        35,
        marker_x,
        48,
        fill="black"
    )

    canvas.create_text(
        marker_x,
        18,
        text=f"Indoor CO₂ = {indoor_co2:.0f} ppm",
        font=("Arial", 11, "bold")
    )

    canvas.create_text(
        365,
        185,
        text=(
            "EN 16798-1:2019 classification based on "
            "indoor CO₂ increase above outdoor CO₂"
        ),
        font=("Arial", 9, "italic")
    )


# ============================================================
# Graphical interface
# ============================================================

root = tk.Tk()
root.title(
    "Indoor CO₂ Steady-State Model — EN 16798-1:2019"
)
root.geometry("1050x720")
root.minsize(950, 650)

main_frame = ttk.Frame(
    root,
    padding=20
)
main_frame.pack(
    fill="both",
    expand=True
)

title_label = ttk.Label(
    main_frame,
    text=(
        "Indoor CO₂ Steady-State Calculator\n"
        "Comfort categories according to EN 16798-1:2019"
    ),
    font=("Arial", 17, "bold"),
    justify="center"
)
title_label.pack(pady=(0, 20))

content_frame = ttk.Frame(main_frame)
content_frame.pack(
    fill="x",
    expand=False
)

input_frame = ttk.LabelFrame(
    content_frame,
    text="Input parameters",
    padding=15
)
input_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)

result_frame = ttk.LabelFrame(
    content_frame,
    text="Calculated results",
    padding=15
)
result_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(10, 0)
)


# ============================================================
# Input fields
# ============================================================

input_data = [
    ("Floor area", "100", "m²"),
    ("Ceiling height", "3", "m"),
    ("Outdoor CO₂ concentration", "400", "ppm"),
    ("Air changes per hour", "0.7", "h⁻¹"),
    ("Number of occupants", "2", "people"),
    ("CO₂ generation per person", "0.018", "m³/h/person")
]

entries = []

for row, (parameter, default_value, unit) in enumerate(input_data):

    ttk.Label(
        input_frame,
        text=parameter
    ).grid(
        row=row,
        column=0,
        sticky="w",
        padx=5,
        pady=8
    )

    entry = ttk.Entry(
        input_frame,
        width=14
    )
    entry.insert(0, default_value)
    entry.grid(
        row=row,
        column=1,
        padx=5,
        pady=8
    )

    ttk.Label(
        input_frame,
        text=unit
    ).grid(
        row=row,
        column=2,
        sticky="w",
        padx=5,
        pady=8
    )

    entries.append(entry)

(
    entry_area,
    entry_height,
    entry_outdoor,
    entry_ach,
    entry_people,
    entry_generation
) = entries

calculate_button = ttk.Button(
    input_frame,
    text="Calculate indoor CO₂",
    command=calculate
)
calculate_button.grid(
    row=len(input_data),
    column=0,
    columnspan=3,
    pady=20
)


# ============================================================
# Result fields
# ============================================================

result_labels = [
    "Room volume:",
    "Ventilation airflow:",
    "Total CO₂ generation:",
    "Steady-state indoor CO₂:",
    "CO₂ increase:",
    "EN 16798-1 category:"
]

value_labels = []

for row, label_text in enumerate(result_labels):

    ttk.Label(
        result_frame,
        text=label_text,
        font=("Arial", 10, "bold")
    ).grid(
        row=row,
        column=0,
        sticky="w",
        padx=5,
        pady=9
    )

    value_label = ttk.Label(
        result_frame,
        text="—",
        font=("Arial", 11)
    )
    value_label.grid(
        row=row,
        column=1,
        sticky="w",
        padx=10,
        pady=9
    )

    value_labels.append(value_label)

(
    label_volume_value,
    label_airflow_value,
    label_generation_value,
    label_indoor_co2_value,
    label_delta_co2_value,
    label_category_value
) = value_labels

label_indoor_co2_value.config(
    font=("Arial", 17, "bold")
)

label_category_value.config(
    font=("Arial", 12, "bold")
)


# ============================================================
# Comfort-zone gauge
# ============================================================

gauge_frame = ttk.LabelFrame(
    main_frame,
    text="EN 16798-1:2019 indoor CO₂ comfort zones",
    padding=10
)
gauge_frame.pack(
    fill="both",
    expand=True,
    pady=(20, 0)
)

label_limits = ttk.Label(
    gauge_frame,
    text="",
    font=("Arial", 10),
    justify="center"
)
label_limits.pack(pady=(5, 0))

canvas = tk.Canvas(
    gauge_frame,
    width=730,
    height=210,
    background="#F3F3F3",
    highlightthickness=0
)
canvas.pack(
    fill="both",
    expand=True,
    pady=5
)

formula_label = ttk.Label(
    gauge_frame,
    text=(
        "Model: Cₛₛ = Cₒᵤₜ + "
        "(N × Gₚ / Q) × 10⁶,     "
        "with Q = ACH × V"
    ),
    font=("Arial", 11, "italic")
)
formula_label.pack(pady=8)


# Perform the initial calculation
calculate()

root.mainloop()