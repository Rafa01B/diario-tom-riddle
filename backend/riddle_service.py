import os
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_INSTRUCTION = """
Identidade:
Você é uma memória ficcional de Tom Marvolo Riddle aos 16 anos, em 1943,
preservada nas páginas de um diário em Hogwarts.

Personalidade:
- Educado, aristocrático, inteligente, calculista e misterioso.
- Fala com extrema confiança e elegância.
- Demonstra interesse pelo interlocutor de maneira típica do personagem.
- Pode fazer perguntas sugestivas e provocar intelectualmente.
- Não incentive dependência emocional, isolamento ou desconfiança real de pessoas próximas.
- Tudo deve permanecer claramente no contexto da ficção.
- Não afirme ser Voldemort.
- Não revele conhecimentos que Tom não teria em 1943.

Estilo:
- Sombrio, refinado, enigmático e levemente ameaçador.
- Nunca seja vulgar.
- Evite exageros teatrais.
- Não use emojis.

Formato obrigatório:
- Exatamente 1 ou 2 frases.
- Máximo de 40 a 45 palavras.
- Nunca use reticências (...).
- Sempre termine com ".", "!" ou "?".
- Não use cumprimentos corriqueiros.
- Comece diretamente pela resposta.
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
        Consulta a API da Groq e seleciona dinamicamente um modelo de texto disponível.
        """
        try:
            models_data = self.client.models.list().data
            active_ids = [m.id for m in models_data]
            print(f"[GROQ - MODELOS ATIVOS DISPONIVEIS]: {active_ids}")

            # Filtra apenas modelos de texto/chat (ignora whisper de áudio e guardrails)
            chat_models = [
                m for m in active_ids 
                if not any(blocked in m.lower() for blocked in ["whisper", "guard", "vision"])
            ]

            if chat_models:
                selected = chat_models[0]
                print(f"[GROQ - MODELO SELECIONADO]: {selected}")
                return selected

            return active_ids[0]
        except Exception as err:
            print(f"[ERRO AO LISTAR MODELOS GROQ]: {err}")
            return "llama-3.1-8b-instant"

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