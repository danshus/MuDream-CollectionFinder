# MuDream Collection Finder

A powerful desktop application to help MuDream Online players find and track collection items in the game's marketplace.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎮 About

MuDream Collection Finder is a Windows application designed for [MuDream Online](https://mudream.online) private server players. It automates the process of searching the marketplace for specific collection items based on your unique collection requirements, complete with smart price filtering and sorting.

### Key Features

- ✅ **Multi-Set Configuration** - Configure unlimited armor sets with their specific excellent option requirements
- ✅ **Smart Price Filtering** - Filter items by maximum prices across all currency types (Jewels, Zen, DC)
- ✅ **Intelligent Price Sorting** - Items automatically sorted by value (cheapest first) using normalized pricing
- ✅ **Persistent Storage** - Your collection requirements are saved and auto-load on startup
- ✅ **Search Flexibility** - Search all sets at once or focus on a single set
- ✅ **Easy Market Access** - One-click market opening with search criteria copied to clipboard

## 📸 Screenshots

### Setup Collections Tab
Configure your unique collection requirements with an intuitive interface.

### Search Market Tab
Search and filter items with advanced price controls and instant results.

## 🚀 Installation

### Option 1: Download Executable (Easiest)

1. Download the latest `MuDreamCollectionFinder.exe` from [Releases](../../releases)
2. Run the executable - no installation required!

### Option 2: Run from Source

**Requirements:**
- Python 3.7 or higher
- pip (Python package manager)

**Steps:**

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mudream-collection-finder.git
cd mudream-collection-finder
```

2. Install dependencies:
```bash
pip install requests
```

3. Run the application:
```bash
python mudream_collection_finder.py
```

## 📖 How to Use

### Initial Setup (One-Time)

1. **Get Your Bearer Token**
   - Login to [mudream.online](https://mudream.online)
   - Press `F12` to open Developer Tools
   - Go to **Network** tab
   - Type `graphql` in the filter
   - Click on any item in the market
   - Find the request, click it, scroll to **Request Headers**
   - Copy the `authorization` value (starts with "Bearer")

2. **Configure Your Collections**
   - Open the app and go to **⚙️ Setup Collections** tab
   - Select an armor set from the dropdown
   - Check the required excellent options for each piece:
     - **MH** - Increase maximum life
     - **SD** - Increase maximum SD
     - **DD** - Damage decrease
     - **REF** - Reflect Damage
     - **DSR** - Defense success rate
     - **ZEN** - Increase Zen drop rate
   - Click **💾 Save/Update This Set**
   - Repeat for all your collection sets

### Searching the Market

1. Go to **🔍 Search Market** tab
2. Paste your Bearer Token (from initial setup)
3. Select which set to search (or "All Sets")
4. **(Optional)** Set maximum price filters:
   - Jewels: Bless, Soul, Life, Chaos, Creation
   - Zen: Game currency
   - DC: Dream Credits
5. Click **🔍 Search Selected Set(s)**
6. Results appear sorted by price (cheapest first!)

### Understanding Results

Each result shows:
- **Item name** with index number
- **Gear Score** (if applicable)
- **Price** in various currencies
- **Normalized Value** - Calculated using:
  - Life/Chaos = 1.0
  - Creation = 0.5
  - Bless/Soul = 0.25
  - DC = 0.125 (8 DC = 1 Life/Chaos)
- **Search criteria** - Click to copy, then apply manually in market
- **[Open Market]** button - Opens market in your browser

## 💰 Price Filtering Logic

The app uses intelligent price filtering:

### Jewel Items
- Items priced in jewels (Bless, Soul, Life, Chaos, Creation)
- **Pass:** All jewels are within your set limits
- **Fail:** Item costs a jewel you didn't set a limit for
- **Fail:** Any jewel exceeds your limit

**Example:**
```
Your Filters: Life ≤ 50, Chaos ≤ 30

✅ Item A: Life 40, Chaos 20 (PASS - within limits)
❌ Item B: Life 60, Chaos 20 (FAIL - Life exceeds limit)
❌ Item C: Life 40, Chaos 20, Bless 10 (FAIL - no Bless limit set)
```

### DC/Zen Items
- Simple threshold filtering
- Items priced at or below your limit pass

### Multiple Categories
- Set filters for different categories to see items from any matching category
- Leave empty for no price limit

## 🛠️ Configuration File

Your collection requirements are saved in `collection_config.json` in the same folder as the app.

**Example structure:**
```json
{
  "sets": {
    "Leather": {
      "helm": ["iml", "imsd"],
      "armor": ["dd", "rd"],
      "pants": ["dsr"],
      "gloves": ["iml"],
      "boots": ["izdr"]
    },
    "Vine": {
      "helm": ["iml", "dd"],
      "armor": ["imsd", "rd"]
    }
  }
}
```

You can manually edit this file if needed, but it's recommended to use the app interface.

## 🔧 Troubleshooting

### "Failed to fetch data" Error
- Your Bearer Token may have expired
- Solution: Get a fresh token (see Initial Setup step 1)
- Tokens typically last 4+ hours

### No Results Appear
- Check if you configured the correct excellent options for that set
- Verify your price filters aren't too restrictive
- Try searching without price filters first

### "No collections configured" Error
- Go to Setup Collections tab
- Configure at least one armor set with requirements
- Save before searching

### App Won't Start
- Ensure you have Python 3.7+ installed (if running from source)
- Install required dependencies: `pip install requests`
- Check that you're not running from a read-only location

## 🎯 Supported Armor Sets

All 44 MuDream armor sets are supported:

<details>
<summary>Click to expand full list</summary>

- Leather, Pad, Vine, Bronze, Silk, Bone, Scale, Wind
- Violent Wind, Sphinx, Brass, Spirit, Plate, Legendary
- Red Winged, Guardian, Dragon, Light Plate, Sacred Fire
- Ancient, Adamantine, Storm Crow, Storm Zahard, Black Dragon
- Demonic, Grand Soul, Holy Spirit, Dark Steel, Dark Phoenix
- Thunder Hawk, Great Dragon, Dark Soul, Hurricane, Red Spirit
- Dark Master, Storm Blitz, Piercing Grove, Dragon Knight
- Vengeance, Sylphid Ray, Volcano, Sunlight, Succubus, Phoenix Soul

</details>

## 📝 Technical Details

**Built with:**
- Python 3.7+
- tkinter (GUI)
- requests (API calls)
- threading (async operations)

**API:**
- GraphQL endpoint: `https://mudream.online/api/graphql`
- Authentication: Bearer token (JWT)

**Currency Codes:**
- `bless`, `soul`, `life`, `chaos`, `creat` (jewels)
- `zen` (game currency)
- `dc` (Dream Credits)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is not affiliated with, endorsed by, or connected to MuDream Online or its developers. It is a community-created tool for educational purposes. Use at your own risk.

## 🙏 Acknowledgments

- MuDream Online community
- All contributors and testers

## 📞 Support

- **Issues:** [GitHub Issues](../../issues)
- **Discord:** [MuDream Community](https://mudream.online)

---

**Made with ❤️ for the MuDream community**

*If this tool helped you complete your collections, consider giving it a ⭐!*