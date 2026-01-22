export class SchedulePage {
  constructor(page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto("/horarios");
    await this.page.waitForLoadState("networkidle");
    console.log("SchedulePage goto called successfully");
  }
}
