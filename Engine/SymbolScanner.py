# SymbolScanner.py - SAFE VERSION for all brokers

import json
import MetaTrader5 as mt5


def safe_get(obj, attr):
    """Return attribute if exists, else None."""
    return getattr(obj, attr, None)


def scan_symbols(output_file="symbols.json"):
    print("✅ Initializing MT5 Connection...")

    if not mt5.initialize():
        print("❌ MT5 initialization failed!")
        return

    all_symbols = mt5.symbols_get()
    print(f"✅ Total symbols found: {len(all_symbols)}")

    results = []

    for sym in all_symbols:
        symbol = sym.name

        # Select symbol
        mt5.symbol_select(symbol, True)

        info = mt5.symbol_info(symbol)
        if info is None:
            continue

        if not info.visible:
            continue

        # SAFE extraction using safe_get()
        data = {
            "symbol": symbol,
            "digits": safe_get(info, "digits"),
            "spread": safe_get(info, "spread"),
            "volume_min": safe_get(info, "volume_min"),
            "volume_max": safe_get(info, "volume_max"),
            "volume_step": safe_get(info, "volume_step"),
            "trade_contract_size": safe_get(info, "trade_contract_size"),
            "freeze_level": safe_get(info, "freeze_level"),
            "margin_initial": safe_get(info, "margin_initial"),
            "margin_maintenance": safe_get(info, "margin_maintenance"),
            "point": safe_get(info, "point"),
            "is_tradable": safe_get(info, "trade_mode") == mt5.SYMBOL_TRADE_MODE_FULL,
        }

        results.append(data)

    # Save results
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"✅ Scan complete! Saved to {output_file}")
    mt5.shutdown()


def main():
    print("🔍 Running Symbol Scanner...")
    scan_symbols()


if __name__ == "__main__":
    main()
