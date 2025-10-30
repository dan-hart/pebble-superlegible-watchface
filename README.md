# Superledgible

A minimalist Pebble watchface focused on maximum readability using the Atkinson Hyperlegible font.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Platforms](https://img.shields.io/badge/platforms-Aplite%20%7C%20Basalt%20%7C%20Chalk%20%7C%20Diorite%20%7C%20Emery-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Features

- **Maximum Size**: Time displayed as large as possible
- **Ultimate Simplicity**: Just the time, nothing else
- **Maximum Legibility**: Atkinson Hyperlegible font designed by Braille Institute
- **Auto Time Format**: Automatically detects and respects your system 12h/24h preference
- **Universal**: Works on all 5 Pebble platforms
- **Battery Efficient**: Updates only once per minute

## Screenshots

*Coming soon - screenshots of the watchface on different platforms*

## Installation

### From Pebble App Store
*Coming soon when published to the Pebble app store*

### Manual Installation

1. Download the `.pbw` file from the [Releases](https://github.com/yourusername/pebble-superledgible-watchface/releases) page
2. Open the Pebble app on your phone
3. Go to Settings → Apps
4. Tap "Install Watch App"
5. Select the downloaded `.pbw` file

### Building from Source

**Prerequisites**:
- [Nix package manager](https://nixos.org/download.html)
- [pebble.nix](https://github.com/Sorixelle/pebble.nix)

**Build Steps**:

```bash
# Clone the repository
git clone https://github.com/yourusername/pebble-superledgible-watchface.git
cd pebble-superledgible-watchface

# Build with Nix
nix-shell --run "pebble build"

# The .pbw file will be in build/
```

**Install to Emulator**:
```bash
nix-shell --run "pebble install --emulator basalt"
```

**Install to Physical Watch**:
```bash
nix-shell --run "pebble install --phone <IP_ADDRESS>"
```

## Configuration

No configuration required! Superledgible automatically:
- Detects your system time format preference (12h/24h)
- Optimizes display for your Pebble model
- Adapts to rectangular and round displays

Your Pebble's time format setting (in Date & Time settings) is automatically respected.

## Technical Details

**Font**: Atkinson Hyperlegible Regular
- Designed by Braille Institute specifically for legibility
- 48pt size optimized for Pebble's display
- Licensed under SIL Open Font License v1.1

**Supported Platforms**:
- Pebble (Aplite) - 144x168 Black & White
- Pebble Time (Basalt) - 144x168 Color
- Pebble Time Round (Chalk) - 180x180 Color, Round
- Pebble 2 (Diorite) - 144x168 Black & White
- Pebble Time 2 (Emery) - 200x228 Color

**Memory Usage**:
- Resources: 6-8KB (depending on platform)
- RAM: ~1KB
- Very efficient and lightweight

## Development

This project follows Pebble development best practices:
- Clean init/deinit pattern
- Proper resource management
- Platform-specific optimizations
- Battery-efficient updates
- Comprehensive documentation

See the [technical documentation](https://github.com/yourusername/pebble-superledgible-watchface/tree/main/docs) for detailed information on architecture and design decisions.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## Credits

- **Font**: [Atkinson Hyperlegible](https://brailleinstitute.org/freefont) by Braille Institute of America
- **Developer**: Dan Hart
- **SDK**: Pebble SDK 3 via [pebble.nix](https://github.com/Sorixelle/pebble.nix)

## License

- **Code**: MIT License (see LICENSE file)
- **Font**: SIL Open Font License v1.1 (see OFL.txt)

## Related Projects

- **Modern Citizen**: A comprehensive watchface with date, weather, and temperature

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: (your contact method)

---

**Superledgible** - Maximum readability, minimal complexity.
