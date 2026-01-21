/**
 * Page Object Model for Attendance Page
 * Encapsulates page interactions and selectors
 * 
 * Best Practices:
 * - Single Responsibility: One POM per page/component
 * - Encapsulation: Hide implementation details
 * - Reusability: Methods can be reused across tests
 * - Maintainability: Selectors in one place
 */

export class AttendancePage {
  /**
   * @param {import('@playwright/test').Page} page - Playwright page object
   */
  constructor(page) {
    this.page = page;
  }

  /**
   * Navigate to attendance page
   */
  async goto() {
    await this.page.goto('/attendance');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Create a new attendance session
   * @param {Object} sessionData - Session data
   * @param {string} sessionData.date - Session date (YYYY-MM-DD)
   * @param {string} sessionData.startTime - Start time (HH:MM)
   * @param {string} sessionData.endTime - End time (HH:MM)
   * @param {string} sessionData.description - Session description
   * @returns {Promise<boolean>} True if successful, false if error
   */
  async createSession({ date, startTime, endTime, description }) {
    // Fill date input
    await this.page.locator('input[type="date"]').fill(date);
    
    // Fill time inputs - there are two time inputs, first is start time, second is end time
    const timeInputs = this.page.locator('input[type="time"]');
    await timeInputs.nth(0).fill(startTime);
    await timeInputs.nth(1).fill(endTime);
    
    // Fill description if provided
    if (description) {
      await this.page.locator('input[placeholder*="Ej: Clase sobre funciones cuadráticas"]').fill(description);
    }
    
    // Click create session button
    await this.page.getByRole('button', { name: /crear sesión y comenzar/i }).click();
    
    // Wait for either success or error with longer timeout
    try {
      await Promise.race([
        this.page.getByText(/sesión.*creada.*exitosamente/i).waitFor({ timeout: 15000 }),
        this.page.getByText(/ya existe una sesión/i).waitFor({ timeout: 15000 }),
        this.page.getByText(/error|debe|no se puede/i).waitFor({ timeout: 15000 }),
        // Also wait for the student list to appear (success case)
        this.page.getByRole('heading', { name: /lista de estudiantes/i }).waitFor({ timeout: 15000 })
      ]);
    } catch (error) {
      console.log('Timeout waiting for session creation response');
    }
    
    // Check if session was created successfully (student list appears)
    const studentListVisible = await this.page.getByRole('heading', { name: /lista de estudiantes/i }).isVisible().catch(() => false);
    if (studentListVisible) {
      return true;
    }
    
    // Return false if error is visible
    const errorVisible = await this.page.getByText(/ya existe una sesión|error|debe|no se puede/i).isVisible().catch(() => false);
    return !errorVisible;
  }

  /**
   * Mark all students with a specific status
   * @param {'present'|'absent'|'late'} status - Attendance status
   */
  async markAllStudents(status) {
    const buttonMap = {
      present: /marcar todos presentes/i,
      absent: /marcar todos ausentes/i,
      late: /marcar todos tardanza/i,
    };
    
    await this.page.getByRole('button', { name: buttonMap[status] }).click();
    await this.page.waitForTimeout(500); // Wait for UI update
  }

  /**
   * Change individual student status by clicking their button
   * @param {number} studentIndex - Index of student (0-based)
   */
  async changeStudentStatus(studentIndex = 0) {
    const studentButtons = this.page.getByRole('button').filter({ hasText: /EST-/ });
    const student = studentButtons.nth(studentIndex);
    await student.click();
    await this.page.waitForTimeout(200); // Wait for UI update
  }

  /**
   * Search for students by name or code
   * @param {string} searchTerm - Search term
   */
  async searchStudents(searchTerm) {
    await this.page.locator('input[placeholder*="Buscar por nombre o código"]').fill(searchTerm);
    await this.page.waitForTimeout(500); // Wait for search to filter
  }

  /**
   * Save attendance
   */
  async saveAttendance() {
    await this.page.getByRole('button', { name: /guardar asistencia/i }).click();
    await this.page.waitForTimeout(1000); // Wait for save operation
  }

  /**
   * Cancel attendance session
   */
  async cancel() {
    await this.page.getByRole('button', { name: /cancelar/i }).click();
  }

  /**
   * Navigate to attendance history
   */
  async goToHistory() {
    await this.page.getByRole('button', { name: /ver historial/i }).click();
    await this.page.waitForURL('/attendance/history');
  }

  /**
   * Get statistics from cards
   * @returns {Promise<{total: number, present: number, absent: number, late: number}>}
   */
  async getStatistics() {
    // Wait for statistics to be visible
    await this.page.locator('.bg-white:has-text("Total")').waitFor({ timeout: 10000 });
    
    const getText = async (selector) => {
      const element = this.page.locator(selector).locator('text=/^\\d+$/');
      const text = await element.textContent();
      return parseInt(text) || 0;
    };

    return {
      total: await getText('.bg-white:has-text("Total")'),
      present: await getText('.bg-green-50:has-text("Presentes")'),
      absent: await getText('.bg-red-50:has-text("Ausentes")'),
      late: await getText('.bg-yellow-50:has-text("Tardanzas")'),
    };
  }

  /**
   * Check if success message is visible
   * @returns {Promise<boolean>}
   */
  async isSuccessMessageVisible() {
    return this.page.getByText(/sesión.*creada.*exitosamente/i).isVisible();
  }

  /**
   * Check if error message is visible
   * @returns {Promise<boolean>}
   */
  async isErrorMessageVisible() {
    return this.page.getByText(/ya existe una sesión|error|debe|no se puede/i).isVisible();
  }

  /**
   * Get error message text
   * @returns {Promise<string>}
   */
  async getErrorMessage() {
    const errorElement = this.page.getByText(/ya existe una sesión|error|debe|no se puede/i);
    return errorElement.textContent();
  }

  /**
   * Get count of students with specific status
   * @param {'PRESENTE'|'AUSENTE'|'TARDANZA'} status - Status to count
   * @returns {Promise<number>}
   */
  async getStudentCountByStatus(status) {
    const buttons = await this.page.getByText(status).all();
    return buttons.length;
  }

  /**
   * Verify page is loaded
   */
  async verifyPageLoaded() {
    await this.page.getByRole('heading', { name: 'Tomar Asistencia' }).waitFor();
  }

  /**
   * Verify session is created
   */
  async verifySessionCreated() {
    // Wait for the student list heading to appear, which indicates session was created
    // Also check for the bulk actions section as an alternative indicator
    await Promise.race([
      this.page.getByRole('heading', { name: /lista de estudiantes/i }).waitFor({ timeout: 15000 }),
      this.page.getByRole('heading', { name: /acciones masivas/i }).waitFor({ timeout: 15000 }),
      this.page.getByText(/marcar todos presentes/i).waitFor({ timeout: 15000 })
    ]);
  }
}
