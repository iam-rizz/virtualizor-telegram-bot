# Changelog

All notable changes to this project will be documented in this file.

## [2.3] - 2026-02-01

### Added
- **VM Power Controls** - Start, Stop, Restart, and Power Off VMs directly from Telegram
- Action buttons in VM details page based on VM status
- Automatic status detection for available actions
- Success/failure feedback for VM operations
- Auto-refresh after successful action

### Changed
- Removed emojis from button labels for cleaner interface
- Kept status indicators (● ○ ◌) for better visual recognition

### Features
- Start VM (when stopped)
- Stop VM (when running)
- Restart VM (when running)
- Power Off VM (when running)
- Retry option on failure
- Real-time action feedback

### Improved
- VM details page now includes power control buttons
- Better user experience with contextual actions
- Clear error messages for failed operations

## [2.2] - 2026-02-01

### Added
- **Batch Add APIs** feature for adding multiple API connections at once
- Support for bulk import with format: `name|url|key|password`
- Comprehensive validation for batch operations
- Detailed results showing success/failure for each API
- Maximum 10 APIs per batch for safety

### Features
- Add multiple APIs in one operation
- Format: One API per line with pipe separator
- Automatic validation and testing for each API
- Clear success/failure feedback
- Connection testing before saving

### Improved
- API Management menu reorganized for better UX
- Added "Batch Add" button alongside "Add API"
- Better error messages for batch operations

## [2.1] - 2026-02-01

### Added
- Case-insensitive API name uniqueness check
- Support for spaces in API names
- Maximum length validation (50 characters) for API names

### Changed
- API names now preserve original case (e.g., "Main Server" instead of "main-server")
- Updated name validation to allow spaces, letters, numbers, hyphens, and underscores
- Improved user-friendly display names throughout the interface

### Improved
- More natural and professional API name display
- Better validation messages with clearer examples
- Enhanced user experience for API naming

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
