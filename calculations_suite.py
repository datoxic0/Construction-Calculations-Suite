#!/usr/bin/env python3
"""
Advanced Material Volume ⇄ Weight Calculation Suite
===================================================
Professional engineering and logistics tool for converting
between volume and weight (mass) for bulk materials.

Supports: metric tonnes, short tons, long tons, kg, lb
          cubic metre, litre, cubic foot, cubic yard, US gallon
          cost estimation, moisture/compaction corrections

Author: AI Engineering Solutions
Version: 2.0.0
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Dict, Optional, Tuple, Union, List
import math
import sys

# -----------------------------------------------------------------------------
# 1. Unit Systems – Precise conversion factors to/from base SI (m³, kg)
# -----------------------------------------------------------------------------

class VolumeUnit(Enum):
    """Supported volume units with conversion factor to cubic metres."""
    CUBIC_METRE      = (1.0, "m³")
    LITRE            = (0.001, "L")
    CUBIC_FOOT       = (0.028316846592, "ft³")
    CUBIC_YARD       = (0.764554857984, "yd³")
    US_GALLON        = (0.003785411784, "gal(US)")
    IMPERIAL_GALLON  = (0.00454609, "gal(UK)")
    CUBIC_INCH       = (1.6387064e-5, "in³")

    def __init__(self, to_m3: float, symbol: str):
        self.to_m3 = to_m3
        self.symbol = symbol

    @classmethod
    def from_symbol(cls, sym: str) -> 'VolumeUnit':
        for unit in cls:
            if unit.symbol.lower() == sym.lower():
                return unit
        raise ValueError(f"Unknown volume unit symbol: {sym}")

class MassUnit(Enum):
    """Supported mass units with conversion factor to kilograms."""
    METRIC_TONNE     = (1000.0, "t")
    KILOGRAM         = (1.0, "kg")
    SHORT_TON        = (907.18474, "st")       # US ton
    LONG_TON         = (1016.0469088, "lt")     # UK / imperial ton
    POUND            = (0.45359237, "lb")

    def __init__(self, to_kg: float, symbol: str):
        self.to_kg = to_kg
        self.symbol = symbol

    @classmethod
    def from_symbol(cls, sym: str) -> 'MassUnit':
        for unit in cls:
            if unit.symbol.lower() == sym.lower():
                return unit
        raise ValueError(f"Unknown mass unit symbol: {sym}")

# -----------------------------------------------------------------------------
# 2. Material Definition & Built-in Density Library
# -----------------------------------------------------------------------------

class Material:
    """
    Represents a bulk material with a base dry density.
    Density is stored in kg/m³ (SI internal), but can be accessed in any unit.
    """
    def __init__(self, name: str, density_kg_per_m3: float,
                 typical_range: Optional[Tuple[float, float]] = None,
                 description: str = ""):
        if density_kg_per_m3 <= 0:
            raise ValueError("Density must be positive.")
        self.name = name
        self._density_si = density_kg_per_m3
        self.typical_range = typical_range
        self.description = description

    @property
    def density_si(self) -> float:
        return self._density_si

    def density(self, mass_unit: MassUnit = MassUnit.KILOGRAM,
                volume_unit: VolumeUnit = VolumeUnit.CUBIC_METRE) -> float:
        """
        Returns density in the requested mass/volume units.
        E.g., material.density(MassUnit.METRIC_TONNE, VolumeUnit.LITRE)
        """
        kg_per_desired_vol = self._density_si / volume_unit.to_m3
        return kg_per_desired_vol / mass_unit.to_kg

    def __repr__(self):
        return f"Material('{self.name}', {self._density_si:.1f} kg/m³)"

# Built-in material database (extensive)
MATERIAL_LIBRARY: Dict[str, Material] = {
    # Water & liquids
    "water":                Material("Water", 1000.0, description="Pure water at 4°C"),
    "diesel":               Material("Diesel", 840.0, (820, 950)),
    "petrol":               Material("Petrol", 750.0, (700, 770)),
    "crude_oil":            Material("Crude Oil", 870.0, (790, 970)),
    # Soils & aggregates
    "topsoil_loose":        Material("Topsoil (loose)", 1200.0, (1100, 1350)),
    "topsoil_compacted":    Material("Topsoil (compacted)", 1550.0, (1400, 1650)),
    "clay_dry":             Material("Clay (dry)", 1600.0, (1400, 1700)),
    "clay_wet":             Material("Clay (wet)", 1750.0, (1600, 1900)),
    "sand_dry_loose":       Material("Sand, dry loose", 1442.0, (1300, 1550)),
    "sand_dry_compacted":   Material("Sand, dry compacted", 1680.0, (1550, 1750)),
    "sand_wet":             Material("Sand, wet", 1922.0, (1800, 2000)),
    "gravel_loose":         Material("Gravel, loose dry", 1522.0, (1400, 1700)),
    "gravel_compacted":     Material("Gravel, compacted", 1750.0, (1650, 1850)),
    "crushed_stone":        Material("Crushed Stone", 1600.0, (1400, 1800)),
    # Construction
    "concrete":             Material("Concrete", 2400.0, (2200, 2500)),
    "asphalt":              Material("Asphalt", 2320.0, (2200, 2450)),
    "brick_common":         Material("Brick (common)", 1920.0, (1600, 2000)),
    "cement_portland":      Material("Portland Cement", 1500.0, (1300, 1600)),
    "lime":                 Material("Lime", 1120.0, (800, 1300)),
    # Wood & organic
    "wood_chips":           Material("Wood Chips", 380.0, (200, 600)),
    "sawdust":              Material("Sawdust", 210.0, (150, 300)),
    "bark":                 Material("Bark", 320.0, (200, 500)),
    "compost":              Material("Compost", 600.0, (400, 800)),
    # Metals & ores
    "iron_ore":             Material("Iron Ore", 2400.0, (2100, 2800)),
    "steel":                Material("Steel (solid)", 7850.0),
    "aluminium":            Material("Aluminium (solid)", 2700.0),
    # Miscellaneous
    "snow_fresh":           Material("Snow, fresh", 160.0, (50, 250)),
    "snow_compacted":       Material("Snow, compacted", 480.0, (300, 600)),
    "ice":                  Material("Ice", 917.0),
    "rubble":               Material("Rubble (demolition)", 1400.0, (1200, 1600)),
    "coal_bituminous":      Material("Coal (bituminous)", 1350.0, (1200, 1500)),
    "salt_bulk":            Material("Salt (bulk)", 1200.0, (1100, 1300)),
}

def list_materials() -> List[str]:
    """Return sorted list of available material keys."""
    return sorted(MATERIAL_LIBRARY.keys())

def get_material(identifier: str) -> Material:
    """Retrieve a material by key name, case-insensitive."""
    key = identifier.lower().strip()
    if key in MATERIAL_LIBRARY:
        return MATERIAL_LIBRARY[key]
    # Try partial match
    matches = [name for name in MATERIAL_LIBRARY if key in name]
    if len(matches) == 1:
        return MATERIAL_LIBRARY[matches[0]]
    elif len(matches) > 1:
        raise ValueError(f"Ambiguous material name '{identifier}'. Candidates: {matches}")
    raise ValueError(f"Material '{identifier}' not found. Available: {list_materials()}")

# -----------------------------------------------------------------------------
# 3. Correction Factors (Moisture, Compaction, Swell, Waste)
# -----------------------------------------------------------------------------

class CorrectionFactors:
    """
    Multipliers applied to the base density to account for site conditions.
    All factors are combined multiplicatively: effective density = base_density * Π factors
    """
    def __init__(self,
                 moisture_factor: float = 1.0,
                 compaction_factor: float = 1.0,
                 swell_factor: float = 1.0,
                 waste_factor: float = 1.0):
        if any(f <= 0 for f in (moisture_factor, compaction_factor, swell_factor, waste_factor)):
            raise ValueError("All correction factors must be > 0")
        self.moisture_factor = moisture_factor
        self.compaction_factor = compaction_factor
        self.swell_factor = swell_factor
        self.waste_factor = waste_factor

    def combined(self) -> float:
        return self.moisture_factor * self.compaction_factor * self.swell_factor * self.waste_factor

    def __repr__(self):
        return (f"CorrectionFactors(moisture={self.moisture_factor:.3f}, "
                f"compaction={self.compaction_factor:.3f}, swell={self.swell_factor:.3f}, "
                f"waste={self.waste_factor:.3f})")

# -----------------------------------------------------------------------------
# 4. Core Conversion Engine
# -----------------------------------------------------------------------------

class MaterialConverter:
    """
    Performs volume ⇄ mass conversions for a given material and correction state.
    """
    def __init__(self, material: Material, corrections: CorrectionFactors = CorrectionFactors()):
        self.material = material
        self.corrections = corrections

    def effective_density_si(self) -> float:
        """Density in kg/m³ after applying all correction factors."""
        return self.material.density_si * self.corrections.combined()

    def volume_to_mass(self,
                       volume: float,
                       vol_unit: VolumeUnit,
                       mass_unit: MassUnit) -> float:
        """Convert volume (in given unit) to mass (in given unit)."""
        if volume < 0:
            raise ValueError("Volume must be >= 0")
        # Convert volume to m³
        vol_m3 = volume * vol_unit.to_m3
        # Effective density in kg/m³ → total mass in kg
        mass_kg = vol_m3 * self.effective_density_si()
        # Convert kg to desired mass unit
        return mass_kg / mass_unit.to_kg

    def mass_to_volume(self,
                       mass: float,
                       mass_unit: MassUnit,
                       vol_unit: VolumeUnit) -> float:
        """Convert mass (in given unit) to volume (in given unit)."""
        if mass < 0:
            raise ValueError("Mass must be >= 0")
        # Convert mass to kg
        mass_kg = mass * mass_unit.to_kg
        # Volume in m³
        vol_m3 = mass_kg / self.effective_density_si()
        # Convert to desired volume unit
        return vol_m3 / vol_unit.to_m3

    def __repr__(self):
        return f"MaterialConverter({self.material.name}, corr={self.corrections})"

# -----------------------------------------------------------------------------
# 5. Cost Calculator
# -----------------------------------------------------------------------------

class CostCalculator:
    """
    Computes total cost given a price per unit mass or volume.
    Price can be per metric tonne, per kg, per m³, etc.
    """
    def __init__(self, converter: MaterialConverter):
        self.converter = converter

    def cost_by_volume(self, volume: float, vol_unit: VolumeUnit,
                       price_per_vol: float, price_vol_unit: VolumeUnit,
                       currency_symbol: str = "$") -> Tuple[float, str]:
        """
        Calculate cost for a given volume.
        price_per_vol: price per unit volume (e.g., per m³)
        """
        # Normalise volume to price volume unit
        vol_in_price_units = volume * vol_unit.to_m3 / price_vol_unit.to_m3
        total_cost = vol_in_price_units * price_per_vol
        return total_cost, f"{currency_symbol}{total_cost:,.2f}"

    def cost_by_mass(self, mass: float, mass_unit: MassUnit,
                     price_per_mass: float, price_mass_unit: MassUnit,
                     currency_symbol: str = "$") -> Tuple[float, str]:
        """Calculate cost for a given mass."""
        mass_in_price_units = mass * mass_unit.to_kg / price_mass_unit.to_kg
        total_cost = mass_in_price_units * price_per_mass
        return total_cost, f"{currency_symbol}{total_cost:,.2f}"

# -----------------------------------------------------------------------------
# 6. High-level Conversion Suite (User-friendly API)
# -----------------------------------------------------------------------------

class ConversionSuite:
    """
    Single entry point for all calculations.
    Maintains a current material and correction state.
    """
    def __init__(self):
        self.converter: Optional[MaterialConverter] = None
        self.cost_calc: Optional[CostCalculator] = None

    def select_material(self, material_id: str, **corrections) -> None:
        """
        Select a material from the library and optionally set correction factors.
        Example: suite.select_material('sand_dry_loose', moisture_factor=1.05)
        """
        mat = get_material(material_id)
        corr = CorrectionFactors(**corrections)
        self.converter = MaterialConverter(mat, corr)
        self.cost_calc = CostCalculator(self.converter)
        print(f"Selected: {mat.name} (base density {mat.density_si:.1f} kg/m³)")
        if any(v != 1.0 for v in (corr.moisture_factor, corr.compaction_factor,
                                  corr.swell_factor, corr.waste_factor)):
            print(f"Corrections: {corr} => effective density {self.converter.effective_density_si():.1f} kg/m³")

    def volume_to_mass(self, volume: float, vol_unit: str = "m³", mass_unit: str = "t") -> float:
        """Quick string-based conversion. Units can be symbols like 'm³', 'L', 't', 'kg'."""
        if not self.converter:
            raise RuntimeError("No material selected. Use select_material() first.")
        v_unit = VolumeUnit.from_symbol(vol_unit)
        m_unit = MassUnit.from_symbol(mass_unit)
        return self.converter.volume_to_mass(volume, v_unit, m_unit)

    def mass_to_volume(self, mass: float, mass_unit: str = "t", vol_unit: str = "m³") -> float:
        if not self.converter:
            raise RuntimeError("No material selected.")
        m_unit = MassUnit.from_symbol(mass_unit)
        v_unit = VolumeUnit.from_symbol(vol_unit)
        return self.converter.mass_to_volume(mass, m_unit, v_unit)

    def estimate_cost_by_volume(self, volume: float, vol_unit: str,
                                price_per_vol: float, price_vol_unit: str,
                                currency: str = "$") -> str:
        if not self.cost_calc:
            raise RuntimeError("No material selected.")
        v_unit = VolumeUnit.from_symbol(vol_unit)
        pv_unit = VolumeUnit.from_symbol(price_vol_unit)
        _, formatted = self.cost_calc.cost_by_volume(volume, v_unit, price_per_vol, pv_unit, currency)
        return formatted

    def estimate_cost_by_mass(self, mass: float, mass_unit: str,
                              price_per_mass: float, price_mass_unit: str,
                              currency: str = "$") -> str:
        if not self.cost_calc:
            raise RuntimeError("No material selected.")
        m_unit = MassUnit.from_symbol(mass_unit)
        pm_unit = MassUnit.from_symbol(price_mass_unit)
        _, formatted = self.cost_calc.cost_by_mass(mass, m_unit, price_per_mass, pm_unit, currency)
        return formatted

# -----------------------------------------------------------------------------
# 7. Command-Line Interface (for direct use)
# -----------------------------------------------------------------------------

def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║      MATERIAL VOLUME ⇄ WEIGHT CALCULATION SUITE     ║
╚══════════════════════════════════════════════════════╝
""")

def interactive_cli():
    suite = ConversionSuite()
    print_banner()
    print("Available materials:")
    for i, mat in enumerate(list_materials(), 1):
        print(f"  {i:2d}: {mat}")
    print()
    while True:
        try:
            choice = input("Enter material name/number (or 'quit'): ").strip()
            if choice.lower() in ('quit', 'exit', 'q'):
                break
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(list_materials()):
                    mat_id = list_materials()[idx]
                else:
                    print("Invalid number. Try again.")
                    continue
            else:
                mat_id = choice
            suite.select_material(mat_id)
            # Optionally set corrections
            corr_input = input("Correction factors? (moisture compaction swell waste, space-separated, Enter for none): ").strip()
            if corr_input:
                parts = [float(x) for x in corr_input.split()]
                corrs = {}
                names = ['moisture_factor', 'compaction_factor', 'swell_factor', 'waste_factor']
                for i, val in enumerate(parts[:4]):
                    corrs[names[i]] = val
                suite.select_material(mat_id, **corrs)  # re-select with corrections
            while True:
                action = input("Convert (v)olume→mass, (m)ass→volume, (c)ost, or (b)ack: ").strip().lower()
                if action == 'b':
                    break
                if action == 'v':
                    vol = float(input("Volume: "))
                    vu = input("Volume unit (m³, L, ft³, yd³, gal): ").strip()
                    mu = input("Target mass unit (t, kg, st, lt, lb): ").strip()
                    result = suite.volume_to_mass(vol, vu, mu)
                    print(f"  → {vol} {vu} of {suite.converter.material.name} = {result:.3f} {mu}")
                elif action == 'm':
                    mass = float(input("Mass: "))
                    mu = input("Mass unit (t, kg, st, lt, lb): ").strip()
                    vu = input("Target volume unit (m³, L, ft³, yd³, gal): ").strip()
                    result = suite.mass_to_volume(mass, mu, vu)
                    print(f"  → {mass} {mu} of {suite.converter.material.name} = {result:.3f} {vu}")
                elif action == 'c':
                    cost_type = input("Cost by (v)olume or (m)ass? ").strip().lower()
                    if cost_type == 'v':
                        vol = float(input("Volume: "))
                        vu = input("Volume unit: ").strip()
                        price = float(input("Price per volume unit (e.g., per m³): "))
                        pu = input("Volume unit of price (e.g., m³): ").strip()
                        print(suite.estimate_cost_by_volume(vol, vu, price, pu))
                    elif cost_type == 'm':
                        mass = float(input("Mass: "))
                        mu = input("Mass unit: ").strip()
                        price = float(input("Price per mass unit (e.g., per t): "))
                        pu = input("Mass unit of price (e.g., t): ").strip()
                        print(suite.estimate_cost_by_mass(mass, mu, price, pu))
                else:
                    print("Invalid choice.")
        except Exception as e:
            print(f"Error: {e}")

# -----------------------------------------------------------------------------
# 8. Demo / Unit Tests (run with `python calculations_suite.py`)
# -----------------------------------------------------------------------------

def run_demo():
    print("=== Calculation Suite Demonstration ===\n")
    suite = ConversionSuite()
    # Example 1: 10 m³ of dry sand -> metric tonnes
    suite.select_material("sand_dry_loose")
    vol_m3 = 10.0
    mass_t = suite.volume_to_mass(vol_m3, "m³", "t")
    print(f"Example 1: {vol_m3} m³ of dry loose sand = {mass_t:.2f} tonnes")
    # Example 2: Convert 20 metric tonnes of compacted gravel to cubic yards
    suite.select_material("gravel_compacted")
    mass_t2 = 20.0
    vol_yd3 = suite.mass_to_volume(mass_t2, "t", "yd³")
    print(f"Example 2: {mass_t2} t of compacted gravel = {vol_yd3:.2f} yd³")
    # Example 3: With moisture correction (5% water content adding weight)
    suite.select_material("sand_dry_loose", moisture_factor=1.05)
    mass_t_wet = suite.volume_to_mass(10, "m³", "t")
    print(f"Example 3: 10 m³ sand with +5% moisture = {mass_t_wet:.2f} t (vs. {mass_t:.2f} t dry)")
    # Example 4: Cost estimation – price per ton
    suite.select_material("concrete")
    cost = suite.estimate_cost_by_mass(50, "t", 120.0, "t", "$")
    print(f"Example 4: 50 t of concrete at $120/t => {cost}")
    # Example 5: Convert 1 m³ of water to long tons (imperial)
    suite.select_material("water")
    water_lt = suite.volume_to_mass(1, "m³", "lt")
    print(f"Example 5: 1 m³ water = {water_lt:.4f} long tons")
    # Example 6: 500 US gallons of diesel to short tons
    suite.select_material("diesel")
    diesel_st = suite.volume_to_mass(500, "gal(US)", "st")
    print(f"Example 6: 500 US gal diesel = {diesel_st:.2f} short tons")

def run_tests():
    """Minimal test suite using assertions."""
    suite = ConversionSuite()
    suite.select_material("water")
    assert abs(suite.volume_to_mass(1, "m³", "t") - 1.0) < 1e-6
    assert abs(suite.mass_to_volume(1000, "kg", "m³") - 1.0) < 1e-6
    suite.select_material("concrete")
    # 1 m³ concrete approx 2.4 t
    mass = suite.volume_to_mass(1, "m³", "t")
    assert 2.3 < mass < 2.5
    vol = suite.mass_to_volume(2400, "kg", "m³")
    assert abs(vol - 1.0) < 0.05
    # Test with corrections
    suite.select_material("sand_dry_loose", moisture_factor=1.1)
    dry_mass = 10 * 1442 / 1000  # approximate
    wet_mass = suite.volume_to_mass(10, "m³", "t")
    assert wet_mass > dry_mass
    print("All basic tests passed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        interactive_cli()
