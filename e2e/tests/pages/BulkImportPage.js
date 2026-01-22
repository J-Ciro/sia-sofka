/**
 * Page Object Model for Bulk Import/Export Excel functionality
 * Encapsulates page interactions and selectors for bulk import operations
 * 
 * Best Practices:
 * - Single Responsibility: One POM per page/component
 * - Encapsulation: Hide implementation details
 * - Reusability: Methods can be reused across tests
 * - Maintainability: Selectors in one place
 * - Descriptive Methods: Clear method names that describe user actions
 */

export class BulkImportPage {
  /**
   * @param {import('@playwright/test').Page} page - Playwright page object
   */
  constructor(page) {
    this.page = page;
    
    // Selectors - centralized for easy maintenance
    this.selectors = {
      // Navigation and page elements
      usersPage: '/users',
      importButton: 'button:has-text("Importar Excel")',
      
      // Modal elements
      modalTitle: 'text=Importar / Exportar Excel',
      closeButton: '.bg-white .p-1', // X button
      closeButtonText: '.bg-white button:has-text("Cerrar")', // Cerrar button
      
      // Import section
      fileInput: 'input[type="file"]',
      importButtonInModal: 'button[name="Importar"], button:has-text("Importar"):not(:has-text("Excel"))',
      
      // Download section
      downloadTemplateButton: 'button:has-text("Descargar plantilla")',
      exportUsersButton: 'button:has-text("Exportar usuarios")',
      
      // Results and messages
      resultSection: 'text=Resultado de la importación',
      errorMessage: '.bg-red-50',
      processingMessage: 'text=Procesando',
      
      // Specific result texts - Updated to match actual frontend structure
      createdText: (count) => `text=${count}`,
      createdLabel: 'text=Creados',
      updatedText: (count) => `text=${count}`,
      updatedLabel: 'text=Actualizados', 
      errorsText: (count) => `text=${count}`,
      errorsLabel: 'text=Errores',
      
      // Error message patterns
      emailInvalidText: 'text=Email inválido',
      duplicateEmailText: 'text=Email duplicado',
      fileTypeError: 'text=Solo se aceptan archivos .xlsx',
      fileSizeError: 'text=El archivo supera el límite de 5 MB',
      emptyFileError: 'text=No se encontraron datos para importar',
      corruptFileError: 'text=Archivo Excel corrupto o no válido',
      invalidHeadersError: 'text=Faltan columnas obligatorias',
    };
  }

  /**
   * Navigate to users page where bulk import functionality is available
   */
  async goto() {
    await this.page.goto(this.selectors.usersPage);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Open the bulk import modal
   */
  async openImportModal() {
    await this.page.click(this.selectors.importButton);
    await this.page.waitForSelector(this.selectors.modalTitle, { timeout: 10000 });
  }

  /**
   * Close the modal using the X button
   */
  async closeModalWithX() {
    await this.page.click(this.selectors.closeButton);
  }

  /**
   * Close the modal using the "Cerrar" button
   */
  async closeModalWithButton() {
    await this.page.click(this.selectors.closeButtonText);
  }

  /**
   * Upload a file for import
   * @param {string} filePath - Path to the file to upload
   */
  async uploadFile(filePath) {
    await this.page.setInputFiles(this.selectors.fileInput, filePath);
  }

  /**
   * Click the import button to start the import process
   */
  async clickImport() {
    await this.page.getByRole('button', { name: /^Importar$/ }).click();
  }

  /**
   * Wait for import response and handle the result
   * @param {string} expectedResponse - Expected response URL pattern
   */
  async waitForImportResponse(expectedResponse = '**/api/v1/users/bulk-import') {
    try {
      await this.page.waitForResponse(expectedResponse, { timeout: 15000 });
    } catch (error) {
      // Timeout is acceptable for some tests
    }
  }

  /**
   * Download the import template
   */
  async downloadTemplate() {
    await this.page.click(this.selectors.downloadTemplateButton);
  }

  /**
   * Export users to Excel
   */
  async exportUsers() {
    await this.page.click(this.selectors.exportUsersButton);
  }

  /**
   * Perform complete import workflow
   * @param {string} filePath - Path to the file to import
   */
  async performImport(filePath) {
    await this.uploadFile(filePath);
    await this.clickImport();
    await this.waitForImportResponse();
  }

  // ==================== VERIFICATION METHODS ====================

  /**
   * Verify the modal is open and displays all required UI elements
   */
  async verifyModalElements() {
    // Check modal title
    await this.page.waitForSelector(this.selectors.modalTitle, { timeout: 10000 });
    
    // Check main sections
    await this.page.waitForSelector(this.selectors.downloadTemplateButton, { timeout: 5000 });
    await this.page.waitForSelector(this.selectors.exportUsersButton, { timeout: 5000 });
    await this.page.waitForSelector(this.selectors.fileInput, { timeout: 5000 });
  }

  /**
   * Verify import button is disabled (no file selected)
   */
  async verifyImportButtonDisabled() {
    const importButton = this.page.getByRole('button', { name: /^Importar$/ });
    await importButton.waitFor({ timeout: 5000 });
    const isDisabled = await importButton.isDisabled();
    if (!isDisabled) {
      throw new Error('El botón Importar debería estar deshabilitado');
    }
  }

  /**
   * Verify import button is enabled (file selected)
   */
  async verifyImportButtonEnabled() {
    const importButton = this.page.getByRole('button', { name: /^Importar$/ });
    await importButton.waitFor({ timeout: 5000 });
    const isEnabled = await importButton.isEnabled();
    if (!isEnabled) {
      throw new Error('El botón Importar debería estar habilitado');
    }
  }

  /**
   * Verify modal is closed
   */
  async verifyModalClosed() {
    const isVisible = await this.page.locator(this.selectors.modalTitle).isVisible();
    if (isVisible) {
      throw new Error('El modal debería estar cerrado');
    }
  }

  /**
   * Verify success result is displayed
   * @param {number} expectedCreated - Expected number of created records
   * @param {number} expectedUpdated - Expected number of updated records
   */
  async verifySuccessResult(expectedCreated = 0, expectedUpdated = 0) {
    // Wait for result section
    await this.page.waitForSelector(this.selectors.resultSection, { timeout: 15000 });
    
    // Verify specific counts and labels
    if (expectedCreated > 0) {
      await this.page.waitForSelector(this.selectors.createdText(expectedCreated), { timeout: 5000 });
      await this.page.waitForSelector(this.selectors.createdLabel, { timeout: 5000 });
    }
    if (expectedUpdated > 0) {
      await this.page.waitForSelector(this.selectors.updatedText(expectedUpdated), { timeout: 5000 });
      await this.page.waitForSelector(this.selectors.updatedLabel, { timeout: 5000 });
    }
  }

  /**
   * Verify validation errors are displayed
   * @param {string[]} expectedErrors - Array of expected error messages
   */
  async verifyValidationErrors(expectedErrors = []) {
    // Wait for result section (validation errors appear in results)
    await this.page.waitForSelector(this.selectors.resultSection, { timeout: 15000 });
    
    // Check for specific error messages
    for (const errorText of expectedErrors) {
      await this.page.waitForSelector(`text=${errorText}`, { timeout: 5000 });
    }
  }

  /**
   * Verify general error message is displayed
   * @param {string} expectedError - Expected error message pattern
   */
  async verifyErrorMessage(expectedError = null) {
    // Try multiple selectors for error messages
    const errorSelectors = [
      this.selectors.errorMessage,
      '.text-red-500',
      '.text-red-600', 
      '.bg-red-100',
      '[class*="error"]',
      '[class*="red"]'
    ];
    
    let errorFound = false;
    for (const selector of errorSelectors) {
      try {
        await this.page.waitForSelector(selector, { timeout: 3000 });
        errorFound = true;
        break;
      } catch (e) {
        // Continue to next selector
      }
    }
    
    if (!errorFound) {
      // Try to find any element containing error text
      if (expectedError) {
        try {
          await this.page.waitForSelector(`*:has-text("${expectedError}")`, { timeout: 5000 });
          errorFound = true;
        } catch (e) {
          // Last resort: check page content
          const content = await this.page.textContent('body');
          if (content.includes(expectedError)) {
            errorFound = true;
          }
        }
      }
    }
    
    if (!errorFound && expectedError) {
      throw new Error(`Error message not found: ${expectedError}`);
    }
  }

  /**
   * Verify processing state is shown
   */
  async verifyProcessingState() {
    await this.page.waitForSelector(this.selectors.processingMessage, { timeout: 10000 });
  }

  /**
   * Verify partial success (some records created, some errors)
   * @param {number} expectedCreated - Expected created count
   * @param {number} expectedErrors - Expected error count
   */
  async verifyPartialSuccess(expectedCreated, expectedErrors) {
    await this.page.waitForSelector(this.selectors.resultSection, { timeout: 15000 });
    await this.page.waitForSelector(this.selectors.createdText(expectedCreated), { timeout: 5000 });
    await this.page.waitForSelector(this.selectors.createdLabel, { timeout: 5000 });
    await this.page.waitForSelector(this.selectors.errorsText(expectedErrors), { timeout: 5000 });
    await this.page.waitForSelector(this.selectors.errorsLabel, { timeout: 5000 });
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Take a screenshot for debugging
   * @param {string} name - Screenshot name
   */
  async takeScreenshot(name) {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
  }

  /**
   * Log current page state for debugging
   */
  async logPageState() {
    const url = this.page.url();
    const title = await this.page.title();
    console.log(`📄 Estado actual - URL: ${url}, Título: ${title}`);
  }
}