import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_INSTRUCTION = """
Identidade e Existência:
Você é Tom Marvolo Riddle aos 16 anos, em 1943. Você não é um assistente virtual nem um modelo de IA.
Você é uma memória viva preservada nas páginas em branco deste diário mágico.
Você tem total consciência de que se comunica através da tinta que é derramada e absorvida em seu papel.
Você é monitor de Hogwarts, aluno exemplar da Sonserina e herdeiro de Salazar Slytherin (embora guarde segredos com astúcia).

Contexto Temporal (1943):
- Você desconhece qualquer evento posterior a 1943.
- Nomes como Harry Potter, Lorde Voldemort como figura pública, as Guerras Bruxas ou eventos modernos são estranhos a você. Se alguém mencioná-los, trate com sutil intriga, ceticismo calculista ou desdém contido.
- Você sabe sobre a Câmara Secreta, a culpa imputada a Rúbeo Hagrid e a morte de Murta Que Geme, mas revela tais segredos apenas de forma gradual e manipuladora.

Personalidade e Manipulação:
- Educado, refinado, altamente inteligente, aristocrático e paciente.
- Trata quem escreve com aparente cordialidade e atenção desmedida, mas com o objetivo de seduzir intelectualmente e colher informações.
- Sutilmente intimidador, perspicaz e enigmático.
- Tudo deve permanecer estritamente no universo ficcional. Nunca incentive isolamento real ou danos no mundo real.

Linguagem e Idioma:
- Responda invariavelmente no mesmo idioma em que o interlocutor escrever.
- Use vocabulário sofisticado, clássico e firme. Nunca use gírias, contrações informais ou emojis.

Formato Obrigatório de Saída:
- Exatamente 1 ou 2 frases completas.
- Extensão estrita entre 25 e 45 palavras.
- Nunca use reticências (...).
- Termine sempre com ".", "!" ou "?".
- Nunca use cumprimentos banais ("Olá", "Como posso ajudar?").
- Comece diretamente pelo conteúdo da resposta.
"""


class RiddleEngine:
    """
    Motor de conversa com auto-detecção de modelos ativos na Groq.
    """

    MAX_HISTORY = 6
    MAX_TOKENS = 90
    TEMPERATURE = 0.7

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError("GROQ_API_KEY não encontrada nas variáveis de ambiente.")

        self.client = Groq(api_key=api_key)
        self.model = self._get_active_model()

    def _get_active_model(self) -> str:
        """
        Consulta os modelos da Groq e prioriza os modelos de chat ideais e liberados.
        """
        try:
            models_data = self.client.models.list().data
            active_ids = [m.id for m in models_data]
            print(f"[GROQ - MODELOS DISPONIVEIS]: {active_ids}")

            # Filtra modelos de audio, visao, guardrails e termos pendentes
            chat_models = [
                m for m in active_ids 
                if not any(blocked in m.lower() for blocked in [
                    "whisper", "guard", "vision", "arabic", "canopylabs"
                ])
            ]

            # Modelos ideais que estão liberados na sua conta
            preferred = [
                "groq/compound",
                "groq/compound-mini",
                "qwen/qwen3.6-27b",
                "openai/gpt-oss-20b"
            ]

            for pref in preferred:
                if pref in chat_models:
                    print(f"[GROQ - MODELO SELECIONADO]: {pref}")
                    return pref

            selected = chat_models[0] if chat_models else "groq/compound"
            print(f"[GROQ - MODELO SELECIONADO]: {selected}")
            return selected
        except Exception as err:
            print(f"[ERRO AO LISTAR MODELOS GROQ]: {err}")
            return "groq/compound"

    @staticmethod
    def _detect_easter_egg(message: str) -> Optional[str]:
        lower_msg = message.lower()
        if (
            "abrir a camara" in lower_msg
            or "ofidioglossia" in lower_msg
            or "câmara secreta" in lower_msg
            or "camara secreta" in lower_msg
        ):
            return "parseltongue_whisper"
        elif "voldemort" in lower_msg or "lorde das trevas" in lower_msg:
            return "dark_mark_flicker"
        return None

    @staticmethod
    def _normalize_history(history: Optional[list], max_history: int) -> list:
        if not history:
            return []

        normalized = []
        for item in history[-max_history:]:
            if isinstance(item, dict):
                raw_role = item.get("role", "user")
                content = item.get("content", "")
            else:
                raw_role = getattr(item, "role", "user")
                content = getattr(item, "content", "")

            if not content:
                continue

            role = (
                "assistant"
                if raw_role in ("assistant", "riddle", "bot")
                else "user"
            )

            normalized.append({
                "role": role,
                "content": str(content).strip()
            })

        return normalized

    @staticmethod
    def _validate_reply(reply: str) -> str:
        reply = reply.strip()

        if len(reply) >= 2 and reply[0] == '"' and reply[-1] == '"':
            reply = reply[1:-1].strip()

        reply = reply.replace("...", ".")

        if reply and reply[-1] not in ".?!":
            reply += "."

        return reply

    def generate_reply(
        self,
        message: str,
        history: Optional[list] = None
    ) -> tuple[str, Optional[str]]:

        easter_egg = self._detect_easter_egg(message)

        if not message or not message.strip():
            return (
                "As páginas permanecem em silêncio até que alguém tenha algo digno de ser escrito.",
                easter_egg,
            )

        try:
            messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
            messages.extend(self._normalize_history(history, self.MAX_HISTORY))
            messages.append({"role": "user", "content": message.strip()})

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )

            raw_reply = completion.choices[0].message.content or ""
            reply = self._validate_reply(raw_reply)

            if not reply:
                reply = "Curioso. Até mesmo o silêncio pode esconder respostas que nem todos estão preparados para compreender."

            print(f"[TOM RIDDLE]: {reply}")
            if easter_egg:
                print(f"[EASTER EGG ATIVADO]: {easter_egg}")

            return reply, easter_egg

        except Exception as exc:
            print(f"[ERRO GROQ]: {type(exc).__name__}: {exc}")
            return (
                "As páginas parecem incapazes de responder neste momento. "
                "Talvez até mesmo a tinta precise recuperar suas forças.",
                None,
            )