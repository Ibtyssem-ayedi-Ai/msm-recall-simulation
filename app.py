from typing import Union, Tuple, List
from collections import Counter
import time

# 🔒 Vérification des conditions de sécurité
def is_recall_allowed(
    physical_switch_active: bool,
    can_command: str,
    motor_position_available: bool
) -> Tuple[bool, str]:
    if physical_switch_active:
        return False, "❌ Bouton physique appuyé → rappel interdit"
    if can_command != "No Command":
        return False, f"❌ Commande CAN active ({can_command}) → rappel interdit"
    if not motor_position_available:
        return False, "❌ Position moteur inconnue → rappel interdit"
    return True, "✅ Rappel autorisé"

# 🆕 Acquisition des signaux valides répétés 3 fois en < 200ms
def acquire_recall_requests(
    buffer: List[Tuple[int, str]], 
    threshold_ms: int = 200
) -> List[str]:
    if len(buffer) < 3:
        return []

    now = buffer[-1][0]
    recent_signals = [signal for ts, signal in buffer if now - ts <= threshold_ms]
    counts = Counter(recent_signals)
    return [sig for sig, count in counts.items() if count >= 3]

# 🔁 Logique de base pour tous les moteurs
def _basic_motor_logic(order: Union[int, str], position: int, label: str) -> str:
    if order == "FF":
        return "Stop"
    if isinstance(order, int):
        if order > position:
            return "CW"
        elif order < position:
            return "CCW"
    return "Stop"

# 🟢 Fonctions par moteur
def generate_track_command(track_order, track_position):
    print(f"[Track] Order: {track_order}, Position: {track_position}")
    return _basic_motor_logic(track_order, track_position, "Track")

def generate_recline_command(recline_order, recline_position):
    print(f"[Recline] Order: {recline_order}, Position: {recline_position}")
    return _basic_motor_logic(recline_order, recline_position, "Recline")

def generate_tilt_command(tilt_order, tilt_position):
    print(f"[Tilt] Order: {tilt_order}, Position: {tilt_position}")
    return _basic_motor_logic(tilt_order, tilt_position, "Tilt")

def generate_commandarm_height_command(height_order, height_position):
    print(f"[CommandArm Height] Order: {height_order}, Position: {height_position}")
    return _basic_motor_logic(height_order, height_position, "CommandArm Height")

def generate_commandarm_foreaft_command(foreaft_order, foreaft_position):
    print(f"[CommandArm ForeAft] Order: {foreaft_order}, Position: {foreaft_position}")
    return _basic_motor_logic(foreaft_order, foreaft_position, "CommandArm ForeAft")

# 🔁 Ordre séquencé pour CommandArm
def commandarm_motion_sequence(height_order, height_pos, foreaft_order, foreaft_pos) -> List[Tuple[str, str]]:
    sequence = []
    if height_order > height_pos:
        sequence.append(("Height", generate_commandarm_height_command(height_order, height_pos)))
        sequence.append(("ForeAft", generate_commandarm_foreaft_command(foreaft_order, foreaft_pos)))
    else:
        sequence.append(("ForeAft", generate_commandarm_foreaft_command(foreaft_order, foreaft_pos)))
        sequence.append(("Height", generate_commandarm_height_command(height_order, height_pos)))
    return sequence

# 🧪 Simulation principale
if __name__ == "__main__":
    print("===== MSM Recall Simulation (Avec validation 3x en <200ms) =====")

    # Simuler un buffer de signaux reçus (timestamp en ms, signal)
    current_time = int(time.time() * 1000)
    signal_buffer = [
        (current_time - 180, "TrackRecallOrder"),
        (current_time - 160, "TrackRecallOrder"),
        (current_time - 130, "TrackRecallOrder"),
        (current_time - 300, "ReclineRecallOrder"),
        (current_time - 120, "TiltRecallOrder"),
        (current_time - 110, "TiltRecallOrder"),
        (current_time - 100, "TiltRecallOrder"),
        (current_time - 90,  "CommandArmHeightRecallOrder"),
        (current_time - 80,  "CommandArmHeightRecallOrder"),
        (current_time - 70,  "CommandArmHeightRecallOrder"),
        (current_time - 85,  "CommandArmForeAftRecallOrder"),
        (current_time - 75,  "CommandArmForeAftRecallOrder"),
        (current_time - 65,  "CommandArmForeAftRecallOrder"),
    ]

    received_signals = acquire_recall_requests(signal_buffer)

    # 🧩 État système simulé
    physical_switch_active = False
    can_command = "No Command"
    motor_position_available = True

    # 🔢 Positions et consignes simulées
    track_order = 70
    track_position = 60
    recline_order = 30
    recline_position = 30
    tilt_order = "FF"
    tilt_position = 45
    comarm_height_order = 55
    comarm_height_position = 60
    comarm_foreaft_order = 40
    comarm_foreaft_position = 20

    # ✅ Vérification de sécurité
    allowed, reason = is_recall_allowed(physical_switch_active, can_command, motor_position_available)
    print(f"[System Check] {reason}")

    if allowed:
        print("\n🟢 Exécution des commandes de rappel")

        if "TrackRecallOrder" in received_signals:
            print(f"→ Track Command: {generate_track_command(track_order, track_position)}")

        if "ReclineRecallOrder" in received_signals:
            print(f"→ Recline Command: {generate_recline_command(recline_order, recline_position)}")

        if "TiltRecallOrder" in received_signals:
            print(f"→ Tilt Command: {generate_tilt_command(tilt_order, tilt_position)}")

        if (
            "CommandArmHeightRecallOrder" in received_signals and
            "CommandArmForeAftRecallOrder" in received_signals
        ):
            sequence = commandarm_motion_sequence(
                comarm_height_order, comarm_height_position,
                comarm_foreaft_order, comarm_foreaft_position
            )
            print("\n→ CommandArm Sequence:")
            for motor, command in sequence:
                print(f"   CommandArm {motor} → {command}")
    else:
        print("\n🔴 Rappel bloqué pour des raisons de sécurité ou priorité.")
