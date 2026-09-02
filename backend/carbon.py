"""Cálculo de pegada de carbono por trecho.

Metodologia (simples e defensável para a demo):
  emissão_voo (kg CO2) = distância_gc × fator_desvio × assentos × fator_kg_por_assento_km(tipo)
  emissão_por_passageiro = emissão_voo / passageiros_a_bordo   (ocupação em tempo real)

Quanto mais cheio o voo, menor a emissão por pessoa: o app usa isso para
empurrar o comprador para o assento que "custa" menos carbono.
Fatores aproximados por classe de aeronave (kg CO2 por assento-km), ordem de
grandeza dos calculadores ICAO/DEFRA. Ajuste em FACTORS se quiser refinar.
"""
from __future__ import annotations
import math

DETOUR = 1.08          # rota real é ~8% maior que o grande círculo (prática ICAO)
RFI = 1.9              # índice de forçamento radiativo (opcional, efeitos não-CO2)

FACTORS = [            # (substring do identificador, kg CO2 por assento-km)
    ("concorde", 0.55), ("tu-144", 0.55),
    ("a380", 0.115), ("747", 0.120), ("a340", 0.118), ("dc-10", 0.125), ("md-11", 0.120), ("il-96", 0.130), ("tu-154", 0.150),
    ("a330", 0.098), ("a350", 0.085), ("777", 0.100), ("787", 0.082), ("767", 0.105), ("a300", 0.115), ("a310", 0.110),
    ("a320", 0.088), ("a319", 0.092), ("a321", 0.085), ("737", 0.090), ("757", 0.095), ("md-8", 0.110), ("md-9", 0.105), ("dc-9", 0.120), ("tu-134", 0.150),
    ("fokker 100", 0.098), ("fokker 70", 0.105), ("crj", 0.110), ("erj", 0.110), ("embraer", 0.100), ("bae 146", 0.115), ("avro", 0.115), ("dornier", 0.110),
    ("q series", 0.060), ("dash", 0.060), ("atr", 0.058), ("saab", 0.070), ("turboprop", 0.065), ("cessna", 0.150), ("ultraleicht", 0.030),
]
DEFAULT_FACTOR = 0.100


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p = math.pi / 180
    a = (math.sin((lat2 - lat1) * p / 2) ** 2
         + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def factor_for(identifier: str | None) -> float:
    ident = (identifier or "").lower()
    for key, f in FACTORS:
        if key in ident:
            return f
    return DEFAULT_FACTOR


def emissions(distance_km: float, identifier: str | None, capacity: int, booked: int) -> dict:
    """Devolve emissões do voo e por passageiro, na ocupação atual."""
    seats = max(int(capacity or 0), 1)
    onboard = min(max(int(booked or 0), 1), seats)
    dist = distance_km * DETOUR
    f = factor_for(identifier)
    flight_kg = dist * seats * f
    per_pax = flight_kg / onboard
    # se você comprar, você entra no denominador: emissão marginal por pessoa
    per_pax_if_you_buy = flight_kg / min(onboard + 1, seats)
    return {
        "distance_km": round(distance_km, 1),
        "factor_kg_seat_km": f,
        "flight_kg": round(flight_kg, 1),
        "occupancy": round(onboard / seats, 3),
        "per_pax_kg": round(per_pax, 1),
        "per_pax_kg_after_purchase": round(per_pax_if_you_buy, 1),
        "per_pax_kg_rfi": round(per_pax * RFI, 1),
        "trees_year_equivalent": round(per_pax / 22.0, 1),   # ~22 kg CO2 por árvore/ano
    }


def label(per_pax_kg: float, distance_km: float) -> str:
    """Selo A–E comparando com a mediana esperada para a distância (~0,11 kg/pax-km)."""
    if distance_km <= 0:
        return "C"
    ratio = per_pax_kg / (distance_km * 0.11)
    if ratio < 0.6:
        return "A"
    if ratio < 0.85:
        return "B"
    if ratio < 1.15:
        return "C"
    if ratio < 1.6:
        return "D"
    return "E"
