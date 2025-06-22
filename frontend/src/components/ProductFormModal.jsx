import React, { useState, useEffect } from 'react';
// 1. Importamos os hooks 'useMutation' e 'useQueryClient' do React Query
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from '../lib/api';

// --- Nossas Funções de API ---

// 2. Função para CRIAR um produto
async function createProduct(newProductData) {
  // Usamos .model_dump() ou .dict() no backend, então enviamos os tipos corretos
  const payload = {
    ...newProductData,
    price: String(newProductData.price), // Enviando como string para a API com Decimal
  };
  const { data } = await api.post('/products', payload);
  return data;
}

// 3. Função para ATUALIZAR um produto
async function updateProduct({ id, data }) {
  const payload = {
    ...data,
    price: String(data.price), // Enviando como string para a API com Decimal
  };
  const response = await api.patch(`/products/${id}`, payload);
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
    if (productToEdit && open) {
      setName(productToEdit.name);
      setDescription(productToEdit.description || '');
      setPrice(String(productToEdit.price));
      setStock(String(productToEdit.stock));
    } else if (!productToEdit && open) {
      // Limpa o formulário quando abre para Adicionar
      setName('');
      setDescription('');
      setPrice('');
      setStock('');
    }
  }, [productToEdit, open]);

  // --- Nossas Mutações ---

  // Função a ser chamada em caso de sucesso para ambas as mutações
  const onMutationSuccess = () => {
    // Invalida a query 'products'. Isso diz ao React Query:
    // "Os dados de produtos estão desatualizados, busque-os novamente".
    // Isso faz a nossa tabela se atualizar AUTOMATICAMENTE!
    queryClient.invalidateQueries({ queryKey: ['products'] });
    onOpenChange(false); // Fecha o modal
  };

  // 4. Mutação para CRIAR
  const { mutate: createMutate, isLoading: isCreating } = useMutation({
    mutationFn: createProduct,
    onSuccess: onMutationSuccess,
    onError: (error) => alert(`Erro ao criar produto: ${error.response?.data?.detail || error.message}`),
  });

  // 5. Mutação para ATUALIZAR
  const { mutate: updateMutate, isLoading: isUpdating } = useMutation({
    mutationFn: updateProduct,
    onSuccess: onMutationSuccess,
    onError: (error) => alert(`Erro ao editar produto: ${error.response?.data?.detail || error.message}`),
  });

  // 6. Lógica de Submit Inteligente
  const handleSubmit = (event) => {
    event.preventDefault();
    const productData = {
      name,
      description,
      price: parseFloat(price),
      stock: parseInt(stock, 10),
    };

    if (isEditing) {
      updateMutate({ id: productToEdit.id, data: productData });
    } else {
      createMutate(productData);
    }
  };
  
  const isLoading = isCreating || isUpdating;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar Produto' : 'Adicionar Novo Produto'}</DialogTitle>
          <DialogDescription>
            {isEditing ? `Alterando dados de: ${productToEdit.name}` : 'Preencha os detalhes do novo produto.'}
          </DialogDescription>
        </DialogHeader>
        <form id="product-form" onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
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
        </form>
        <DialogFooter>
          <Button type="submit" form="product-form" disabled={isLoading}>
            {isLoading ? 'Salvando...' : 'Salvar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}