# Changelog

All notable changes to this project will be documented in this file.

## [2.0] - 2026-02-01

### Changed
- **BREAKING:** Migrated from `python-telegram-bot` to `aiogram 3.24.0`
- Refactored `handlers/` to `routers/` using aiogram Router system
- Replaced ConversationHandler with aiogram FSM (Finite State Machine)
- Updated keyboard building to use InlineKeyboardBuilder
- Modernized async architecture for better performance

### Added
- Migration guide (MIGRATION_v2.0.md)
- Changelog file
- Release notes (RELEASE_NOTES_v2.0.md)

### Improved
- Code structure is now more modular and maintainable
- Better type hints and cleaner syntax
- Improved memory efficiency
- Faster update processing

### Technical
- Removed python-telegram-bot dependency
- Added aiogram 3.24.0 dependency
- Updated all handler decorators to router decorators
- Implemented FSM states for API configuration flow
- Removed unused helper functions (chunk_buttons, get_back_button)

## [1.0.6] - 2026-01-31

### Added
- VM list now shows vCPU, RAM, Storage, and OS information
- VM status indicators: ● Running, ○ Stopped, ◌ Suspended
- Detailed VM info with real-time resource usage:
  - IPv4 and IPv6 addresses
  - RAM usage with progress bar
  - Disk usage with progress bar
  - Bandwidth usage with progress bar
  - Port forwarding rules count
  - OS and virtualization type
- OS mapping for common distros (Ubuntu, Debian, AlmaLinux, CentOS)

### Improved
- VM details page now shows comprehensive resource statistics
- Better visual representation with progress bars
- Enhanced error handling for missing stats

## [1.0.5] - 2026-01-30

### Added
- Auto-update feature with GitHub version checking
- `start.sh` - Auto-setup script with dependency checking
- `update.sh` - Update and restart script
- Update notification in main menu when new version available
- "Update Bot" button for one-click updates
- Automatic installation of python3, python3-venv, pip, screen
- Support for PM2 and screen process managers

### Improved
- README with quick start instructions
- Setup process is now fully automated

## [1.0.4] - 2026-01-29

### Added
- Informative descriptions on all pages
- Footer with version and author on all pages
- Better navigation with consistent Back/Home buttons

### Fixed
- MarkdownV2 escaping for API names with special characters

## [1.0.3] - 2026-01-28

### Added
- VM management features
- VM listing with status indicators
- VM details page with VPS ID, IP, and API info

### Improved
- Error handling for API connections
- Better user feedback messages

## [1.0.2] - 2026-01-27

### Added
- API management features
- Set default API
- Delete API
- List APIs with default indicator

### Improved
- Database schema for default API flag
- API selection flow for multiple APIs

## [1.0.1] - 2026-01-26

### Added
- API configuration with validation
- Connection testing before saving
- Detailed error messages for connection failures

### Fixed
- HTTPS validation for API URLs
- Input validation for API credentials

## [1.0.0] - 2026-01-25

### Added
- Initial release
- Basic bot structure with command handlers
- SQLite database for API storage
- Virtualizor API client
- Main menu with navigation
- About page
- Colored console logging
- Startup banner

### Features
- Add API configuration
- Store multiple API profiles
- Secure credential storage
- User authentication
- Auto-delete user messages for clean chat

---

**Format:** Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
**Versioning:** [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
