export default function CoinDropdown({ coins, selected, onChange }) {
  // Handle both string array and object array formats
  const getAssetId = (asset) => typeof asset === 'string' ? asset : asset.id;
  const getAssetDisplay = (asset) => {
    if (typeof asset === 'string') {
      return asset.replace(/-/g, ' ').toUpperCase();
    }
    return asset.name || asset.symbol || asset.id;
  };

  // Handle undefined or null coins array
  const assetsList = coins || [];

  return (
    <select
      value={selected}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    >
      <option value="">Select an asset</option>
      {assetsList.map((asset) => {
        const id = getAssetId(asset);
        const display = getAssetDisplay(asset);
        return (
          <option key={id} value={id}>
            {display}
          </option>
        );
      })}
    </select>
  );
}