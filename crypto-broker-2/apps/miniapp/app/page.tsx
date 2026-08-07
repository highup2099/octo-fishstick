"use client";
import {useState} from "react";

export default function Home() {
  const [amount,setAmount]=useState("1000");
  const [result,setResult]=useState<string|null>(null);

  async function getQuote() {
    const r=await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/quotes`,{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({sell_asset:"USDT",buy_asset:"USDC",sell_amount:amount})
    });
    const data=await r.json();
    setResult(r.ok ? `Receive ${data.buy_amount} USDC · fee ${data.fee_amount} USDT` : "Quote failed");
  }

  return <main style={{maxWidth:520,margin:"0 auto",padding:24}}>
    <h1>CryptoBroker</h1><p>Invite-only brokerage MVP</p>
    <label>Sell amount</label>
    <input value={amount} onChange={e=>setAmount(e.target.value)} inputMode="decimal"
      style={{display:"block",width:"100%",padding:14,margin:"8px 0 20px"}} />
    <div>USDT → USDC</div>
    <button onClick={getQuote} style={{width:"100%",padding:14,marginTop:20}}>Get Quote</button>
    {result && <p>{result}</p>}
  </main>;
}
