import { useEffect, useState } from "react";
import { fetchCoins, fetchPrediction } from "../services/api";
import CoinDropdown from "../components/CoinDropdown";
import PredictionCard from "../components/PredictionCard";
import PriceChart from "../components/PriceChart";
import { Calendar } from "lucide-react";

export default function Dashboard() {
  const [coins, setCoins] = useState([]);
  const [selectedCoin, setSelectedCoin] = useState("");
  const [predictionDate, setPredictionDate] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [currency, setCurrency] = useState("INR"); // INR or USD
  const USD_TO_INR = 83.12;

  // Fetch available coins on mount
  useEffect(() => {
    const loadCoins = async () => {
      try {
        setLoading(true);
        const res = await fetchCoins();
        console.log('🪙 Backend response:', res.data);

        // Handle different response formats
        let assetsList = [];
        if (res.data.assets) {
          assetsList = res.data.assets;
        } else if (res.data.coins) {
          // Fallback for old response format
          assetsList = res.data.coins;
        } else if (Array.isArray(res.data)) {
          // If response is directly an array
          assetsList = res.data;
        }

        console.log('📋 Available assets:', assetsList);

        setCoins(assetsList);

        if (assetsList.length > 0) {
          const firstAsset = assetsList[0];
          console.log('🎯 Selected first asset:', firstAsset);
          setSelectedCoin(firstAsset);
        } else {
          console.warn('⚠️ No assets returned from API');
          setError("No assets available. Please check if the backend is running and has data.");
        }
      } catch (err) {
        const errorMsg = err.response?.data?.detail || err.message || "Failed to load assets";
        setError(`Failed to load assets: ${errorMsg}`);
        console.error('❌ Error loading assets:', {
          error: err,
          response: err.response?.data,
          status: err.response?.status
        });
        // Set empty array to prevent map errors
        setCoins([]);
      } finally {
        setLoading(false);
      }
    };

    loadCoins();
  }, []);

  const calculateDaysAhead = (targetDate) => {
    if (!targetDate) return 1;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const target = new Date(targetDate);
    target.setHours(0, 0, 0, 0);
    const diffTime = target - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(1, Math.min(30, diffDays));
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30);
    return maxDate.toISOString().split('T')[0];
  };

  const loadPrediction = async (coin, targetDate = null, silent = false) => {
    try {
      if (!silent) setLoading(true);
      setError(null);

      const daysAhead = calculateDaysAhead(targetDate);
      console.log('🔮 Requesting prediction for:', coin, 'days ahead:', daysAhead);

      const res = await fetchPrediction(coin, daysAhead);
      console.log('✅ Prediction received:', res.data);

      // Add INR conversion
      const predictionWithINR = {
        ...res.data,
        current_price_inr: res.data.current_price * USD_TO_INR,
        q10_inr: res.data.q10 * USD_TO_INR,
        q50_inr: res.data.q50 * USD_TO_INR,
        q90_inr: res.data.q90 * USD_TO_INR,
        daysAhead: daysAhead,
        targetDate: targetDate
      };

      setPrediction(predictionWithINR);
      setLastUpdate(new Date());
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to load prediction";
      console.error('❌ Prediction error:', {
        coin: coin,
        status: err.response?.status,
        detail: err.response?.data?.detail,
        fullError: err.response?.data
      });
      setError(errorMsg);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const handlePredictionRequest = () => {
    if (!selectedCoin) {
      setError("Please select an asset");
      return;
    }

    if (!predictionDate) {
      setError("Please select a prediction date");
      return;
    }

    const daysAhead = calculateDaysAhead(predictionDate);
    if (daysAhead < 1) {
      setError("Please select a future date");
      return;
    }

    loadPrediction(selectedCoin, predictionDate);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDE2YzAtNi42MjcgNS4zNzMtMTIgMTItMTJzMTIgNS4zNzMgMTIgMTItNS4zNzMgMTItMTIgMTItMTItNS4zNzMtMTItMTJ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-20"></div>

      <div className="relative max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-3 tracking-tight">
          MarketIQ India
          </h1>
          <p className="text-purple-300 text-lg">AI-Powered Quantile Regression Analysis</p>
          <div className="flex items-center justify-center gap-2 mt-4 text-purple-400 text-sm">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/50 rounded-xl p-4 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-semibold text-red-400">Error</p>
                <p className="text-sm text-red-300">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="mb-8 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 shadow-2xl">
          <div className="grid md:grid-cols-3 gap-6">
            {/* Coin Selector */}
            <div>
              <label className="block text-sm font-semibold text-purple-300 mb-3">
                Select Asset
              </label>
              <CoinDropdown
                coins={coins}
                selected={selectedCoin}
                onChange={setSelectedCoin}
              />
            </div>

            {/* Date Selector */}
            <div>
              <label className="block text-sm font-semibold text-purple-300 mb-3">
                <Calendar className="inline w-4 h-4 mr-1" />
                Prediction Date
              </label>
              <input
                type="date"
                value={predictionDate}
                onChange={(e) => setPredictionDate(e.target.value)}
                min={getMinDate()}
                max={getMaxDate()}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
              />
              <p className="text-xs text-purple-300 mt-1">
                Select a date up to 30 days ahead
              </p>
            </div>

            {/* Currency Toggle */}
            <div>
              <label className="block text-sm font-semibold text-purple-300 mb-3">
                Display Currency
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrency("INR")}
                  className={`flex-1 px-4 py-2 rounded-lg font-semibold transition ${
                    currency === "INR"
                      ? "bg-purple-600 text-white"
                      : "bg-white/20 text-purple-300 hover:bg-white/30"
                  }`}
                >
                  ₹ INR
                </button>
                <button
                  onClick={() => setCurrency("USD")}
                  className={`flex-1 px-4 py-2 rounded-lg font-semibold transition ${
                    currency === "USD"
                      ? "bg-purple-600 text-white"
                      : "bg-white/20 text-purple-300 hover:bg-white/30"
                  }`}
                >
                  $ USD
                </button>
              </div>
              <p className="text-xs text-purple-300 mt-1">
                Rate: $1 = ₹{USD_TO_INR}
              </p>
            </div>
          </div>

          {/* Predict Button */}
          <button
            onClick={handlePredictionRequest}
            disabled={loading || !selectedCoin || !predictionDate}
            className="w-full mt-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-4 rounded-lg hover:from-purple-700 hover:to-blue-700 transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Predicting...
              </span>
            ) : (
              '🔮 Get AI Prediction'
            )}
          </button>
        </div>

        {loading && !prediction ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent"></div>
            <p className="mt-6 text-purple-300 text-lg font-medium">Loading predictions...</p>
          </div>
        ) : (
          <div className="space-y-6">
            <PredictionCard
              data={prediction}
              selectedCoin={selectedCoin}
              currency={currency}
              exchangeRate={USD_TO_INR}
            />
            <PriceChart
              data={prediction?.history}
              prediction={prediction}
              currency={currency}
              exchangeRate={USD_TO_INR}
            />
          </div>
        )}
      </div>
    </div>
  );
}