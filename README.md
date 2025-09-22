# ORC_CO2_100kW

A Python-based steady-state Organic Rankine Cycle (ORC) model using CO₂ as working fluid, designed to deliver 100 kW of net electrical power. This model leverages CoolProp for thermodynamic property calculations.

## Features
- Steady-state ORC simulation: pump → evaporator → turbine → condenser
- Auto-calculates mass flow to meet target net power
- Supercritical and subcritical CO₂ operation with critical temperature checks
- Computes turbine/pump work, net power, thermal efficiency

## Requirements
- Python 3.8+
- [CoolProp](https://github.com/CoolProp/CoolProp)
- NumPy

Install dependencies:
```bash
pip install -r requirements.txt
