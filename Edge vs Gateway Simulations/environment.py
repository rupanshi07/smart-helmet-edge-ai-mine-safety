"""
environment.py

Environment models for realistic underground/construction LoRa simulation.

Provides:
- path_loss_model: path loss (dB) given distance and environment
- apply_nlos_penalty: extra loss for NLOS / corner
- tunnel_fading: fast fading sample (dB)
- noise_floor_model: dynamic noise floor (dBm)
- rssi_from_tx: compute Rx RSSI given Tx power and losses
- snr_from_rssi: compute SNR given RSSI and noise_floor
- per_from_snr: maps (SF, SNR) -> packet error rate (empirical)
- capture_effect_winner: resolves collisions by RSSI difference
- position_generator: simple placement helper for tunnel/junction assignment
- multi_hop_penalty: returns per-hop extra delay/airtime penalty
- utility constants: SF list, BW, etc.

License: lightweight for research/edu. Use & adapt freely.
"""

import math
import numpy as np
import random
from typing import Tuple, Dict

# -----------------------------
# Constants & defaults
# -----------------------------
SFS = [7, 8, 9, 10, 11, 12]
BW = 125e3  # Hz
TX_POWERS_DBM = [2, 7, 10, 14]  # allowed TX power bins we may simulate
FREQ_HZ = 433e6  # default frequency (change as needed)

# Baseline parameters
PL_D0 = 30.0       # path loss at reference distance d0 (dB) -- tune per environment
D0 = 1.0           # reference distance (meters)
# Typical underground path-loss exponent ranges:
PL_EXP_TUNNEL_LOS = 1.4
PL_EXP_TUNNEL_NLOS = 2.6

# Corner/NLOS penalties (dB)
CORNER_LOSS_DB = 20.0
NLOS_PENALTY_DB = 15.0

# Rock absorption typical range (dB additional loss)
ROCK_ABSORPTION = {
    'sandstone': 10.0,
    'limestone': 16.0,
    'basalt': 25.0,
    'concrete': 18.0,
    'mixed': 14.0
}

# Fast fading (multipath) stddev (dB)
TUNNEL_FADING_STD_DB = 4.0

# Noise floor baseline (dBm)
NOISE_BASE_DBM = -110.0

# Capture threshold (dB) - if difference > threshold, stronger wins
CAPTURE_THRESHOLD_DB = 6.0

# SNR -> PER empirical table per SF (toy but realistic-ish curve)
# The table maps SNR(dB) thresholds to approximate PER. You can refine with measurements.
# Format: list of (snr_threshold, per) ascending thresholds for a given SF.
SNR_PER_TABLE = {
    7: [(-20, 1.0), (-10, 0.9), (-6, 0.5), (-2, 0.2), (0, 0.05), (5, 0.01), (10, 0.001)],
    8: [(-22,1.0), (-12,0.9), (-8,0.5), (-4,0.2), (-1,0.05), (4,0.01), (9,0.001)],
    9: [(-24,1.0), (-14,0.9), (-10,0.5), (-5,0.2), (-2,0.05), (3,0.01), (8,0.001)],
    10:[(-26,1.0), (-16,0.9), (-12,0.5), (-6,0.2), (-3,0.05), (2,0.01), (7,0.001)],
    11:[(-28,1.0), (-18,0.9), (-14,0.5), (-7,0.2), (-4,0.05), (1,0.01), (6,0.001)],
    12:[(-30,1.0), (-20,0.9), (-16,0.5), (-8,0.2), (-5,0.05), (0,0.01), (5,0.001)]
}

# -----------------------------
# Core functions
# -----------------------------


def path_loss(d_m: float, env: str = 'tunnel_los') -> float:
    """
    Path loss in dB for distance d_m and environment type.
    env can be: 'tunnel_los', 'tunnel_nlos', 'indoor', 'open'
    Return: path loss in dB (positive number)
    """
    if d_m < D0:
        d_m = D0
    if env == 'tunnel_los':
        n = PL_EXP_TUNNEL_LOS
    elif env == 'tunnel_nlos':
        n = PL_EXP_TUNNEL_NLOS
    elif env == 'indoor':
        n = 3.0
    elif env == 'open':
        n = 2.0
    else:
        n = 3.0
    pl = PL_D0 + 10.0 * n * math.log10(d_m / D0)
    return pl


def apply_rock_absorption(pl_db: float, rock_type: str = 'mixed') -> float:
    """
    Add rock absorption penalty to path loss.
    """
    extra = ROCK_ABSORPTION.get(rock_type, ROCK_ABSORPTION['mixed'])
    return pl_db + extra


def apply_nlos_penalty(pl_db: float, is_corner: bool = False) -> float:
    """
    Apply NLOS/corner penalty to path loss.
    """
    if is_corner:
        return pl_db + CORNER_LOSS_DB
    else:
        return pl_db + NLOS_PENALTY_DB


def tunnel_fading() -> float:
    """
    Sample fast fading term (dB) for multipath in tunnel.
    """
    return float(np.random.normal(0.0, TUNNEL_FADING_STD_DB))


def noise_floor_model(dynamic_variation_db: float = 0.0) -> float:
    """
    Return instantaneous noise floor in dBm. dynamic_variation_db can be
    positive (more noise) or negative; it can be time varying in sim.
    """
    return NOISE_BASE_DBM + dynamic_variation_db


def rssi_from_tx(tx_power_dbm: float,
                 distance_m: float,
                 env: str = 'tunnel_los',
                 rock: str = 'mixed',
                 is_corner: bool = False,
                 fading: float = None,
                 additional_loss_db: float = 0.0) -> float:
    """
    Compute Rx RSSI (dBm) given Tx power and environment factors.
    """
    pl = path_loss(distance_m, env=env)
    pl = apply_rock_absorption(pl, rock)
    if env.endswith('nlos') or is_corner:
        pl = apply_nlos_penalty(pl, is_corner=is_corner)
    if fading is None:
        fading = tunnel_fading()
    rssi = tx_power_dbm - (pl + fading + additional_loss_db)
    return rssi


def snr_from_rssi(rssi_dbm: float, noise_floor_dbm: float) -> float:
    """
    Simple SNR in dB = RSSI - NoiseFloor
    """
    return rssi_dbm - noise_floor_dbm


def per_from_snr(sf: int, snr_db: float) -> float:
    """
    Empirical mapping SNR->PER for given SF using SNR_PER_TABLE.
    Returns PER between 0 and 1.
    """
    table = SNR_PER_TABLE.get(sf, SNR_PER_TABLE[12])
    # if below first threshold -> return its PER
    for thr, per in table:
        if snr_db <= thr:
            return per
    # if above last threshold -> return tiny per
    return table[-1][1]


def capture_effect_winner(rssi_list: Dict[int, float]) -> Tuple[bool, int]:
    """
    Given dict node_id->rssi for colliding packets, apply capture effect.
    Returns (success_flag, winner_node_id or -1 if none).
    Rule: if strongest - second_strongest >= CAPTURE_THRESHOLD_DB => strongest wins (others lost)
    else -> all lost
    """
    if not rssi_list:
        return False, -1
    items = sorted(rssi_list.items(), key=lambda x: x[1], reverse=True)
    if len(items) == 1:
        return True, items[0][0]
    best_id, best_rssi = items[0]
    second_id, second_rssi = items[1]
    if (best_rssi - second_rssi) >= CAPTURE_THRESHOLD_DB:
        return True, best_id
    else:
        return False, -1


def multi_hop_penalty(hops: int = 0, per_hop_processing_s: float = 0.05) -> float:
    """
    Extra per-packet latency due to multi-hop repeaters (seconds).
    per_hop_processing_s ~ processing + queue time at repeater.
    """
    return hops * per_hop_processing_s


# -----------------------------
# Helper utilities for placement + random scenarios
# -----------------------------
def position_generator(num_nodes: int,
                       layout: str = 'linear_tunnel',
                       length_m: float = 1000.0,
                       junctions: int = 0) -> Dict[int, Dict]:
    """
    Generate simple positions and environment tags for nodes.
    Returns dict: node_id -> {distance_m, env, rock, is_corner, hops}
    layout: 'linear_tunnel', 'branching_tunnel', 'open_site'
    """
    nodes = {}
    if layout == 'linear_tunnel':
        # spread nodes uniformly along tunnel length
        for i in range(num_nodes):
            d = random.uniform(5.0, length_m - 5.0)
            # determine if near corner by small probability
            is_corner = random.random() < 0.15
            env = 'tunnel_los' if random.random() < 0.7 and not is_corner else 'tunnel_nlos'
            rock = random.choice(list(ROCK_ABSORPTION.keys()))
            hops = 0  # default; later you can set repeaters
            nodes[i] = {'distance_m': d, 'env': env, 'rock': rock, 'is_corner': is_corner, 'hops': hops}
    elif layout == 'branching_tunnel':
        for i in range(num_nodes):
            branch = random.choice(range(max(2, junctions+1)))
            d = random.uniform(5.0, length_m/ (branch+1))
            is_corner = random.random() < 0.25
            env = 'tunnel_nlos' if is_corner or random.random() < 0.4 else 'tunnel_los'
            rock = random.choice(list(ROCK_ABSORPTION.keys()))
            hops = random.randint(0, 2)
            nodes[i] = {'distance_m': d + branch* (length_m/4.0), 'env': env, 'rock': rock, 'is_corner': is_corner, 'hops': hops}
    else:  # open_site
        for i in range(num_nodes):
            d = random.uniform(5.0, length_m/2.0)
            env = 'open'
            rock = 'mixed'
            is_corner = False
            hops = 0
            nodes[i] = {'distance_m': d, 'env': env, 'rock': rock, 'is_corner': is_corner, 'hops': hops}
    return nodes


# -----------------------------
# Example convenience function used by sims
# -----------------------------

def evaluate_link(tx_power_dbm: float,
                  distance_m: float,
                  sf: int,
                  layout_meta: Dict,
                  noise_var_db: float = 0.0,
                  extra_loss_db: float = 0.0) -> Dict:
    """
    Evaluate a link and return dictionary with:
    - rssi_dbm
    - noise_dbm
    - snr_db
    - per (packet error rate)
    - expected_success_prob (1-per)
    - recommended_sf (if you want a heuristic)
    """
    env = layout_meta.get('env', 'tunnel_los')
    rock = layout_meta.get('rock', 'mixed')
    is_corner = layout_meta.get('is_corner', False)
    hops = layout_meta.get('hops', 0)
    noise_dbm = noise_floor_model(dynamic_variation_db=noise_var_db)
    rssi_dbm = rssi_from_tx(tx_power_dbm, distance_m, env=env, rock=rock, is_corner=is_corner, additional_loss_db=extra_loss_db)
    snr_db = snr_from_rssi(rssi_dbm, noise_dbm)
    per = per_from_snr(sf, snr_db)
    success = max(0.0, 1.0 - per)
    penalties = multi_hop_penalty(hops)
    return {
        'rssi_dbm': rssi_dbm,
        'noise_dbm': noise_dbm,
        'snr_db': snr_db,
        'per': per,
        'success_prob': success,
        'multi_hop_penalty_s': penalties
    }


# -----------------------------
# If run as script: quick demo
# -----------------------------
if __name__ == "__main__":
    print("environment.py demo")
    nodes = position_generator(8, layout='linear_tunnel', length_m=400.0)
    for nid, meta in nodes.items():
        link = evaluate_link(tx_power_dbm=14.0, distance_m=meta['distance_m'], sf=9, layout_meta=meta, noise_var_db=random.uniform(-2, 6))
        print(f"Node {nid}: d={meta['distance_m']:.1f}m env={meta['env']} rock={meta['rock']} corner={meta['is_corner']} -> RSSI={link['rssi_dbm']:.1f} dBm, SNR={link['snr_db']:.1f} dB, PER={link['per']:.3f}")
