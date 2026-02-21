def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def blended_score(oop_total: float, cpp_blended: float, friction: float, w1=0.5, w2=0.35, w3=0.15) -> float:
    # Simple normalized placeholder for MVP scaffolding.
    oop_term = -oop_total / 5000.0
    cpp_term = clamp(cpp_blended, 0.0, 5.0) / 5.0
    friction_term = -friction / 10.0
    return w1 * oop_term + w2 * cpp_term + w3 * friction_term
