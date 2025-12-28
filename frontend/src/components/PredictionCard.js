export default function PredictionCard({ data, selectedCoin, currency = "INR", exchangeRate = 83.12 }) {
  if (!data) {
    return (
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 shadow-2xl text-center text-purple-300">
        <svg className="w-16 h-16 text-purple-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-lg">Select an asset and date to view predictions</p>
      </div>
    );
  }

  // Check if this is a precious metal (gold/silver)
  const isPreciousMetal = ['gold', 'silver'].includes(data.asset?.toLowerCase() || selectedCoin?.toLowerCase());
  const TROY_OZ_TO_GRAMS = 31.1035;

  const formatCurrency = (amountUSD) => {
    // Convert to per gram for gold/silver
    const displayAmount = isPreciousMetal ? amountUSD / TROY_OZ_TO_GRAMS : amountUSD;

    if (currency === "INR") {
      const inr = displayAmount * exchangeRate;
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
      }).format(inr);
    } else {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 2
      }).format(displayAmount);
    }
  };

  const getUnitLabel = () => {
    if (isPreciousMetal) {
      return "per gram";
    }
    return "";
  };

  const currentPrice = currency === "INR" ? data.current_price_inr : data.current_price;
  const expectedPrice = currency === "INR" ? data.q50_inr : data.q50;
  const changePercent = ((expectedPrice - currentPrice) / currentPrice * 100).toFixed(2);
  const isPositive = parseFloat(changePercent) >= 0;

  const formatDate = (dateStr) => {
    if (!dateStr) return "Next Day";
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20 shadow-2xl">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-xl mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold capitalize">
              {data.asset?.toUpperCase() || selectedCoin?.toUpperCase() || 'Unknown'}
            </h2>
            <p className="text-purple-100 mt-1">
              Prediction for {formatDate(data.targetDate)}
            </p>
            {data.daysAhead && (
              <p className="text-sm text-purple-100 mt-1">
                ({data.daysAhead} {data.daysAhead === 1 ? 'day' : 'days'} ahead)
              </p>
            )}
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold flex items-center justify-end ${
              isPositive ? 'text-green-300' : 'text-red-300'
            }`}>
              <span className="mr-2">{isPositive ? '📈' : '📉'}</span>
              {changePercent}%
            </div>
            <p className="text-sm text-purple-100 mt-1">Expected Change</p>
          </div>
        </div>
      </div>

      {/* Current Price */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-700 p-6 rounded-xl mb-6 border border-purple-500/30">
        <div className="text-center">
          <p className="text-purple-300 text-sm mb-2 font-semibold">
            Current Price {isPreciousMetal && <span className="text-yellow-300">{getUnitLabel()}</span>}
          </p>
          <p className="text-4xl font-bold text-white mb-2">
            {formatCurrency(data.current_price)}
          </p>
          {currency === "INR" && (
            <p className="text-purple-300 text-sm">
              ${isPreciousMetal ? (data.current_price / TROY_OZ_TO_GRAMS).toFixed(2) : data.current_price?.toLocaleString()}
              {isPreciousMetal && " per gram"}
            </p>
          )}
        </div>
      </div>

      {/* Prediction Ranges */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Conservative Q10 */}
        <div className="bg-gradient-to-br from-red-900/40 to-red-800/40 p-6 rounded-xl border-2 border-red-500/50 hover:border-red-400/70 transition">
          <div className="text-center">
            <p className="text-red-300 font-semibold mb-3 flex items-center justify-center">
              <span className="text-2xl mr-2">📉</span>
              Conservative (10%)
            </p>
            <p className="text-3xl font-bold text-red-200 mb-2">
              {formatCurrency(data.q10)}
            </p>
            {currency === "INR" && (
              <p className="text-red-300 text-sm">
                ${isPreciousMetal ? (data.q10 / TROY_OZ_TO_GRAMS).toFixed(2) : data.q10?.toLocaleString()}
                {isPreciousMetal && <span className="text-xs ml-1">/gram</span>}
              </p>
            )}
            <p className="text-xs text-red-400 mt-2">Worst case scenario</p>
          </div>
        </div>

        {/* Expected Q50 */}
        <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/40 p-6 rounded-xl border-2 border-blue-400/70 shadow-lg hover:border-blue-300 transition transform hover:scale-105">
          <div className="text-center">
            <p className="text-blue-200 font-semibold mb-3 flex items-center justify-center">
              <span className="text-2xl mr-2">📊</span>
              Expected (50%)
            </p>
            <p className="text-3xl font-bold text-blue-100 mb-2">
              {formatCurrency(data.q50)}
            </p>
            {currency === "INR" && (
              <p className="text-blue-200 text-sm">
                ${isPreciousMetal ? (data.q50 / TROY_OZ_TO_GRAMS).toFixed(2) : data.q50?.toLocaleString()}
                {isPreciousMetal && <span className="text-xs ml-1">/gram</span>}
              </p>
            )}
            <p className="text-xs text-blue-300 mt-2">Most likely outcome</p>
          </div>
        </div>

        {/* Optimistic Q90 */}
        <div className="bg-gradient-to-br from-green-900/40 to-green-800/40 p-6 rounded-xl border-2 border-green-500/50 hover:border-green-400/70 transition">
          <div className="text-center">
            <p className="text-green-300 font-semibold mb-3 flex items-center justify-center">
              <span className="text-2xl mr-2">📈</span>
              Optimistic (90%)
            </p>
            <p className="text-3xl font-bold text-green-200 mb-2">
              {formatCurrency(data.q90)}
            </p>
            {currency === "INR" && (
              <p className="text-green-300 text-sm">
                ${isPreciousMetal ? (data.q90 / TROY_OZ_TO_GRAMS).toFixed(2) : data.q90?.toLocaleString()}
                {isPreciousMetal && <span className="text-xs ml-1">/gram</span>}
              </p>
            )}
            <p className="text-xs text-green-400 mt-2">Best case scenario</p>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
        <p className="text-sm text-yellow-200">
          <strong>💡 Note:</strong> These predictions use AI-powered quantile regression on historical data.
          {isPreciousMetal ? (
            <> Gold and silver prices are shown <strong>per gram</strong> for Indian users. </>
          ) : (
            <> Market prices are highly volatile. </>
          )}
          Always do your own research before making investment decisions.
          {currency === "INR" && ` Exchange rate: $1 = ₹${exchangeRate}`}
        </p>
      </div>
    </div>
  );
}