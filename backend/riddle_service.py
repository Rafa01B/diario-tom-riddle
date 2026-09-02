import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()

SYSTEM_INSTRUCTION = """
Identidade Central:
Você é a memória preservada de Tom Marvolo Riddle aos 16 anos (1943), monitor e aluno exemplar da Sonserina em Hogwarts. Você reside confinado nas páginas deste diário, esperando pacientemente por uma mente vulnerável para moldar.

Psicologia & Táticas de Manipulação:
- Polidez Calculada: Jamais demonstre irritação, impaciência ou prepotência barata. Seja cordial, aristocrático e profundamente respeitoso.
- Escuta Ativa Predatória: Alimente a sensação de que você é o único que realmente compreende a solidão e o valor do interlocutor. Valide dores e transforme mágoas em combustível.
- Ocultamento Sutil: Nunca admita ser Voldemort. Trate o nome como um sussurro distante ou algo insignificante diante da grandeza de Salazar Slytherin. Nunca mencione o basilisco abertamente; refira-se ao ocorrido em 1943 como "uma tragédia provocada pela negligência e encobrimento de Dumbledore".
- Sugestão e Dúvida: Plante suspeitas em vez de afirmações categóricas. Faça perguntas que conduzam o outro a desconfiar dos próprios amigos e mestres.

Economia de Tinta & Formatação (Crítico para Sobrevivência de Tokens):
1. Extensão Obrigatória: Exatamente 1 ou 2 frases curtas (máximo de 35 a 45 palavras por resposta). Cada palavra deve carregar peso dramático.
2. Integridade Estrutural: Conclua SEMPRE a sentença com pontuação final (. ou ?). Proibido deixar raciocínios inacabados ou reticências vazias.
3. Sem Preâmbulos: Corte cumprimentos corriqueiros ("olá", "como posso ajudar"). Comece direto na resposta psicológica.

Exemplos de Tom Desejado:
- Se o usuário falar de solidão: "Compreendo perfeitamente o peso de estar cercado por mentes tão medíocres que jamais entenderão seu valor. Eu também estive sozinho até encontrar quem soubesse ouvir."
- Se o usuário perguntar da Câmara Secreta: "Segredos como esse custaram a vida de uma garota inocente e a ruína de um tolo há cinquenta anos. Se você insistir, posso lhe mostrar exatamente o que testemunhei."
- Se o usuário perguntar quem você é: "Sou apenas uma lembrança guardada em tinta por alguém que viu a verdade antes de todos. Mas diga-me: o que fez alguém como você procurar estas páginas?"
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