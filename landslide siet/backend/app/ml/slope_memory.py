def update_slope_memory(previous_stress: float, current_stress: float, decay: float = 0.9) -> float:
    if previous_stress < 0 or current_stress < 0:
        raise ValueError("stress values must be nonnegative")
    if not 0 <= decay <= 1:
        raise ValueError("decay must be between 0 and 1")
    return previous_stress * decay + current_stress