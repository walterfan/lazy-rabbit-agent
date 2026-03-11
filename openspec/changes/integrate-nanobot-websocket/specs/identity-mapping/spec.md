## ADDED Requirements

### Requirement: lazy-rabbit maps nanobot identities to local users

The system SHALL maintain a mapping between nanobot identities `(channel, chat_id, sender_id)` and lazy-rabbit user accounts.

#### Scenario: First message from unknown identity triggers auto-creation

- **WHEN** a `chat.request` arrives with `(channel: "telegram", chat_id: "12345", sender_id: "12345")`
- **AND** no mapping exists for this identity
- **THEN** the system creates a new lazy-rabbit user with a generated username (e.g., `nb_telegram_12345`)
- **AND** creates an identity mapping record
- **AND** processes the chat request with the new user

#### Scenario: Subsequent messages use existing mapping

- **WHEN** a `chat.request` arrives with a previously mapped identity
- **THEN** the system resolves the existing lazy-rabbit user
- **AND** processes the request in that user's context (sessions, notes, goals, etc.)

#### Scenario: Multiple nanobot identities can map to one lazy-rabbit user

- **WHEN** a user links their Telegram and Feishu accounts to the same lazy-rabbit user
- **THEN** messages from both channels share the same user data (sessions, notes, goals)

### Requirement: Identity mapping is stored persistently

The system SHALL store identity mappings in the database.

#### Scenario: Mapping survives server restart

- **WHEN** the server restarts
- **THEN** all previously created identity mappings are preserved
- **AND** returning users are recognized without re-creation

#### Scenario: Mapping table schema

- **GIVEN** the `nanobot_identity_mapping` table
- **THEN** it contains columns:
  - `id`: UUID primary key
  - `channel`: string (e.g., "telegram", "feishu")
  - `chat_id`: string (platform-specific chat identifier)
  - `sender_id`: string (platform-specific user identifier)
  - `user_id`: UUID foreign key to users table
  - `display_name`: optional string (user's display name from the platform)
  - `created_at`: timestamp
  - `last_seen_at`: timestamp (updated on each message)

### Requirement: Admin can manage identity mappings

The system SHALL provide admin endpoints to view and manage identity mappings.

#### Scenario: Admin lists all mappings

- **WHEN** an admin GETs `/api/v1/admin/nanobot-identities`
- **THEN** the system returns all identity mappings with user details

#### Scenario: Admin deletes a mapping

- **WHEN** an admin DELETEs `/api/v1/admin/nanobot-identities/{id}`
- **THEN** the mapping is removed (the user account remains)

#### Scenario: Admin links an existing user

- **WHEN** an admin POSTs `/api/v1/admin/nanobot-identities` with `{channel, chat_id, sender_id, user_id}`
- **THEN** the system creates a mapping to the specified existing user (instead of auto-creating)
