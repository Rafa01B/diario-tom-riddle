import React, { useState, useEffect, useCallback } from 'react';
import { useDiarySession } from '../hooks/useDiarySession';
import { sfx } from '../utils/audio';

export default function DiaryBook() {
  const [inputVal, setInputVal] = useState('');
  const { pages = [], currentDisplay, easterEgg, isBusy, sendMessage } = useDiarySession();

  // Índice da página atual em exibição.
  // Se currentPageIndex === pages.length, o usuário está na "Página Atual" (onde se escreve).
  const [currentPageIndex, setCurrentPageIndex] = useState(0);

  // Sincroniza o leitor para a última página sempre que uma nova resposta é gerada
  useEffect(() => {
    setCurrentPageIndex(pages.length);
  }, [pages.length]);

  // Áudio da tinta sendo absorvida
  useEffect(() => {
    if (currentDisplay?.phase === 'absorbing') {
      sfx.playInkAbsorption();
    }
  }, [currentDisplay?.phase]);

  // Efeito sonoro de papel se movendo enquanto Riddle delibera
  useEffect(() => {
    let interval;
    if (isBusy) {
      sfx.playPageRustle();
      interval = setInterval(() => {
        sfx.playPageRustle();
      }, 2400);
    }
    return () => clearInterval(interval);
  }, [isBusy]);

  // Reações sonoras dos Easter Eggs
  useEffect(() => {
    if (easterEgg === 'dark_mark_flicker') {
      sfx.playDarkTremor();
    } else if (easterEgg === 'parseltongue_whisper') {
      sfx.playParseltongue();
    }
  }, [easterEgg]);

  // Handlers para folhear páginas
  const handlePrevPage = useCallback(() => {
    if (currentPageIndex > 0 && !isBusy) {
      sfx.playPageRustle();
      setCurrentPageIndex((prev) => prev - 1);
    }
  }, [currentPageIndex, isBusy]);

  const handleNextPage = useCallback(() => {
    if (currentPageIndex < pages.length && !isBusy) {
      sfx.playPageRustle();
      setCurrentPageIndex((prev) => prev + 1);
    }
  }, [currentPageIndex, pages.length, isBusy]);

  // Navegação por teclado (Setas Esquerda / Direita)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (document.activeElement.tagName === 'INPUT') return;
      if (e.key === 'ArrowLeft') handlePrevPage();
      if (e.key === 'ArrowRight') handleNextPage();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlePrevPage, handleNextPage]);

  const handleInputChange = (e) => {
    setInputVal(e.target.value);
    sfx.playQuillScratch();
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputVal.trim() || isBusy) return;
    sendMessage(inputVal);
    setInputVal('');
  };

  const isBrowsingPast = currentPageIndex < pages.length;
  const viewedHistoricalPage = isBrowsingPast ? pages[currentPageIndex] : null;

  return (
    <main className="relative flex min-h-screen items-center justify-center bg-[#070504] p-4 sm:p-8 overflow-hidden select-none">

      {/* Luz ambiente de vela oscilando ao redor */}
      <div className={`pointer-events-none absolute inset-0 transition-colors duration-1000 ${easterEgg === 'parseltongue_whisper' ? 'bg-[radial-gradient(circle_at_50%_40%,rgba(16,94,46,0.25)_0%,transparent_70%)]' :
        easterEgg === 'dark_mark_flicker' ? 'bg-[radial-gradient(circle_at_50%_40%,rgba(140,15,15,0.3)_0%,transparent_70%)]' :
          'bg-[radial-gradient(circle_at_50%_40%,rgba(180,100,30,0.12)_0%,transparent_70%)]'
        }`} />

      {/* Capa de couro */}
      <div className={`candle-glow relative w-full max-w-3xl rounded-lg bg-[#140f0c] p-4 shadow-[0_0_80px_rgba(0,0,0,0.95)] border border-[#2b1e16] transition-all duration-700 ${easterEgg === 'dark_mark_flicker' ? 'shake-curse curse-aura' : ''
        } ${easterEgg === 'parseltongue_whisper' ? 'slytherin-aura' : ''
        }`}>

        {/* Folha de pergaminho */}
        <div className="diary-parchment relative min-h-[580px] w-full rounded p-8 sm:p-14 shadow-inner flex flex-col justify-between overflow-hidden border-l-[12px] border-[#1d140e]">

          {/* Manchas de tinta sobrenaturais (Ativas apenas enquanto ele pensa) */}
          {isBusy && (
            <>
              <div className="ghost-stain-1 pointer-events-none absolute top-1/4 left-1/3 h-24 w-24 rounded-full bg-[#1b120c] mix-blend-multiply filter blur-sm" />
              <div className="ghost-stain-2 pointer-events-none absolute bottom-1/3 right-1/4 h-32 w-32 rounded-full bg-[#241710] mix-blend-multiply filter blur-md" />
            </>
          )}

          {/* Cabeçalho do Diário com Marcador de Páginas */}
          <div className="flex items-center justify-between border-b border-[#80674d]/20 pb-2 mb-4">
            <span className="font-cinzel text-[10px] tracking-[0.2em] text-[#6d5b4a]/60 uppercase">
              {isBrowsingPast ? `Página ${currentPageIndex + 1} de ${pages.length}` : 'Página Presente'}
            </span>
            <span className="font-cinzel text-xs tracking-[0.35em] text-[#6d5b4a]/80 select-none">
              T. M. RIDDLE
            </span>
            <span className="font-cinzel text-[10px] tracking-[0.2em] text-[#6d5b4a]/60">
              1943
            </span>
          </div>

          {/* Área central mágica de texto */}
          <section className="relative z-10 flex-1 flex flex-col justify-start items-center text-center px-4 sm:px-8 py-4 overflow-y-auto max-h-[400px]">

            {/* Cenário A: Folheando uma página antiga gravada */}
            {isBrowsingPast && viewedHistoricalPage && (
              <div className="my-auto max-w-2xl w-full flex flex-col gap-6 animate-fadeIn">
                <div className="font-user text-xl sm:text-2xl text-[#3b2b20]/60 italic">
                  "{viewedHistoricalPage.userText}"
                </div>
                <div className="font-riddle text-2xl sm:text-3xl md:text-4xl font-bold tracking-wide text-[#080504] leading-relaxed">
                  {viewedHistoricalPage.riddleText}
                </div>
              </div>
            )}

            {/* Cenário B: Página atual viva (escrevendo/absorvendo/revelando) */}
            {!isBrowsingPast && currentDisplay && (
              <div
                key={currentDisplay.text}
                className={`
                  my-auto max-w-2xl w-full break-words whitespace-pre-line leading-relaxed
                  ${currentDisplay.type === 'user' ? 'font-user text-2xl sm:text-3xl text-[#120d0b]' : 'font-riddle text-2xl sm:text-3xl md:text-4xl font-bold tracking-wide'}
                  ${currentDisplay.type === 'riddle' && easterEgg === 'dark_mark_flicker' ? 'text-[#3d0808]' : ''}
                  ${currentDisplay.type === 'riddle' && easterEgg === 'parseltongue_whisper' ? 'text-[#072412]' : 'text-[#080504]'}
                  ${currentDisplay.phase === 'absorbing' ? 'ink-absorb' : ''}
                  ${currentDisplay.phase === 'revealing' ? 'ink-reveal' : ''}
                `}
              >
                {currentDisplay.text}
              </div>
            )}

            {/* Sussurro espectral enquanto Tom formula sua resposta */}
            {!isBrowsingPast && isBusy && !currentDisplay?.text && (
              <div className="my-auto ghost-whisper font-cinzel text-xs tracking-[0.4em] text-[#5e4b3c] uppercase">
                As páginas despertam...
              </div>
            )}
          </section>

          {/* Navegadores de Páginas (Setas Laterais Discretas no Diário) */}
          <div className="flex items-center justify-between text-[#5e4b3c] px-2 py-1 select-none">
            <button
              type="button"
              onClick={handlePrevPage}
              disabled={currentPageIndex === 0 || isBusy}
              className="font-cinzel text-xs tracking-widest uppercase transition-opacity hover:text-[#231811] disabled:opacity-10 disabled:cursor-not-allowed flex items-center gap-1"
            >
              &#x25C0; Virar Atrás
            </button>

            {isBrowsingPast && (
              <button
                type="button"
                onClick={() => setCurrentPageIndex(pages.length)}
                className="font-cinzel text-[11px] tracking-widest uppercase text-[#8c4b2d] hover:underline"
              >
                Retornar ao Presente &#x270E;
              </button>
            )}

            <button
              type="button"
              onClick={handleNextPage}
              disabled={currentPageIndex >= pages.length || isBusy}
              className="font-cinzel text-xs tracking-widest uppercase transition-opacity hover:text-[#231811] disabled:opacity-10 disabled:cursor-not-allowed flex items-center gap-1"
            >
              Virar Adiante &#x25B6;
            </button>
          </div>

          {/* Formulário de escrita (Apenas ativo na página presente) */}
          <form onSubmit={handleSend} className="relative z-10 mt-3 flex items-center gap-3 border-t border-[#80674d]/30 pt-4">
            <input
              type="text"
              value={inputVal}
              onChange={handleInputChange}
              disabled={isBusy || isBrowsingPast}
              placeholder={
                isBrowsingPast
                  ? "Volte à página presente para mergulhar a pena..."
                  : isBusy
                    ? "Alguém segura a pena invisível..."
                    : "Mergulhe a pena e escreva..."
              }
              className="w-full bg-transparent font-user text-2xl sm:text-3xl text-[#1a120c] placeholder:font-cinzel placeholder:text-xs placeholder:tracking-widest placeholder:text-[#846f5c] focus:outline-none disabled:opacity-40"
            />
            <button
              type="submit"
              disabled={isBusy || isBrowsingPast || !inputVal.trim()}
              className="rounded bg-[#231811] px-5 py-2 font-cinzel text-xs font-semibold tracking-widest text-[#d8c3a5] uppercase transition hover:bg-[#3d2b1e] disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Inscrever
            </button>
          </form>

        </div>
      </div>
    </main>
  );
}