from skidl import *

set_default_tool(KICAD8)

vcc_12v = Net('12V')
vcc_5v  = Net('5V')
vcc_3v3 = Net('3V3')
gnd     = Net('GND')

# --- Power Section with Fallbacks ---
try:
    # Try the most common modern name first
    reg_5v = Part('Regulator_Linear', 'LM7805_TO220', footprint='Package_TO_SOT_THT:TO-220-3_Vertical')
except:
    try:
        # Try the base name
        reg_5v = Part('Regulator_Linear', 'LM7805', footprint='Package_TO_SOT_THT:TO-220-3_Vertical')
    except:
        # Generic fallback
        reg_5v = Part('Regulator_Linear', 'L7805', footprint='Package_TO_SOT_THT:TO-220-3_Vertical')

reg_5v[1, 2, 3] += vcc_12v, gnd, vcc_5v

try:
    reg_3v3 = Part('Regulator_Linear', 'AMS1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
except:
    # Some libraries use LM1117
    reg_3v3 = Part('Regulator_Linear', 'LM1117-3.3', footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')

reg_3v3[1, 2, 3] += gnd, vcc_3v3, vcc_5v

# --- Connector Section (Verified by your previous grep) ---
controller_hdr = Part('Connector', 'Conn_01x40_Pin', footprint='Connector_PinHeader_2.54mm:PinHeader_1x40_P2.54mm_Vertical')
controller_hdr[2, 4] += vcc_5v
controller_hdr[6, 9, 14, 20, 25, 30, 34, 39] += gnd

sdr_conn = Part('Connector', 'Conn_01x20_Pin', footprint='Connector_PinHeader_2.54mm:PinHeader_1x20_P2.54mm_Vertical')
sdr_conn[1] += vcc_3v3
sdr_conn[2] += gnd

# --- Signals ---
controller_hdr[19] += sdr_conn[3]  # MOSI
controller_hdr[21] += sdr_conn[4]  # MISO

# --- Capacitors ---
for i in range(5):
    # 'C' is usually in 'Device' or 'Device.kicad_sym'
    cap = Part('Device', 'C', value='100nF', footprint='Capacitor_SMD:C_0805_2012Metric')
    cap[1, 2] += vcc_3v3, gnd

ERC()
generate_netlist(file_='jammer_v4.net')
print("Success! jammer_v4.net generated.")