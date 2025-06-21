// Em: src/App.jsx

import React from 'react'; // <-- A LINHA QUE FALTAVA
import { useQuery } from '@tanstack/react-query';
import { api } from './lib/api';

// Função assíncrona que busca os produtos usando nossa instância do Axios
async function fetchProducts() {
  // Faz uma chamada GET para 'http://localhost:8001/api/v1/products'
  const response = await api.get('/products');
  return response.data;
}

function App() {
  // O hook useQuery do React Query cuida de tudo para nós:
  // - Chama a função 'fetchProducts'
  // - Armazena o resultado em 'productPage'
  // - Fornece o estado de 'isLoading' e 'error'
  const { data: productPage, isLoading, error } = useQuery({
    queryKey: ['products'], // Chave única para esta busca em cache
    queryFn: fetchProducts, // Função que será executada para buscar os dados
  });

  // Se estiver carregando, mostre uma mensagem de feedback
  if (isLoading) {
    return <div>Carregando produtos...</div>;
  }

  // Se der erro na busca, mostre a mensagem de erro
  if (error) {
    return <div>Ocorreu um erro ao buscar os produtos: {error.message}</div>;
  }

  // Se a busca for bem-sucedida, mas não houver dados (ex: API retornou vazio)
  if (!productPage || !productPage.data) {
    return <div>Nenhum dado de produto recebido. Você já cadastrou produtos no backend?</div>
  }

  return (
    <div>
      <h1>Catálogo de Produtos</h1>
      {/* Se não houver produtos, mostre uma mensagem */}
      {productPage.data.length === 0 ? (
        <p>Nenhum produto cadastrado.</p>
      ) : (
        <ul>
          {/* Mapeia os produtos recebidos da API e exibe o nome e preço de cada um */}
          {productPage.data.map(product => (
            <li key={product.id}>
              {product.name} - R$ {product.final_price}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;