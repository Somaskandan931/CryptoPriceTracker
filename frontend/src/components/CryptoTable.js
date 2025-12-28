export default function CryptoTable({ coins }) {
  if (!coins || coins.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No cryptocurrency data available
      </div>
    );
  }

  return (
    <div className="overflow-x-auto bg-white rounded-xl shadow-lg mt-4">
      <table className="min-w-full text-sm">
        <thead className="bg-gradient-to-r from-gray-100 to-gray-200">
          <tr>
            <th className="p-4 text-left font-semibold text-gray-700">Coin</th>
            <th className="p-4 text-right font-semibold text-gray-700">Price ($)</th>
            <th className="p-4 text-right font-semibold text-gray-700">24h Change</th>
            <th className="p-4 text-right font-semibold text-gray-700">Market Cap</th>
          </tr>
        </thead>
        <tbody>
          {coins.map((coin) => (
            <tr key={coin.id} className="border-b border-gray-200 hover:bg-blue-50 transition-colors">
              <td className="p-4 font-medium text-gray-900">{coin.name}</td>
              <td className="p-4 text-right font-semibold text-gray-800">
                ${coin.current_price?.toLocaleString() || 'N/A'}
              </td>
              <td className={`p-4 text-right font-bold ${
                coin.price_change_percentage_24h >= 0
                  ? "text-green-600"
                  : "text-red-600"
              }`}>
                {coin.price_change_percentage_24h
                  ? `${coin.price_change_percentage_24h.toFixed(2)}%`
                  : 'N/A'}
              </td>
              <td className="p-4 text-right text-gray-700">
                ${coin.market_cap?.toLocaleString() || 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}