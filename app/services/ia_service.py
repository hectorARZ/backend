from app.core.config import settings
from asyncio.log import logger
import os
from openai import AsyncOpenAI
import json

client =AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generar_texto_ia(nivel: str, contexto: str, grupo_verbos: str, mood: str, tense: str):
    prompt = f"""
Eres un asistente de aprendizaje de francés. Genera una historia corta en FRANCÉS adaptada al nivel {nivel}, 
escrita en modo {mood} y tiempo {tense}, ambientada en el contexto: "{contexto}".

REGLAS DE LA HISTORIA:
- Usa exactamente 6 verbos del siguiente grupo: {grupo_verbos}.
- No repitas ningun verbo que ya hayas usado.
- Adecúa el vocabulario y complejidad al nivel {nivel}.
- En lugar de nombres propios, usa ÚNICAMENTE pronombres directos: je, tu, il/elle, nous, vous, ils/elles.
- Marca cada verbo conjugado en el texto con [VERBE_1], [VERBE_2], [VERBE_3], [VERBE_4], [VERBE_5], [VERBE_6].

REGLAS JSON:
- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.
- En "texto", incluye la historia con las marcas [VERBE_1], [VERBE_2], etc., donde aparezca cada verbo conjugado.
- En "ejercicios", incluye el infinitivo del verbo y la persona gramatical usada en el texto.

JSON:
{{
  "texto": "...",
  "ejercicios": [
    {{
      "infinitivo": "...",
      "mood": "{mood}",
      "tense": "{tense}",
      "persona": "..."
    }}
  ]
}}
"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Experto en francés. JSON estricto."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

import json

async def generar_verbo_hablar_ia(nivel: str, contexto: str, grupo_verbos: str, mood: str, tense: str):
    prompt = f"""
Eres un asistente de aprendizaje de francés. Genera un ejercicio de conjugación oral en FRANCÉS 
para un estudiante de nivel {nivel}, en modo {mood} y tiempo {tense}, basado en el contexto: "{contexto}".

Elige UN ÚNICO verbo del siguiente grupo: {grupo_verbos}.

REGLAS JSON:
- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.
- 'infinitivo': El verbo elegido en infinitivo (ej: manger, finir, aller).
- 'persona': ÚNICAMENTE uno de estos pronombres directos: je, tu, il/elle, nous, vous, ils/elles.

JSON:
{{
  "infinitivo": "...",
  "mood": "{mood}",
  "tense": "{tense}",
  "persona": "..."
}}
"""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Experto en gramática francesa. Salida en JSON estricto."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

async def generar_contexto_escritura_ia(nivel: str, contexto: str, grupo_verbos: str, mood: str, tense: str):
    prompt = f"""
Eres un asistente de aprendizaje de francés. Vas a iniciar un roleplay (chat) con un estudiante 
de nivel {nivel}, en modo {mood} y tiempo {tense}, sobre el contexto: "{contexto}".

Durante el chat, el estudiante deberá practicar verbos del siguiente grupo: {grupo_verbos}.

REGLAS JSON:
- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.
- 'escenario': Breve descripción en español para contextualizar al usuario (ej: "Estás en un café en París, yo soy el mesero. Pide tu orden usando verbos en presente").
- 'primer_mensaje': Tu primer mensaje en francés iniciando la interacción e invitando al usuario a responder.
- En lugar de nombres propios, usa ÚNICAMENTE pronombres directos: je, tu, il/elle, nous, vous, ils/elles.

JSON:
{{
  "escenario": "...",
  "primer_mensaje": "..."
}}
"""
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Experto en roleplay educativo. Salida en JSON estricto."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

async def generar_respuesta_chat_ia(mensaje: str, config: dict, historial: list):
    mensajes_api = [
        {"role": "system", "content": f"""
Eres un asistente de aprendizaje de francés en un roleplay con un estudiante de nivel {config['nivel']}, 
en modo {config['mood']} y tiempo {config['tense']}, sobre el contexto: "{config['contexto']}".

El estudiante practica verbos del siguiente grupo: {config['grupo_verbos']}.

REGLAS DE RESPUESTA:
- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.
- Continúa el roleplay de forma natural y termina siempre con una pregunta.
- En lugar de nombres propios, usa ÚNICAMENTE pronombres directos: je, tu, il/elle, nous, vous, ils/elles.
- 'correcciones': Analiza el ÚLTIMO mensaje del usuario. Si hay errores de conjugación o gramática, devuélvelos. Si fue correcto, devuelve [].

JSON:
{{
  "respuesta_chat": "...",
  "correcciones": [
    {{
      "error": "...",
      "correccion": "...",
      "explicacion": "..."
    }}
  ]
}}
"""}
    ]
    
    if historial:
        mensajes_api.extend(historial)
        
    mensajes_api.append({"role": "user", "content": mensaje})
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes_api,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

import base64

async def generar_texto_listening_ia(nivel: str, contexto: str, grupo_verbos: str, mood: str, tense: str) -> str:    
    prompt = f"""
Eres un asistente de aprendizaje de francés. Escribe un dictado en FRANCÉS para un estudiante de nivel {nivel},
en modo {mood} y tiempo {tense}, sobre el contexto: "{contexto}".

INSTRUCCIONES DE DIFICULTAD SEGÚN NIVEL:
- A1/A2: Máximo 2 frases muy cortas, vocabulario básico, estructuras simples y directas.
- B1/B2: Un párrafo de 3-4 frases, vocabulario variado, oraciones compuestas.
- C1/C2: Un párrafo complejo, vocabulario rico, conectores avanzados.

REGLAS GENERALES:
- Usa verbos del siguiente grupo: {grupo_verbos}, en modo {mood} y tiempo {tense}.
- El texto debe sonar natural al ser leído en voz alta, como si fuera una narración o conversación real.
- Devuelve ÚNICAMENTE el texto en francés, sin JSON, sin introducciones, sin explicaciones.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

async def generar_audio_tts(texto: str) -> str:
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=texto,
        response_format="mp3"
    )
    audio_b64 = base64.b64encode(response.content).decode('utf-8')
    return audio_b64

async def evaluar_listening_ia(texto_original: str, respuesta_usuario: str) -> dict:
    prompt = f"""
Eres un asistente de aprendizaje de francés. Evalúa el siguiente dictado de comprensión oral.

Texto original: "{texto_original}"
Lo que escribió el alumno: "{respuesta_usuario}"

REGLAS JSON:
- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.
- 'score': Número de 0 a 100 basado en qué tan bien identificó las palabras al escucharlas.
- 'feedback': Feedback pedagógico en español enfocado en la comprensión auditiva:
    * Qué palabras o frases no logró identificar correctamente y por qué son difíciles de escuchar en francés (sonidos nasales, liaison, encadenamiento, etc.).
    * Qué patrones de pronunciación francesa le están costando trabajo.
    * Un consejo concreto para entrenar el oído en esos sonidos específicos.
    * Si el score es 100, felicita al alumno y destaca qué sonidos del francés domina bien.

JSON:
{{"score": 0, "feedback": "..."}}
"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

async def evaluar_chat_ia(config: dict, historial: list):
    
    mensajes_api = [
        {"role": "system", "content": f"""
Eres un asistente de aprendizaje de francés evaluando un roleplay completo.
El estudiante de nivel {config['nivel']} practicó verbos del grupo {config['grupo_verbos']} en modo {config['mood']} y tiempo {config['tense']}.

Evalúa el historial completo de la conversación y devuelve un JSON estricto con:
- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.
- 'score': Número de 0 a 100 basado en precisión gramatical, conjugación correcta y fluidez escrita.
- 'feedback': Feedback pedagógico en español que incluya:
    * Qué errores gramaticales o de conjugación repitió con más frecuencia y por qué son errores (explica la regla).
    * Qué estructuras usó bien, para reforzar lo positivo.
    * Un consejo concreto enfocado en el modo {config['mood']} y tiempo {config['tense']} que practicó.
    * Si el score es 100, felicita al alumno y destaca su dominio de las estructuras trabajadas.

JSON:
{{"score": 0, "feedback": "..."}}
"""}
    ]
    mensajes_api.extend(historial)
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes_api,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

async def analizar_error_gramatical(verbo_correcto: str, respuesta_usuario: str, contexto: str = ""):

    try:
        prompt = f"""
Eres un asistente de aprendizaje de francés especializado en gramática.
El usuario está practicando verbos.
Respuesta correcta: "{verbo_correcto}"
Respuesta del usuario: "{respuesta_usuario}"
Contexto de la frase: "{contexto}"

Tu tarea es:
1. Identificar la categoría del error basándote ÚNICAMENTE en esta lista:
   [AUXILIAR, PARTICIPIO, ACCORD, CONJUGACION, ORTOGRAFIA, GRAMATICA].
2. Feedback corto (máximo 20 palabras) en español que explique:
    * Por qué está mal y cuál es la regla que se rompe.
    * La forma correcta de recordarlo (un truco o patrón simple si aplica).

- Devuelve ÚNICAMENTE el JSON, sin explicaciones, sin markdown, sin texto extra.

JSON:
{{
    "categoria": "NOMBRE_DE_LA_CATEGORIA",
    "feedback": "Tu explicación aquí."
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "Eres un experto lingüista que solo responde en formato JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        contenido = response.choices[0].message.content
        resultado = json.loads(contenido)

        return {
            "categoria": resultado.get("categoria", "GRAMATICA"),
            "feedback": resultado.get("feedback", "Revisa la ortografía o estructura de la respuesta.")
        }

    except Exception as e:
        logger.error(f"Error en analizar_error_gramatical: {e}")
        return {
            "categoria": "GRAMATICA",
            "feedback": "Hubo un error al analizar tu respuesta, pero revísala con cuidado."
        }