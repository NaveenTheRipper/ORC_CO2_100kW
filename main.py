# =============================================================================
# ORC_CO2_100kW.py
# Steady-state CO₂ Organic Rankine Cycle (ORC) simulation targeting 100 kW
# Computes turbine/pump work, thermal efficiency, and required mass flow
# Uses CoolProp for thermodynamic properties
#
# Copyright 2025 Naveen Ranasinghe
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import CoolProp.CoolProp as CP

# --- User inputs ---
fluid = 'CO2'                 # working fluid
T_source = 34 + 273.15       # geothermal/heat source temperature [K]
T_sink   = 10 + 273.15         # seawater sink temperature [K]
T_evap_superheat = 1.5          # superheat [K]
T_cond_subcool = 3          # subcooling [K]
pinch_evap = 5                # pinch in evaporator [K]
pinch_cond = 5                # pinch in condenser [K]
eta_turbine = 0.80            # turbine isentropic efficiency
eta_pump = 0.75               # pump isentropic efficiency
gen_eff = 0.96                # generator + gearbox efficiency
P_target = 100e3              # target net power [W]

# --- Critical temperature check ---
T_crit = CP.PropsSI('Tcrit', fluid)
T_evap = min(T_source - pinch_evap, T_crit - 1.0)   # ensure T_evap < T_crit
if T_source - pinch_evap > T_crit:
    print(f"Warning: Evap temperature exceeds critical temperature. Clipped to {T_evap:.2f} K")

T_cond = T_sink + pinch_cond  # condensing temperature

# --- Saturation pressures ---
P_evap = CP.PropsSI('P','T',T_evap,'Q',1,fluid)   # evap pressure [Pa]
P_cond = CP.PropsSI('P','T',T_cond,'Q',0,fluid)   # cond pressure [Pa]

# --- State 1: liquid leaving condenser (subcooled) ---
T1 = T_cond - T_cond_subcool
h1 = CP.PropsSI('H','T',T1,'P',P_cond,fluid)
s1 = CP.PropsSI('S','T',T1,'P',P_cond,fluid)

# --- Pump (1 -> 2) ---
s2s = s1
h2s = CP.PropsSI('H','P',P_evap,'S',s2s,fluid)
wp_isentropic = h2s - h1
wp_actual = wp_isentropic / eta_pump
h2 = h1 + wp_actual
T2 = CP.PropsSI('T','P',P_evap,'H',h2,fluid)
s2 = CP.PropsSI('S','P',P_evap,'H',h2,fluid)

# --- Evaporator (2 -> 3) ---
T3 = T_evap + T_evap_superheat
if T3 >= T_crit:
    T3 = T_crit - 0.1
    print(f"Warning: Superheated evaporator temp clipped to {T3:.2f} K")
h3 = CP.PropsSI('H','T',T3,'P',P_evap,fluid)
s3 = CP.PropsSI('S','T',T3,'P',P_evap,fluid)

# --- Turbine (3 -> 4) ---
s4s = s3
h4s = CP.PropsSI('H','P',P_cond,'S',s4s,fluid)
h4 = h3 - eta_turbine * (h3 - h4s)
T4 = CP.PropsSI('T','P',P_cond,'H',h4,fluid)
s4 = CP.PropsSI('S','P',P_cond,'H',h4,fluid)

# --- Heat duties ---
q_in = h3 - h2       # J/kg
q_out = h4 - h1      # J/kg

# --- Power/performance ---
W_turbine_specific = h3 - h4
W_pump_specific = h2 - h1
W_net_specific = W_turbine_specific - W_pump_specific

# Adjust mass flow to meet target net power
mdot_working = P_target / (W_net_specific * gen_eff)

P_net = mdot_working * W_net_specific * gen_eff
Q_in_total = mdot_working * q_in
thermal_efficiency = P_net / Q_in_total

# --- Display results ---
print('--- ORC CO2 100 kW Results ---')
print(f'Working fluid: {fluid}')
print(f'Evap T [K]: {T_evap:.2f}, Cond T [K]: {T_cond:.2f}')
print(f'P_net (electrical) [W]: {P_net:.1f}')
print(f'Thermal efficiency (ORC): {thermal_efficiency*100:.3f} %')
print(f'Turbine specific work [kJ/kg]: {W_turbine_specific/1e3:.3f}')
print(f'Pump specific work [kJ/kg]: {W_pump_specific/1e3:.3f}')
print(f'Mass flow required [kg/s]: {mdot_working:.3f}')

# --- Sanity check ---
if Q_in_total <= 0:
    print("Warning: Computed heat input is non-positive; check temperatures and states.")
