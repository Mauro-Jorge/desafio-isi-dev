// Em: src/components/DiscountFormModal.jsx

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from '../lib/api';

// Funções que chamam a API
async function applyPercentDiscount({ productId, value }) {
  const { data } = await api.post(`/products/${productId}/discount/percent`, { value });
  return data;
}

async function applyCouponDiscount({ productId, code }) {
  const { data } = await api.post(`/products/${productId}/discount/coupon`, { code });
  return data;
}

export function DiscountFormModal({ open, onOpenChange, product }) {
  const queryClient = useQueryClient();
  const [percentValue, setPercentValue] = useState('');
  const [couponCode, setCouponCode] = useState('');

  const onMutationSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['products'] });
    onOpenChange(false);
  };

  const percentMutation = useMutation({
    mutationFn: applyPercentDiscount,
    onSuccess: onMutationSuccess,
    onError: (error) => alert(`Erro: ${error.response?.data?.detail || error.message}`),
  });

  const couponMutation = useMutation({
    mutationFn: applyCouponDiscount,
    onSuccess: onMutationSuccess,
    onError: (error) => alert(`Erro: ${error.response?.data?.detail || error.message}`),
  });

  const handleApplyPercent = (e) => {
    e.preventDefault();
    percentMutation.mutate({ productId: product.id, value: parseFloat(percentValue) });
  };

  const handleApplyCoupon = (e) => {
    e.preventDefault();
    couponMutation.mutate({ productId: product.id, code: couponCode });
  };
  
  const isLoading = percentMutation.isLoading || couponMutation.isLoading;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Aplicar Desconto</DialogTitle>
          <DialogDescription>
            Aplicando desconto no produto: <span className="font-bold">{product?.name}</span>
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="percent" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="percent">Percentual</TabsTrigger>
            <TabsTrigger value="coupon">Cupom</TabsTrigger>
          </TabsList>
          
          <TabsContent value="percent">
            <form onSubmit={handleApplyPercent}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="percent" className="text-right">Valor (%)</Label>
                  <Input id="percent" type="number" value={percentValue} onChange={(e) => setPercentValue(e.target.value)} className="col-span-3" placeholder="Ex: 15" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Aplicando...' : 'Aplicar Desconto'}
                </Button>
              </DialogFooter>
            </form>
          </TabsContent>

          <TabsContent value="coupon">
            <form onSubmit={handleApplyCoupon}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="coupon" className="text-right">Código</Label>
                  <Input id="coupon" value={couponCode} onChange={(e) => setCouponCode(e.target.value)} className="col-span-3" placeholder="Ex: PROMO10" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Aplicando...' : 'Aplicar Cupom'}
                </Button>
              </DialogFooter>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}