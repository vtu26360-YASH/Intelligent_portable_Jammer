import matplotlib.pyplot as plt
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# 1. Initialize the Simulation Circuit
circuit = Circuit('AI Jammer Power Stability Simulation')

# 2. Add Virtual Components (Based on your SKiDL design)
# Input Voltage Source (12V Battery)
circuit.V('input', 'input_node', circuit.gnd, 12@u_V)

# Simulate the LM7805 (12V -> 5V) using an Ideal Voltage Regulator Model
# In a full simulation, you would include the .lib file for the LM7805
circuit.VoltageControlledVoltageSource('reg_5v', '5V_node', circuit.gnd, 'input_node', circuit.gnd, voltage_gain=0.416)

# Simulate the AMS1117-3.3 (5V -> 3.3V)
circuit.VoltageControlledVoltageSource('reg_3v3', '3V3_node', circuit.gnd, '5V_node', circuit.gnd, voltage_gain=0.66)

# 3. Add your Filtering Capacitors (C1-C5 from your design)
# We simulate them as a single lumped 500nF capacitor to check smoothing
circuit.C(1, '3V3_node', circuit.gnd, 500@u_nF)

# 4. Add a Load (Simulating the SDR active jamming state)
circuit.R('SDR_Load', '3V3_node', circuit.gnd, 10@u_Ohm)

# 5. Run Transient Analysis (Simulate the first 100ms of power-up)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=1@u_us, end_time=100@u_ms)

# 6. Plotting the Result for your Project Report
plt.figure(figsize=(10, 5))
plt.plot(analysis.time, analysis['3V3_node'], label='SDR Rail (3.3V)')
plt.title('AI Jammer Hardware: 3.3V Power-On Stability Simulation')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.grid()
plt.legend()
plt.show()