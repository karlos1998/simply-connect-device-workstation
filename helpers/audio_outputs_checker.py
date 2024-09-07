import pyudev

# Utwórz kontekst udev
context = pyudev.Context()

# Utwórz monitor dla urządzeń
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

# Nasłuchuj na zdarzenia w trybie blokującym
for device in iter(monitor.poll, None):
    if device.action == 'add':
        print(f"Podłączono urządzenie: {device}")
    elif device.action == 'remove':
        print(f"Odłączono urządzenie: {device}")
