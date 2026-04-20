const { test, expect } = require('@playwright/test');

// This small E2E checks search + tag filter flows
test('filter flow updates URL and applies filters', async ({ page }) => {
  await page.goto('http://localhost:5000/mezmur');

  // wait for search input
  const search = page.locator('#searchInput');
  await expect(search).toBeVisible();

  await search.fill('love');
  await page.waitForTimeout(500);

  // check URL updated
  await expect(page).toHaveURL(/\?q=love/);

  // toggle first available tag (desktop or mobile depending on viewport)
  const firstTag = page.locator('.tag-list .form-check-input').first();
  if (await firstTag.count() > 0) {
    await firstTag.click();
    await page.waitForTimeout(300);
    // check that the active filters container has a chip with 'love' or tag
    await expect(page.locator('#activeFiltersContainer')).toBeVisible();
    
    // Save button should be visible in the toolbar
    const saveBtn = page.locator('#saveFilterBtn')
    await expect(saveBtn).toBeVisible()
    
    // When unauthenticated clicking Save should redirect to login with next param
    await saveBtn.click()
    await expect(page).toHaveURL(/\/login\?next=/)
  }
});
