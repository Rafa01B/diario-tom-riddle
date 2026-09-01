import { useState, useCallback } from 'react';

const API_BASE_URL = 'http://localhost:8000/api';

export function useDiarySession() {
  const [messages, setMessages] = useState([]);
  const [currentDisplay, setCurrentDisplay] = useState(null);
  const [easterEgg, setEasterEgg] = useState(null);
  const [isBusy, setIsBusy] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());

  const sendMessage = useCallback(async (userText) => {
    if (!userText.trim() || isBusy) return;

    setIsBusy(true);
    setEasterEgg(null);

    // Exibe a mensagem do usuário
    setCurrentDisplay({ type: 'user', text: userText, phase: 'writing' });

    // Absorve a tinta
    setTimeout(() => {
      setCurrentDisplay((prev) => prev ? { ...prev, phase: 'absorbing' } : null);
    }, 1200);

    try {
      const response = await fetch(`${API_BASE_URL}/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userText,
          history: messages
        }),
      });

      if (!response.ok) throw new Error('Falha ao comunicar com o diário');
      const data = await response.json();

      const updatedHistory = [
        ...messages,
        { role: 'user', content: userText },
        { role: 'assistant', content: data.response }
      ];

      // Dispara a revelação e ativa qualquer evento místico
      setTimeout(() => {
        setMessages(updatedHistory);
        setEasterEgg(data.easter_egg_triggered);
        setCurrentDisplay({ type: 'riddle', text: data.response, phase: 'revealing' });
        setIsBusy(false);
      }, 3200);

    } catch (err) {
      console.error(err);
      setCurrentDisplay({
        type: 'riddle',
        text: 'Algo perturbou a magia destas páginas...',
        phase: 'revealing'
      });
      setIsBusy(false);
    }
  }, [messages, isBusy, sessionId]);

  return { currentDisplay, easterEgg, isBusy, sendMessage };
}