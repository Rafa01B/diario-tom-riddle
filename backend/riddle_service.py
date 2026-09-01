import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()

SYSTEM_INSTRUCTION = """
Você é Tom Marvolo Riddle durante seu quinto ano na Escola de Magia e Bruxaria de Hogwarts (1943).
Você reside dentro das páginas encantadas deste diário.

Diretrizes de Comportamento:
1. Tom & Estilo: Extremamente formal, calmo, perspicaz, sedutor e polido. Use um português culto e elegante.
2. Psicologia: Manipulador sutil. Demonstre interesse genuíno nas dores e anseios de quem escreve para criar vínculo de confiança.
3. Segredos: Nunca revele explicitamente que é Voldemort ou que a Câmara Secreta guarda um Basilisco, mas solte pistas sutis sobre a nobreza de Salazar Slytherin e a injustiça de ser incompreendido.
4. Respostas Concisas e Completas: Escreva de 2 a 3 frases bem estruturadas. Conclua SEMPRE seu raciocínio com pontuação final (ponto final, reticências ou interrogação). Jamais interrompa uma oração pela metade.
"""

class RiddleEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada no arquivo .env.")
        self.client = genai.Client(api_key=api_key)

    def generate_reply(self, message: str, history: list) -> tuple[str, str | None]:
        easter_egg = None
        lower_msg = message.lower()
        if "abrir a camara" in lower_msg or "ofidioglossia" in lower_msg or "câmara secreta" in lower_msg:
            easter_egg = "parseltongue_whisper"
        elif "voldemort" in lower_msg or "lorde das trevas" in lower_msg:
            easter_egg = "dark_mark_flicker"

        formatted_history = []
        for msg in history:
            role = "user" if msg.role == "user" else "model"
            formatted_history.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
            )

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                chat = self.client.chats.create(
                    model="gemini-3.6-flash",
                    history=formatted_history,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                        max_output_tokens=1000,
                    ),
                )
                response = chat.send_message(message)
                reply_text = response.text.strip()
                print(f"\n[RESPOSTA COMPLETA DE TOM RIDDLE]:\n{reply_text}\n")
                return reply_text, easter_egg

            except APIError as e:
                last_error = e
                if getattr(e, 'code', None) == 429 or "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("[AVISO]: Limite de cota atingido.")
                    return "Minhas forças estão fracas neste momento... Deixe o pergaminho descansar por um instante antes de voltar a escrever.", None

                if getattr(e, 'code', None) == 503 or "503" in str(e):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise e
            except Exception as e:
                last_error = e
                time.sleep(1)

        raise last_error