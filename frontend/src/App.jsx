// Em: src/App.jsx
import React from 'react';
import { ProductList } from './components/ProductList'; // Importa nosso novo componente

function App() {
  return (
    // Container principal da aplicação com uma cor de fundo suave
    <main className="bg-gray-50 min-h-screen">
      <ProductList />
    </main>
  );
}

export default App;