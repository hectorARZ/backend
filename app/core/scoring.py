import Levenshtein
import unicodedata

def sin_acentos(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def calcular_calificacion(intento: str, correcta: str, umbral_minimo: int = 70):
    intento = intento.strip().lower()
    correcta = correcta.strip().lower()
    
    if intento == correcta:
        return 100
    
    if sin_acentos(intento) == sin_acentos(correcta):
        return 85
    
    distancia = Levenshtein.distance(intento, correcta)
    max_len = max(len(intento), len(correcta))
    puntaje = ((max_len - distancia) / max_len) * 100
    
    if puntaje < umbral_minimo:
        return 0

    return round(puntaje, 2)