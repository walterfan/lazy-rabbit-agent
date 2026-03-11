## ADDED Requirements

### Requirement: lazy-rabbit agents can push notifications through nanobot

The system SHALL allow agents to send proactive notifications to users via their nanobot-connected channels.

#### Scenario: Reminder agent sends a push notification

- **WHEN** a reminder triggers for a user who has a nanobot identity mapping
- **THEN** the system sends a `push.notification` message over the WebSocket
- **AND** the notification includes the target `channel`, `chat_id`, and `content`

#### Scenario: Push notification to user with multiple channels

- **WHEN** a user has mappings for both Telegram and Feishu
- **THEN** the system sends the notification to the user's preferred channel (or the most recently active one)

#### Scenario: Push notification when nanobot is disconnected

- **WHEN** a push notification is triggered but no nanobot WebSocket connection is active
- **THEN** the notification is queued in memory (up to 100 per user)
- **AND** delivered when a nanobot connection is re-established

#### Scenario: Queued notifications expire

- **WHEN** queued notifications are older than 24 hours
- **THEN** they are discarded (stale reminders are not useful)

### Requirement: Push notifications support delivery acknowledgment

The system SHALL track whether push notifications were successfully delivered.

#### Scenario: Successful delivery acknowledged

- **WHEN** nanobot delivers a push notification to the target channel
- **THEN** nanobot sends a `push.ack` with `{notification_id, delivered: true}`
- **AND** lazy-rabbit marks the notification as delivered

#### Scenario: Failed delivery reported

- **WHEN** nanobot cannot deliver a push notification (channel unavailable, user blocked bot, etc.)
- **THEN** nanobot sends a `push.ack` with `{delivered: false, reason: "..."}`
- **AND** lazy-rabbit logs the failure for observability

### Requirement: Push notification service is accessible to all agents

The system SHALL provide a `PushService` that any agent or service can use to send notifications.

#### Scenario: Agent uses PushService API

- **GIVEN** the `PushService` interface
- **THEN** agents can call:
  ```python
  await push_service.notify(
      user_id=uuid,
      content="Time to study! You have a 5-day streak 🔥",
      priority="normal",  # normal | high
  )
  ```
- **AND** the service resolves the user's nanobot identity and sends via WebSocket

#### Scenario: PushService with no nanobot mapping

- **WHEN** `notify()` is called for a user with no nanobot identity mapping
- **THEN** the call returns `False` (notification not sent)
- **AND** no error is raised
