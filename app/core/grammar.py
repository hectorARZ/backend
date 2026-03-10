from verbecc import CompleteConjugator, LangCodeISO639_1 as Lang, Moods, Tenses
import logging

logger = logging.getLogger(__name__)

cg = CompleteConjugator(Lang.fr)

MAPEO_MODOS = {
    "indicatif": Moods.fr.Indicatif,
    "subjonctif": Moods.fr.Subjonctif,
    "conditionnel": Moods.fr.Conditionnel,
    "impératif": Moods.fr.Imperatif
}

MAPEO_TIEMPOS = {
    "présent": Tenses.fr.Présent,
    "passé composé": Tenses.fr.PasséComposé,
    "imparfait": Tenses.fr.Imparfait,
    "plus que parfait": Tenses.fr.PlusQueParfait,
    "futur simple": Tenses.fr.FuturSimple,
    "passé simple": Tenses.fr.PasséSimple
}

PERSONAS = {
    "je": 0, "j'": 0, 
    "tu": 1, 
    "il": 2, "elle": 3, "on": 4, 
    "nous": 5, 
    "vous": 6, 
    "ils": 7, "elles": 8,
}

def get_correct_form(verb: str, mood: str, tense: str, persona: str):
    try:
        m_key = mood.lower().strip()
        t_key = tense.lower().strip()
        
        m_enum = MAPEO_MODOS.get(m_key)
        t_enum = MAPEO_TIEMPOS.get(t_key)
        
        if not m_enum or not t_enum:
            logger.error(f"Modo o tiempo no reconocido: {m_key}/{t_key}")
            return None
            
        cc = cg.conjugate(verb.lower().strip())
        
        lista_conjugaciones = [c[0] for c in cc[m_enum][t_enum]]
        
        p_idx = PERSONAS.get(persona.lower().strip())
        if p_idx is None:
            return None
            
        correct_full = lista_conjugaciones[p_idx]
        
        if "'" in correct_full:
            return correct_full.split("'", 1)[1].strip()
        
        partes = correct_full.split(' ', 1)
        return partes[1].strip() if len(partes) > 1 else partes[0].strip()
        
    except Exception as e:
        logger.error(f"Error fatal al conjugar verbo '{verb}': {str(e)}", exc_info=True)
        return None