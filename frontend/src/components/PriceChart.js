import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, AreaChart, Area } from "recharts";

export default function PriceChart({ data, prediction, currency = "INR", exchangeRate = 83.12 }) {
  // Check if this is a precious metal
  const isPreciousMetal = prediction && ['gold', 'silver'].includes(prediction.asset?.toLowerCase());
  const TROY_OZ_TO_GRAMS = 31.1035;

  // Generate mock history data if not available
  const historyData = data || (prediction ? [
    { time: "Day 1", price: prediction.current_price * 0.95 },
    { time: "Day 2", price: prediction.current_price * 0.97 },
    { time: "Day 3", price: prediction.current_price * 0.98 },
    { time: "Day 4", price: prediction.current_price },
    { time: "Prediction", price: prediction.q50 }
  ] : []);

  if (!historyData || !Array.isArray(historyData) || historyData.length === 0) {
    return (
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 shadow-2xl text-center">
        <svg className="w-16 h-16 text-purple-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p className="text-purple-300 text-lg">No chart data available</p>
      </div>
    );
  }

  // Convert data to selected currency and per gram for precious metals
  const chartData = historyData.map(item => {
    const pricePerGram = isPreciousMetal ? item.price / TROY_OZ_TO_GRAMS : item.price;
    return {
      ...item,
      displayPrice: currency === "INR" ? pricePerGram * exchangeRate : pricePerGram
    };
  });

  const formatCurrency = (value) => {
    if (currency === "INR") {
      return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
    }
    return `$${value.toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  };

  const currencySymbol = currency === "INR" ? "₹" : "$";

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-white">
          Price Trend & Prediction
          {isPreciousMetal && <span className="text-lg text-yellow-300 ml-2">(per gram)</span>}
        </h3>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-purple-300 text-sm">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span>Historical & Forecasted</span>
          </div>
          <div className="px-3 py-1 bg-purple-600/50 rounded-lg text-white text-sm font-semibold">
            {currencySymbol} {currency}
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
          <XAxis
            dataKey="time"
            stroke="#a78bfa"
            style={{ fontSize: '14px', fontWeight: '500' }}
          />
          <YAxis
            stroke="#a78bfa"
            style={{ fontSize: '14px', fontWeight: '500' }}
            tickFormatter={formatCurrency}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '12px',
              padding: '12px',
              backdropFilter: 'blur(10px)'
            }}
            labelStyle={{ color: '#c4b5fd', fontWeight: '600', marginBottom: '4px' }}
            itemStyle={{ color: '#fff', fontWeight: '700' }}
            formatter={(value) => {
              const displayValue = typeof value === 'number' ? formatCurrency(value) : value;
              return [displayValue, 'Price'];
            }}
          />
          <Area
            type="monotone"
            dataKey="displayPrice"
            stroke="#8b5cf6"
            strokeWidth={3}
            fill="url(#colorPrice)"
            dot={{ fill: '#8b5cf6', r: 5, strokeWidth: 2, stroke: '#fff' }}
            activeDot={{ r: 7, strokeWidth: 3, fill: '#8b5cf6', stroke: '#fff' }}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Chart Legend */}
      <div className="mt-6 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500"></div>
          <span className="text-purple-300">Price Trend</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-400 ring-2 ring-white"></div>
          <span className="text-purple-300">Data Points</span>
        </div>
        {currency === "INR" && (
          <div className="text-purple-300 text-xs">
            Exchange Rate: $1 = ₹{exchangeRate}
            {isPreciousMetal && <span className="ml-2">• Prices per gram</span>}
          </div>
        )}
      </div>
    </div>
  );
}