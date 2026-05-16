import time
import random
import xmlrpc.client

# --- CONFIGURATION ---
SERVER_URL = 'http://localhost:8080'
JAMMER_POWER = 0.9  # Increased power for better suppression
SCAN_SPEED = 0.1    # 100ms reaction time
HOP_INTERVAL = 3.0  # How long to stay on target

try:
    radio_api = xmlrpc.client.ServerProxy(SERVER_URL)
    # Test connection immediately
    radio_api.get_samp_rate() 
    print("[SYSTEM] High-speed Link Established.")
except Exception as e:
    print(f"[FATAL] Link Failure: {e}")
    exit()

frequencies = [-400000, -200000, 0, 150000, 350000]

def deploy_countermeasure(target_freq):
    """Executes a surgical strike with zero-latency tuning."""
    # Re-tune and Fire simultaneously (reduces RPC overhead)
    radio_api.set_jammer_freq(target_freq)
    radio_api.set_jammer_amp(JAMMER_POWER)
    print(f"[AI] TARGET NEUTRALIZED: {target_freq/1000} kHz")

print("--- AI COGNITIVE ENGINE: HIGH-PERFORMANCE MODE ---")

last_hop_time = 0

while True:
    try:
        current_time = time.time()

        # 1. FAST SENSING: Check if it's time for a new environmental shift
        if current_time - last_hop_time > HOP_INTERVAL:
            # Simulate Enemy Hops
            enemy_freq = random.choice(frequencies)
            radio_api.set_enemy_freq(enemy_freq)
            
            # 2. INSTANT DETECTION (No more long sleep)
            print(f"\n[SCAN] Threat Detected: {enemy_freq/1000} kHz")
            
            # 3. SURGICAL ACTUATION
            # AI locks and fires in one rapid sequence
            deploy_countermeasure(enemy_freq)
            
            last_hop_time = current_time

        # Smallest possible delay to prevent 100% CPU usage while remaining 'Fast'
        time.sleep(SCAN_SPEED) 
        
    except KeyboardInterrupt:
        print("\n[SYSTEM] Safe Shutdown. Neutralizing Transmissions.")
        radio_api.set_jammer_amp(0.0)
        break
    except Exception as e:
        print(f"[ERROR] Logic Failure: {e}")
        break