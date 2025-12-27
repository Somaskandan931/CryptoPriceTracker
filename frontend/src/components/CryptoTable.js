export default function CryptoTable({ coins }) {
  return (
    <div className="overflow-x-auto bg-white rounded-xl shadow">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-3 text-left">Coin</th>
            <th className="p-3 text-right">Price ($)</th>
            <th className="p-3 text-right">24h Change</th>
            <th className="p-3 text-right">Market Cap</th>
          </tr>
        </thead>
        <tbody>
          {coins.map((coin) => (
            <tr key={coin.id} className="border-b hover:bg-gray-50">
              <td className="p-3 font-medium">{coin.name}</td>
              <td className="p-3 text-right">${coin.current_price}</td>
              <td
                className={`p-3 text-right font-semibold ${
                  coin.price_change_percentage_24h >= 0
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {coin.price_change_percentage_24h.toFixed(2)}%
              </td>
              <td className="p-3 text-right">
                ${coin.market_cap.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
