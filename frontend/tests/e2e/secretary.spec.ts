/**
 * E2E tests for Personal Secretary feature.
 *
 * These tests verify the complete user flow from login to chat interaction.
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';
const API_URL = process.env.E2E_API_URL || 'http://localhost:8000';

// Test user credentials
const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
};

/**
 * Helper to login and navigate to secretary page.
 */
async function loginAndNavigate(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/signin`);

  // Fill in login form
  await page.fill('input[type="email"]', TEST_USER.email);
  await page.fill('input[type="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');

  // Wait for redirect to dashboard
  await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 10000 });

  // Navigate to secretary
  await page.goto(`${BASE_URL}/secretary`);
  await page.waitForLoadState('networkidle');
}

test.describe('Personal Secretary - Chat Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Set up API mocking if needed
    await page.route(`${API_URL}/api/v1/secretary/**`, async (route) => {
      // Pass through to real API or mock
      await route.continue();
    });
  });

  test('should display chat interface', async ({ page }) => {
    await loginAndNavigate(page);

    // Verify chat components are visible
    await expect(page.locator('[data-testid="chat-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="session-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="tool-list"]')).toBeVisible();
  });

  test('should send a message and receive response', async ({ page }) => {
    await loginAndNavigate(page);

    // Type a message
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('Hello, what can you help me with?');

    // Send message
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await expect(page.locator('[data-testid="message-assistant"]').first()).toBeVisible({
      timeout: 30000,
    });

    // Verify response contains text
    const responseText = await page.locator('[data-testid="message-assistant"]').first().textContent();
    expect(responseText).toBeTruthy();
  });

  test('should start a new session', async ({ page }) => {
    await loginAndNavigate(page);

    // Click new session button
    await page.click('[data-testid="new-session-button"]');

    // Verify empty chat
    await expect(page.locator('[data-testid="empty-chat-message"]')).toBeVisible();
  });

  test('should display available tools', async ({ page }) => {
    await loginAndNavigate(page);

    // Check tool list
    const toolList = page.locator('[data-testid="tool-list"]');
    await expect(toolList).toBeVisible();

    // Verify some tools are listed
    await expect(page.locator('[data-testid="tool-item"]').first()).toBeVisible();
  });
});

test.describe('Personal Secretary - Learning Flow', () => {
  test('should learn a word', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to learn a word
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('请帮我学习单词 "algorithm"');
    await page.click('[data-testid="send-button"]');

    // Wait for response with learning content
    await expect(page.locator('[data-testid="message-assistant"]').first()).toBeVisible({
      timeout: 30000,
    });

    // Check for save button
    const saveButton = page.locator('[data-testid="save-learning-button"]');
    if (await saveButton.isVisible()) {
      await saveButton.click();
      await expect(page.locator('[data-testid="learning-saved-toast"]')).toBeVisible();
    }
  });

  test('should learn a topic', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to learn a topic
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('请帮我学习 Kubernetes 的基本概念');
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await expect(page.locator('[data-testid="message-assistant"]').first()).toBeVisible({
      timeout: 60000,
    });
  });
});

test.describe('Personal Secretary - Task Management', () => {
  test('should create a task', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to create a task
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('帮我创建一个任务：完成项目报告，截止日期明天');
    await page.click('[data-testid="send-button"]');

    // Wait for response confirming task creation
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });

    const response = await page.locator('[data-testid="message-assistant"]').last().textContent();
    expect(response).toMatch(/任务|创建|完成/);
  });

  test('should list tasks', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to list tasks
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('查看我的待办任务');
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });
  });
});

test.describe('Personal Secretary - Note Management', () => {
  test('should save a note', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to save a note
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('帮我记录一条笔记：今天学习了 E2E 测试的写法');
    await page.click('[data-testid="send-button"]');

    // Wait for response confirming note saved
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });

    const response = await page.locator('[data-testid="message-assistant"]').last().textContent();
    expect(response).toMatch(/笔记|保存|记录/);
  });

  test('should search notes', async ({ page }) => {
    await loginAndNavigate(page);

    // First save a note
    let chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('保存笔记：Playwright E2E 测试框架');
    await page.click('[data-testid="send-button"]');
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });

    // Then search for it
    chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('搜索包含 Playwright 的笔记');
    await page.click('[data-testid="send-button"]');
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });
  });
});

test.describe('Personal Secretary - Reminder Management', () => {
  test('should create a reminder', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to create a reminder
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('提醒我明天下午3点开会');
    await page.click('[data-testid="send-button"]');

    // Wait for response confirming reminder
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });

    const response = await page.locator('[data-testid="message-assistant"]').last().textContent();
    expect(response).toMatch(/提醒|设置/);
  });

  test('should list upcoming reminders', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask for upcoming reminders
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('查看我今天的提醒');
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });
  });
});

test.describe('Personal Secretary - Utility Tools', () => {
  test('should calculate expression', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask to calculate
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('计算 (15 + 25) * 2');
    await page.click('[data-testid="send-button"]');

    // Wait for response with result
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });

    const response = await page.locator('[data-testid="message-assistant"]').last().textContent();
    expect(response).toMatch(/80/);
  });

  test('should get current datetime', async ({ page }) => {
    await loginAndNavigate(page);

    // Ask for current time
    const chatInput = page.locator('[data-testid="chat-input"] textarea');
    await chatInput.fill('现在几点了？');
    await page.click('[data-testid="send-button"]');

    // Wait for response with time
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 30000 });

    const response = await page.locator('[data-testid="message-assistant"]').last().textContent();
    expect(response).toMatch(/\d{1,2}:\d{2}/);
  });
});

test.describe('Learning History Page', () => {
  test('should display learning records', async ({ page }) => {
    await page.goto(`${BASE_URL}/signin`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 10000 });

    // Navigate to learning history
    await page.goto(`${BASE_URL}/learning`);
    await page.waitForLoadState('networkidle');

    // Verify page elements
    await expect(page.locator('[data-testid="learning-records-list"]')).toBeVisible();
    await expect(page.locator('[data-testid="learning-statistics"]')).toBeVisible();
  });

  test('should filter by type', async ({ page }) => {
    await page.goto(`${BASE_URL}/signin`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 10000 });

    await page.goto(`${BASE_URL}/learning`);
    await page.waitForLoadState('networkidle');

    // Click word filter
    await page.click('[data-testid="filter-word"]');
    await page.waitForLoadState('networkidle');

    // Verify filter applied
    await expect(page.locator('[data-testid="filter-word"]')).toHaveClass(/active/);
  });

  test('should search records', async ({ page }) => {
    await page.goto(`${BASE_URL}/signin`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${BASE_URL}/dashboard`, { timeout: 10000 });

    await page.goto(`${BASE_URL}/learning`);
    await page.waitForLoadState('networkidle');

    // Search for something
    await page.fill('[data-testid="search-input"]', 'test');
    await page.press('[data-testid="search-input"]', 'Enter');

    // Wait for search results
    await page.waitForLoadState('networkidle');
  });
});
