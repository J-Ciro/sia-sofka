export class SchedulePageMinimal {
  constructor(page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/horarios');
    await this.page.waitForLoadState('networkidle');
    console.log('Minimal goto() called successfully');
  }
}