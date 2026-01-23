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
    
    const button = this.page.getByRole('button', { name: buttonMap[status] });
    await button.waitFor({ state: 'visible', timeout: 10000 });
    await button.click();
    
    // Wait for success message or UI update
    await Promise.race([
      this.page.getByText(/todos los estudiantes marcados como/i).waitFor({ timeout: 5000 }).catch(() => null),
      this.page.waitForTimeout(1000)
    ]);
    
    // Wait a bit more for statistics to update
    await this.page.waitForTimeout(500);
  }

  /**
   * Change individual student status by clicking their button
   * @param {number} studentIndex - Index of student (0-based)
   */
  async changeStudentStatus(studentIndex = 0) {
    // Wait for student buttons to be available
    await this.page.getByRole('button').filter({ hasText: /EST-/ }).first().waitFor({ timeout: 10000 });
    
    const studentButtons = this.page.getByRole('button').filter({ hasText: /EST-/ });
    const count = await studentButtons.count();
    
    if (count === 0) {
      throw new Error('No student buttons found. Make sure students are loaded.');
    }
    
    if (studentIndex >= count) {
      throw new Error(`Student index ${studentIndex} is out of range. Only ${count} students found.`);
    }
    
    const student = studentButtons.nth(studentIndex);
    await student.waitFor({ state: 'visible', timeout: 5000 });
    await student.click();
    await this.page.waitForTimeout(300); // Wait for UI update
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
    
    // Also wait for students to be loaded before reading statistics
    // This ensures the statistics are accurate
    try {
      await this.page.getByRole('button').filter({ hasText: /EST-/ }).first().waitFor({ timeout: 5000 });
    } catch (error) {
      // If no students found, statistics might be 0, which is valid
      console.log('No students found when reading statistics');
    }
    
    // Wait a bit more for statistics to update after any state changes
    await this.page.waitForTimeout(300);
    
    const getText = async (selector) => {
      try {
        const element = this.page.locator(selector);
        await element.waitFor({ timeout: 5000 });
        const textElement = element.locator('text=/^\\d+$/').first();
        const text = await textElement.textContent();
        return parseInt(text) || 0;
      } catch (error) {
        console.log(`Error reading statistics from ${selector}:`, error.message);
        return 0;
      }
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
    
    // Wait for students to actually load - look for student buttons with EST- code
    // This ensures the API call to fetch students has completed
    // Give it more time and check multiple times
    let studentsFound = false;
    for (let attempt = 0; attempt < 5; attempt++) {
      try {
        await this.page.waitForTimeout(1000); // Wait between attempts
        const studentButtons = this.page.getByRole('button').filter({ hasText: /EST-/ });
        const count = await studentButtons.count();
        if (count > 0) {
          studentsFound = true;
          break;
        }
      } catch (error) {
        // Continue trying
      }
    }
    
    if (!studentsFound) {
      // Check if there's a "no students" message
      await this.page.waitForTimeout(1000);
      const noStudentsMessage = await this.page.getByText(/no.*estudiantes|sin estudiantes|no hay estudiantes matriculados/i).isVisible().catch(() => false);
      if (noStudentsMessage) {
        // Log helpful debug info
        const pageText = await this.page.textContent('body').catch(() => '');
        console.warn('No students found. Page text snippet:', pageText.substring(0, 1000));
        throw new Error('No students found in the subject. Make sure enrollments exist. Check global-setup.js logs to verify subject and enrollment were created.');
      }
      // If still no students after waiting, this is a real issue - the test needs students
      throw new Error('Students did not appear after session creation. This indicates a data setup issue. Verify that: 1) global-setup.js created subject and enrollment, 2) The subject has students enrolled, 3) The API endpoint /subjects/{id}/students returns data.');
    }
  }
}
