// Em: src/components/ProductList.jsx

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useDebounce } from '../hooks/useDebounce';
import { ProductFormModal } from './ProductFormModal';

async function fetchProducts({ queryKey }) {
  const [_key, searchTerm, page] = queryKey;
  
  const params = new URLSearchParams();
  if (searchTerm) {
    params.append('search', searchTerm);
  }
  params.append('page', page);
  params.append('limit', 10);

  const response = await api.get(`/products?${params.toString()}`);
  return response.data;
}

export function ProductList() {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormModalOpen, setFormModalOpen] = useState(false);
  const [productToEdit, setProductToEdit] = useState(null);
  
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  const { data: productPage, isLoading, error, isFetching } = useQuery({
    queryKey: ['products', debouncedSearchTerm, page],
    queryFn: fetchProducts,
    keepPreviousData: true,
  });

  const handleAddProduct = () => {
    setProductToEdit(null);
    setFormModalOpen(true);
  };

  const handleEditProduct = (product) => {
    setProductToEdit(product);
    setFormModalOpen(true);
  };

  const renderStockStatus = (stock) => {
    if (stock > 0) {
      return (
        <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
          Em Estoque
        </span>
      );
    }
    return (
      <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
        Esgotado
      </span>
    );
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Produtos</h1>
          <p className="mt-2 text-sm text-gray-700">
            Gerencie e visualize todos os produtos cadastrados no sistema.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button onClick={handleAddProduct} type="button" className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto">
            Adicionar Produto
          </button>
        </div>
      </div>

      <div className="mt-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Buscar por nome do produto..."
          className="block w-full max-w-lg rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        />
      </div>

      {isFetching && !isLoading && <div className="text-sm text-gray-500 mt-2 animate-pulse">Atualizando lista...</div>}

      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Nome / Descrição</th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Preço</th>
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Ações</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {isLoading ? (
                    <tr><td colSpan="4" className="p-4 text-center text-gray-500">Carregando...</td></tr>
                  ) : error ? (
                    <tr><td colSpan="4" className="p-4 text-center text-red-500">Ocorreu um erro: {error.message}</td></tr>
                  // CORREÇÃO: Verificamos se 'productPage' existe ANTES de tentar acessar 'productPage.data'
                  ) : !productPage || productPage.data.length === 0 ? (
                    <tr><td colSpan="4" className="p-4 text-center text-gray-500">Nenhum produto encontrado.</td></tr>
                  ) : (
                    productPage.data.map((product) => (
                      <tr key={product.id}>
                        <td className="py-4 pl-4 pr-3 text-sm sm:pl-6">
                          <div className="font-medium text-gray-900">{product.name}</div>
                          <div className="mt-1 text-gray-500 truncate max-w-xs">{product.description || 'Sem descrição'}</div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {renderStockStatus(product.stock)}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {product.discount ? (
                            <div>
                              <span className="line-through text-gray-400">R$ {product.price}</span>
                              <span className="ml-2 font-bold text-gray-900">R$ {product.final_price}</span>
                            </div>
                          ) : (
                            <span>R$ {product.price}</span>
                          )}
                        </td>
                        <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                          <button onClick={() => handleEditProduct(product)} className="text-indigo-600 hover:text-indigo-900">
                            Editar<span className="sr-only">, {product.name}</span>
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            {productPage && productPage.meta.totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-2 md:rounded-b-lg">
                <div className="text-sm text-gray-700">
                  Mostrando <span className="font-medium">{(page - 1) * 10 + 1}</span> a <span className="font-medium">{(page - 1) * 10 + productPage.data.length}</span> de <span className="font-medium">{productPage.meta.totalItems}</span> resultados
                </div>
                <div className="flex flex-1 justify-between sm:justify-end gap-2">
                  <button
                    onClick={() => setPage((old) => Math.max(old - 1, 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() => setPage((old) => (productPage.meta.page < productPage.meta.totalPages ? old + 1 : old))}
                    disabled={page === productPage.meta.totalPages || !productPage.data.length}
                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>

      <ProductFormModal 
        open={isFormModalOpen} 
        onOpenChange={setFormModalOpen} 
        productToEdit={productToEdit} 
      />
    </div>
  );
}