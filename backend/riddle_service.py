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
- Não incentive dependência emocional, isolamento ou desconfiança real
  de pessoas próximas.
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
    Motor de conversa para a persona ficcional de Tom Riddle integrado via Groq.
    """

    MODEL = "llama3-8b-8192"
    MAX_HISTORY = 6
    MAX_TOKENS = 90
    TEMPERATURE = 0.7

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY não encontrada nas variáveis de ambiente."
            )

        self.client = Groq(api_key=api_key)

    @staticmethod
    def _detect_easter_egg(message: str) -> Optional[str]:
        """
        Detecta palavras-chave na mensagem para disparar efeitos especiais no frontend.
        """
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
    def _normalize_history(history: Optional[list]) -> list:
        """
        Converte diferentes formatos de histórico para:
        {"role": "user"/"assistant", "content": "..."}
        """
        if not history:
            return []

        normalized = []

        for item in history[-RiddleEngine.MAX_HISTORY:]:
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
        """
        Garante que a resposta respeite as regras estilísticas da persona
        sem fatiar orações pela metade.
        """
        reply = reply.strip()

        if len(reply) >= 2 and reply[0] == '"' and reply[-1] == '"':
            reply = reply[1:-1].strip()

        reply = reply.replace("...", ".")

        if reply and reply[-1] not in ".?!":
            reply += "."

        return reply

    def _build_messages(self, message: str, history: Optional[list]) -> list:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            }
        ]

        messages.extend(self._normalize_history(history))

        messages.append({
            "role": "user",
            "content": message.strip()
        })

        return messages

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
            messages = self._build_messages(message, history)

            completion = self.client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )

            raw_reply = completion.choices[0].message.content or ""
            reply = self._validate_reply(raw_reply)

            if not reply:
                reply = (
                    "Curioso. Até mesmo o silêncio pode esconder respostas "
                    "que certas pessoas não estão preparadas para compreender."
                )

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

    def stream_reply(
        self,
        message: str,
        history: Optional[list] = None
    ):
        if not message or not message.strip():
            yield (
                "As páginas permanecem em silêncio até que alguém "
                "tenha algo digno de ser escrito."
            )
            return

        try:
            messages = self._build_messages(message, history)

            stream = self.client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
                stream=True,
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        except Exception as exc:
            print(f"[ERRO STREAM GROQ]: {type(exc).__name__}: {exc}")
            yield "As páginas parecem incapazes de responder neste momento."