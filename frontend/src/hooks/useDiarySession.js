import { useState, useCallback } from 'react';

// Garante o prefixo /api e remove barras duplicadas no final caso existam
const rawUrl = import.meta.env.VITE_API_URL || 'https://diario-tom-riddle.onrender.com/api';
const API_BASE_URL = rawUrl.replace(/\/+$/, '');

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

    // 1. Exibe a mensagem escrita pelo usuário
    setCurrentDisplay({ type: 'user', text: userText, phase: 'writing' });

    // 2. Transição de absorção da tinta no pergaminho
    setTimeout(() => {
      setCurrentDisplay((prev) => (prev ? { ...prev, phase: 'absorbing' } : null));
    }, 1200);

    try {
      // Dispara a requisição para a rota correta: /api/write
      const endpoint = API_BASE_URL.endsWith('/api') 
        ? `${API_BASE_URL}/write` 
        : `${API_BASE_URL}/api/write`;

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: userText,
          history: messages,
        }),
      });

      if (!response.ok) {
        throw new Error(`Falha no servidor: ${response.status}`);
      }

      const data = await response.json();

      const updatedHistory = [
        ...messages,
        { role: 'user', content: userText },
        { role: 'assistant', content: data.response },
      ];

      // Revela a resposta de Riddle após a tinta sumir
      setTimeout(() => {
        setMessages(updatedHistory);
        setEasterEgg(data.easter_egg_triggered);
        setCurrentDisplay({ type: 'riddle', text: data.response, phase: 'revealing' });
        setIsBusy(false);
      }, 3000);

    } catch (err) {
      console.error('[ERRO DE CONEXAO]:', err);
      setCurrentDisplay({
        type: 'riddle',
        text: 'O pergaminho está despertando das sombras... Aguarde alguns instantes e tente novamente.',
        phase: 'revealing',
      });
      setIsBusy(false);
    }
  }, [messages, isBusy, sessionId]);

  return { currentDisplay, easterEgg, isBusy, sendMessage };
}