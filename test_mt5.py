import MetaTrader5 as mt5

print("Initializing...")
if not mt5.initialize():
    print("MT5 Init Failed:", mt5.last_error())
else:
    print("MT5 Connected ✅")
    print("Terminal Info:", mt5.terminal_info())
    print("Version:", mt5.version())
    mt5.shutdown()
