// Em: src/hooks/useDebounce.js
import { useState, useEffect } from 'react';

// Este hook customizado recebe um valor e um atraso (delay)
export function useDebounce(value, delay) {
  // Estado para armazenar o valor "atrasado"
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // Cria um timer que só vai atualizar o valor "atrasado"
    // depois que o tempo de 'delay' passar sem que o 'value' mude.
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Limpa o timer se o 'value' mudar antes do delay terminar.
    // Isso reinicia a contagem.
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]); // Roda o efeito novamente se o valor ou o delay mudarem

  return debouncedValue;
}