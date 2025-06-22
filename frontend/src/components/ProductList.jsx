// Em: src/components/ProductList.jsx

import React, { useState } from 'react';
// CORREÇÃO: Importamos os hooks que faltavam
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'; 
import { api } from '../lib/api';
import { useDebounce } from '../hooks/useDebounce';
import { ProductFormModal } from './ProductFormModal';
// Importamos os novos componentes
import { ConfirmationDialog } from './ConfirmationDialog';
import { Trash2, Edit, PlusCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

async function fetchProducts({ queryKey }) {
  const [_key, searchTerm, page] = queryKey;
  const params = new URLSearchParams();
  if (searchTerm) params.append('search', searchTerm);
  params.append('page', page);
  params.append('limit', 10);
  const response = await api.get(`/products?${params.toString()}`);
  return response.data;
}

// Função para chamar a API de deleção
async function deleteProduct(productId) {
  const response = await api.delete(`/products/${productId}`);
  return response.data;
}

export function ProductList() {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormModalOpen, setFormModalOpen] = useState(false);
  const [productToEdit, setProductToEdit] = useState(null);
  const [productToDelete, setProductToDelete] = useState(null);

  // Precisamos do queryClient para invalidar o cache após uma deleção
  const queryClient = useQueryClient();
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  const { data: productPage, isLoading, error, isFetching } = useQuery({
    queryKey: ['products', debouncedSearchTerm, page],
    queryFn: fetchProducts,
    keepPreviousData: true,
  });

  // MUTAÇÃO para deletar um produto
  const deleteMutation = useMutation({
    mutationFn: deleteProduct,
    onSuccess: () => {
      console.log("Produto deletado com sucesso!");
      // Invalida a query de 'products' para forçar a atualização da tabela
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error) => {
      alert(`Erro ao deletar produto: ${error.response?.data?.detail || error.message}`);
    }
  });

  const handleAddProduct = () => {
    setProductToEdit(null);
    setFormModalOpen(true);
  };

  const handleEditProduct = (product) => {
    setProductToEdit(product);
    setFormModalOpen(true);
  };

  const handleConfirmDelete = () => {
    if (productToDelete) {
      deleteMutation.mutate(productToDelete.id);
      setProductToDelete(null); // Fecha o modal de confirmação
    }
  };

  const renderStockStatus = (stock) => {
    const isOutOfStock = stock === 0;
    return (
      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${isOutOfStock ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
        {isOutOfStock ? 'Esgotado' : 'Em Estoque'}
      </span>
    );
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Produtos</h1>
          <p className="mt-2 text-sm text-gray-700">Gerencie e visualize todos os produtos cadastrados no sistema.</p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Button onClick={handleAddProduct}>
            <PlusCircle className="mr-2 h-4 w-4" />
            Adicionar Produto
          </Button>
        </div>
      </div>

      <div className="mt-4">
        <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Buscar por nome do produto..." className="block w-full max-w-lg rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
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
                    <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6"><span className="sr-only">Ações</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {isLoading ? (
                    <tr><td colSpan="4" className="p-4 text-center text-gray-500">Carregando...</td></tr>
                  ) : error ? (
                    <tr><td colSpan="4" className="p-4 text-center text-red-500">Ocorreu um erro: {error.message}</td></tr>
                  ) : !productPage || productPage.data.length === 0 ? (
                    <tr><td colSpan="4" className="p-4 text-center text-gray-500">Nenhum produto encontrado.</td></tr>
                  ) : (
                    productPage.data.map((product) => (
                      <tr key={product.id}>
                        <td className="py-4 pl-4 pr-3 text-sm sm:pl-6">
                          <div className="font-medium text-gray-900">{product.name}</div>
                          <div className="mt-1 text-gray-500 truncate max-w-xs">{product.description || 'Sem descrição'}</div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{renderStockStatus(product.stock)}</td>
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
                          <div className="flex items-center justify-end gap-2">
                            <Button variant="ghost" size="icon" onClick={() => handleEditProduct(product)}>
                              <Edit className="h-4 w-4" />
                              <span className="sr-only">Editar</span>
                            </Button>
                            <Button variant="ghost" size="icon" className="text-red-600 hover:text-red-700" onClick={() => setProductToDelete(product)}>
                              <Trash2 className="h-4 w-4" />
                              <span className="sr-only">Excluir</span>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            {productPage && productPage.meta.totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-2 md:rounded-b-lg">
                 {/* ... (lógica de paginação) ... */}
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
      <ConfirmationDialog 
        open={!!productToDelete} 
        onOpenChange={() => setProductToDelete(null)}
        onConfirm={handleConfirmDelete}
        title={`Excluir Produto: ${productToDelete?.name ?? ''}`}
        description="Esta ação não pode ser desfeita. O produto será marcado como inativo."
      />
    </div>
  );
}