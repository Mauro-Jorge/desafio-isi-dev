// Em: src/components/ProductFormModal.jsx

import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogDescription,
  DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from '../lib/api';

// --- Nossas Funções de API ---

// 1. Função para CRIAR um produto
async function createProduct(newProductData) {
  const response = await api.post('/products', newProductData);
  return response.data;
}

// 2. Função para ATUALIZAR um produto
// Recebe um objeto com o ID do produto e os novos dados
async function updateProduct({ id, data }) {
  const response = await api.patch(`/products/${id}`, data);
  return response.data;
}


export function ProductFormModal({ open, onOpenChange, productToEdit }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');

  const isEditing = !!productToEdit;
  const queryClient = useQueryClient();

  useEffect(() => {
    if (productToEdit) {
      setName(productToEdit.name);
      setDescription(productToEdit.description || '');
      setPrice(productToEdit.price);
      setStock(productToEdit.stock);
    } else {
      setName('');
      setDescription('');
      setPrice('');
      setStock('');
    }
  }, [productToEdit, open]); // Adicionado 'open' para garantir que o form limpe ao reabrir

  // --- Nossas Mutações ---

  const onMutationSuccess = () => {
    // Função a ser chamada em caso de sucesso para ambas as mutações
    console.log('Operação bem-sucedida!');
    queryClient.invalidateQueries(['products']);
    onOpenChange(false);
  };

  // 3. Mutação para CRIAR
  const createMutation = useMutation({
    mutationFn: createProduct,
    onSuccess: onMutationSuccess,
    onError: (error) => {
      alert(`Erro ao criar produto: ${error.response?.data?.detail || error.message}`);
    },
  });

  // 4. Mutação para ATUALIZAR
  const updateMutation = useMutation({
    mutationFn: updateProduct,
    onSuccess: onMutationSuccess,
    onError: (error) => {
      alert(`Erro ao editar produto: ${error.response?.data?.detail || error.message}`);
    },
  });

  // 5. Lógica de Submit Inteligente
  const handleSubmit = (event) => {
    event.preventDefault();

    const productData = {
      name,
      description,
      price: parseFloat(price),
      stock: parseInt(stock, 10),
    };

    if (isEditing) {
      // Se estiver editando, chama a mutação de atualização
      updateMutation.mutate({ id: productToEdit.id, data: productData });
    } else {
      // Senão, chama a mutação de criação
      createMutation.mutate(productData);
    }
  };
  
  // Verifica se alguma das mutações está em andamento
  const isLoading = createMutation.isLoading || updateMutation.isLoading;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar Produto' : 'Adicionar Novo Produto'}</DialogTitle>
          <DialogDescription>
            {isEditing ? `Alterando dados de: ${productToEdit.name}` : 'Preencha os detalhes do novo produto.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {/* ... os inputs do formulário continuam os mesmos */}
             <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">Nome</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">Descrição</Label>
              <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="price" className="text-right">Preço</Label>
              <Input id="price" type="number" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="stock" className="text-right">Estoque</Label>
              <Input id="stock" type="number" value={stock} onChange={(e) => setStock(e.target.value)} className="col-span-3" required />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}