import { useState, useCallback, useRef } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://diario-tom-riddle.onrender.com';

export function useDiarySession() {
  const [pages, setPages] = useState([]); // Histórico de { userText, riddleText, easterEgg }
  const [currentDisplay, setCurrentDisplay] = useState(null); // { text, type: 'user'|'riddle', phase: 'absorbing'|'revealing' }
  const [easterEgg, setEasterEgg] = useState(null);
  const [isBusy, setIsBusy] = useState(false);

  // Armazena o histórico no formato enviado à API para contexto contínuo
  const conversationHistoryRef = useRef([]);

  const sendMessage = useCallback(async (text) => {
    const trimmedText = text.trim();
    if (!trimmedText || isBusy) return;

    setIsBusy(true);
    setEasterEgg(null);

    // 1. Fase de escrita do usuário
    setCurrentDisplay({
      text: trimmedText,
      type: 'user',
      phase: 'written',
    });

    // 2. Transição para absorção da tinta do usuário
    setTimeout(() => {
      setCurrentDisplay((prev) => (prev ? { ...prev, phase: 'absorbing' } : null));
    }, 1200);

    // 3. Tinta some por completo antes do Riddle começar a responder
    setTimeout(() => {
      setCurrentDisplay(null);
    }, 2400);

    try {
      const response = await fetch(`${API_BASE_URL}/api/write`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: trimmedText,
          history: conversationHistoryRef.current,
        }),
      });

      if (!response.ok) {
        throw new Error(`Falha no servidor: ${response.status}`);
      }

      const data = await response.json();
      const riddleReply = data.response;
      const detectedEgg = data.easter_egg || null;

      // Atualiza o histórico de contexto enviado para o LLM
      conversationHistoryRef.current = [
        ...conversationHistoryRef.current,
        { role: 'user', content: trimmedText },
        { role: 'assistant', content: riddleReply },
      ];

      // Delay para manter o suspense sobrenatural após a absorção
      setTimeout(() => {
        if (detectedEgg) {
          setEasterEgg(detectedEgg);
        }

        // 4. Revelação da escrita de Tom Riddle
        setCurrentDisplay({
          text: riddleReply,
          type: 'riddle',
          phase: 'revealing',
        });

        // 5. Salva a troca completa como uma página permanente do diário
        setPages((prev) => [
          ...prev,
          {
            userText: trimmedText,
            riddleText: riddleReply,
            easterEgg: detectedEgg,
          },
        ]);

        setIsBusy(false);
      }, 3000);

    } catch (error) {
      console.error('[ERRO DE CONEXAO]:', error);

      setTimeout(() => {
        const errorReply = 'As páginas parecem inertes neste momento. Até mesmo a tinta precisa recuperar suas forças.';
        
        setCurrentDisplay({
          text: errorReply,
          type: 'riddle',
          phase: 'revealing',
        });

        setPages((prev) => [
          ...prev,
          {
            userText: trimmedText,
            riddleText: errorReply,
            easterEgg: null,
          },
        ]);

        setIsBusy(false);
      }, 2600);
    }
  }, [isBusy]);

  return {
    pages,
    currentDisplay,
    easterEgg,
    isBusy,
    sendMessage,
  };
}