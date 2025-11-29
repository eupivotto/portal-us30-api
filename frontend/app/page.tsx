"use client";
import { useState, useEffect } from "react";

export default function Home() {
  // Use <any> para evitar erro de tipagem chato teste
  const [dados, setDados] = useState<any>(null);

  useEffect(() => {
    // Sua URL de produção do Render
    fetch("https://portal-us30-api.onrender.com/teste-btc")
      .then((res) => res.json())
      .then((data) => setDados(data));
  }, []);

  if (!dados) return <div className="p-10 text-white">Carregando Setup...</div>;

  return (
    <main className="min-h-screen p-10 bg-black text-white">
      <h1 className="text-4xl font-bold text-yellow-500 mb-10">
        Painel US30 Elite (Teste BTC)
      </h1>

      <div className="p-6 border border-orange-500 rounded-xl bg-orange-900/20 w-full max-w-md">
        <h2 className="text-xl font-bold">₿ {dados.ativo}</h2>
        <p className="text-4xl mt-4 font-mono">${dados.preco_atual}</p>
        
        <div className="mt-4 flex items-center gap-2">
            <span className="text-sm text-gray-400">Status:</span>
            <span className="font-bold text-green-400">{dados.status}</span>
        </div>
      </div>
  
      <p className="mt-10 text-gray-600 text-sm">
        *Domingo à noite voltamos o código para Goldman Sachs.
      </p>
    </main>
  );
}
