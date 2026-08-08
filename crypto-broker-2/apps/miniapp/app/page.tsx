"use client";

import { useState } from "react";
import { init, useLaunchParams } from "@telegram-apps/sdk-react";

// Initialize Telegram Mini Apps SDK
if (typeof window !== "undefined") {
  init();
}

interface Quote {
  id: string;
  sell_asset: string;
  buy_asset: string;
  sell_amount: number;
  buy_amount: number;
  rate: number;
  fee_percent: number;
  fee_amount: number;
  status: string;
  expires_at: string;
}

interface Order {
  id: string;
  status: string;
  sell_asset: string;
  buy_asset: string;
  sell_amount: number;
  buy_amount: number;
  fee_amount: number;
  withdrawal_address?: string;
}

export default function Home() {
  const lp = useLaunchParams();
  const [step, setStep] = useState<"quote" | "confirm" | "success">("quote");
  const [sellAmount, setSellAmount] = useState<string>("1000");
  const [withdrawalAddress, setWithdrawalAddress] = useState<string>("");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  async function fetchQuote() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/quotes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sell_asset: "USDT",
          buy_asset: "BTC",
          amount: parseFloat(sellAmount),
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to get quote");
      }

      const data: Quote = await response.json();
      setQuote(data);
      setStep("confirm");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function createOrder() {
    if (!quote) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quote_id: quote.id,
          withdrawal_address: withdrawalAddress,
          withdrawal_network: "TRC20",
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to create order");
      }

      const data: Order = await response.json();
      setOrder(data);
      setStep("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setStep("quote");
    setSellAmount("1000");
    setWithdrawalAddress("");
    setQuote(null);
    setOrder(null);
    setError(null);
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            CryptoBroker
          </h1>
          <p className="text-gray-400 mt-2">Non-custodial OTC Exchange</p>
          {lp?.initData?.user && (
            <p className="text-sm text-gray-500 mt-1">
              Welcome, {lp.initData.user.firstName}!
            </p>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-300">❌ {error}</p>
          </div>
        )}

        {/* Step 1: Enter Amount */}
        {step === "quote" && (
          <div className="space-y-6">
            <div className="bg-gray-800/50 rounded-xl p-6 backdrop-blur">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                💰 Sell Amount (USDT)
              </label>
              <input
                type="number"
                value={sellAmount}
                onChange={(e) => setSellAmount(e.target.value)}
                inputMode="decimal"
                placeholder="1000"
                min="10"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
              />

              <div className="mt-4 flex items-center justify-between text-sm text-gray-400">
                <span>USDT → BTC</span>
                <span className="text-blue-400">Fee: 1.5%</span>
              </div>

              <button
                onClick={fetchQuote}
                disabled={loading || !sellAmount}
                className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? "Getting Quote..." : "📊 Get Quote"}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Confirm Order */}
        {step === "confirm" && quote && (
          <div className="space-y-6">
            <div className="bg-gray-800/50 rounded-xl p-6 backdrop-blur">
              <h2 className="text-xl font-bold mb-4">📋 Quote Summary</h2>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">You send:</span>
                  <span className="font-semibold">{quote.sell_amount} {quote.sell_asset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">You receive:</span>
                  <span className="font-semibold text-green-400">{quote.buy_amount.toFixed(6)} {quote.buy_asset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Rate:</span>
                  <span>1 {quote.sell_asset} = {quote.rate.toFixed(6)} {quote.buy_asset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Fee:</span>
                  <span className="text-orange-400">{quote.fee_amount} {quote.fee_currency || 'USDT'} ({quote.fee_percent}%)</span>
                </div>
                <div className="border-t border-gray-700 pt-3 mt-3">
                  <p className="text-xs text-gray-500">
                    ⏱️ Quote expires at: {new Date(quote.expires_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>

              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  📍 BTC Withdrawal Address
                </label>
                <input
                  type="text"
                  value={withdrawalAddress}
                  onChange={(e) => setWithdrawalAddress(e.target.value)}
                  placeholder="Enter your BTC address"
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white font-mono text-sm"
                />
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={reset}
                  className="flex-1 py-3 px-4 bg-gray-700 rounded-lg font-semibold hover:bg-gray-600 transition-all"
                >
                  ✕ Cancel
                </button>
                <button
                  onClick={createOrder}
                  disabled={loading || !withdrawalAddress}
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg font-semibold hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? "Creating..." : "✅ Confirm Order"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Success */}
        {step === "success" && order && (
          <div className="space-y-6">
            <div className="bg-green-900/30 border border-green-500 rounded-xl p-6 backdrop-blur text-center">
              <div className="text-5xl mb-4">🎉</div>
              <h2 className="text-2xl font-bold text-green-400 mb-2">Order Created!</h2>
              <p className="text-gray-400 text-sm mb-6">Order ID: <span className="font-mono text-white">{order.id}</span></p>

              <div className="bg-gray-800/50 rounded-lg p-4 text-left space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-yellow-400 font-semibold">{order.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Send:</span>
                  <span>{order.sell_amount} {order.sell_asset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Receive:</span>
                  <span className="text-green-400">{order.buy_amount.toFixed(6)} {order.buy_asset}</span>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-900/30 border border-blue-500 rounded-lg">
                <p className="text-sm text-blue-300">
                  📬 Please send <strong>{order.sell_amount} USDT</strong> to the address provided by the bot.
                  Your BTC will be sent to your withdrawal address after confirmation.
                </p>
              </div>

              <button
                onClick={reset}
                className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all"
              >
                🔄 Create New Order
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-xs text-gray-500">
          <p>Powered by CryptoBroker Engine v0.4</p>
          <p className="mt-1">Non-custodial • Secure • Fast</p>
        </div>
      </div>
    </main>
  );
}
