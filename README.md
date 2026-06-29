# Construction-Calculations-Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/construction-calculations-suite.svg?color=brightgreen)](https://pypi.org/project/construction-calculations-suite/)
[![Build Status](https://img.shields.io/travis/datoxic0/Construction-Calculations-Suite.svg?style=flat-square)](https://travis-ci.org/datoxic0/Construction-Calculations-Suite)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Python suite for construction material volume and weight calculations, designed for professional engineering and logistics applications. This tool facilitates accurate conversions between volume and mass for bulk materials, incorporating essential factors like unit conversions, cost estimation, and site-specific corrections.

## Features

*   **Extensive Unit Support:**
    *   **Volume:** Cubic Metre (m³), Litre (L), Cubic Foot (ft³), Cubic Yard (yd³), US Gallon (gal(US)), Imperial Gallon (gal(UK)), Cubic Inch (in³).
    *   **Mass:** Metric Tonne (t), Kilogram (kg), Short Ton (st), Long Ton (lt), Pound (lb).
*   **Material Density Library:** A built-in library with over 30 common construction materials (e.g., sand, gravel, concrete, asphalt, wood chips) including loose and compacted densities.
*   **Bi-directional Conversion:** Seamlessly convert between volume and mass using `volume_to_mass()` and `mass_to_volume()` functions.
*   **Correction Factors:** Account for real-world variations with adjustable factors for:
    *   Moisture Content (`moisture_factor`)
    *   Compaction (`compaction_factor`)
    *   Swell (`swell_factor`)
    *   Waste (`waste_factor`)
*   **Cost Estimation:** Calculate project costs based on price per unit mass or volume, supporting various currency symbols and units.
*   **User-Friendly API:** A high-level `ConversionSuite` class provides a simple interface for common operations.
*   **Command-Line Interface (CLI):** An interactive CLI for quick, ad-hoc calculations directly from the terminal.
*   **Extensibility:** Designed for easy addition of new units, materials, or custom correction logic.
*   **Robustness:** Includes input validation, error handling, and a suite of unit tests for reliability.

## Setup Instructions

### Installation

This library can be installed directly from PyPI:

```bash
pip install construction-calculations-suite
```

Alternatively, you can clone the repository and use the provided Python file directly:

```bash
git clone https://github.com/datoxic0/Construction-Calculations-Suite.git
cd Construction-Calculations-Suite
# Now you can run the script directly or import it
```

### Usage

#### As a Module

Import the `ConversionSuite` class into your Python project:

```python
from calculations_suite import ConversionSuite

# Initialize the suite
suite = ConversionSuite()

# Select a material and optionally apply corrections
suite.select_material("sand_dry_loose", moisture_factor=1.05, waste_factor=1.10)

# Convert volume to mass
volume_m3 = 10.0
mass_tonnes = suite.volume_to_mass(volume_m3, vol_unit="m³", mass_unit="t")
print(f"{volume_m3} m³ of sand is approximately {mass_tonnes:.2f} tonnes.")

# Convert mass to volume
mass_short_tons = 25.0
volume_cubic_yards = suite.mass_to_volume(mass_short_tons, mass_unit="st", vol_unit="yd³")
print(f"{mass_short_tons} short tons of sand is approximately {volume_cubic_yards:.2f} cubic yards.")

# Estimate cost
price_per_tonne = 15.50
cost = suite.estimate_cost_by_mass(mass_tonnes, "t", price_per_tonne, "t", currency="$")
print(f"The estimated cost for {mass_tonnes:.2f} tonnes is {cost}.")
```

#### Command-Line Interface (CLI)

Run the script directly from your terminal to use the interactive CLI:

```bash
python calculations_suite.py
```

The CLI will guide you through selecting materials, applying corrections, and performing conversions or cost estimations.

You can also run built-in demonstrations or tests:

```bash
# Run a quick demonstration of features
python calculations_suite.py --demo

# Run the unit tests
python calculations_suite.py --test
```

## Technology Stack

*   **Python:** 3.8+
*   **Standard Library:** `enum`, `typing`, `math`, `sys`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.