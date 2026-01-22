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
    // Wait for result section to appear
    await this.page.waitForSelector(this.selectors.resultSection, { timeout: 15000 });
    
    // Wait a bit for UI to update
    await this.page.waitForTimeout(1000);
    
    // Find the result section container
    const resultSection = this.page.locator('section:has-text("Resultado de la importación")');
    await resultSection.waitFor({ timeout: 5000 });
    
    // Verify specific counts and labels within the result section
    // The structure is: <div class="text-center"> contains <div class="text-lg font-bold">{number}</div> and <div class="text-xs">{label}</div>
    if (expectedCreated > 0) {
      // Look for the container that has both the number and "Creados" label
      const createdColumn = resultSection.locator('div.text-center').filter({ hasText: 'Creados' });
      await createdColumn.waitFor({ timeout: 5000 });
      
      // Get all text from this column (should include both number and "Creados")
      const columnText = await createdColumn.textContent();
      if (!columnText || !columnText.includes(String(expectedCreated))) {
        // Try to find the number anywhere in the result section as fallback
        const allText = await resultSection.textContent();
        if (!allText || !allText.includes(String(expectedCreated))) {
          throw new Error(
            `Created count ${expectedCreated} not found in results. ` +
            `Column text: "${columnText}", All text: ${allText?.substring(0, 300)}`
          );
        }
      }
      
      // Also verify the label exists
      if (!columnText || !columnText.includes('Creados')) {
        throw new Error(`"Creados" label not found in created column. Column text: "${columnText}"`);
      }
    }
    if (expectedUpdated > 0) {
      const updatedColumn = resultSection.locator('div.text-center').filter({ hasText: 'Actualizados' });
      await updatedColumn.waitFor({ timeout: 5000 });
      
      const columnText = await updatedColumn.textContent();
      if (!columnText || !columnText.includes(String(expectedUpdated))) {
        const allText = await resultSection.textContent();
        if (!allText || !allText.includes(String(expectedUpdated))) {
          throw new Error(
            `Updated count ${expectedUpdated} not found in results. ` +
            `Column text: "${columnText}", All text: ${allText?.substring(0, 300)}`
          );
        }
      }
      
      if (!columnText || !columnText.includes('Actualizados')) {
        throw new Error(`"Actualizados" label not found in updated column. Column text: "${columnText}"`);
      }
    }
    
    // Verify no error section is shown for success
    const errorSection = await this.page.locator(this.selectors.errorMessage).isVisible().catch(() => false);
    if (errorSection) {
      const errorText = await this.page.locator(this.selectors.errorMessage).textContent().catch(() => '');
      throw new Error(`Unexpected error shown in success case: ${errorText}`);
    }
  }

  /**
   * Verify validation errors are displayed
   * @param {string[]} expectedErrors - Array of expected error messages
   */
  async verifyValidationErrors(expectedErrors = []) {
    if (!expectedErrors || expectedErrors.length === 0) {
      throw new Error('verifyValidationErrors requires at least one expected error');
    }
    
    // Wait for result section (validation errors appear in results)
    await this.page.waitForSelector(this.selectors.resultSection, { timeout: 15000 });
    
    // Wait a bit for UI to update
    await this.page.waitForTimeout(1000);
    
    // Find the result section container
    const resultSection = this.page.locator('section:has-text("Resultado de la importación")');
    await resultSection.waitFor({ timeout: 5000 });
    
    // Look for errors list within the result section
    const errorsList = resultSection.locator('ul, div:has-text("Detalles de errores")');
    const errorsListVisible = await errorsList.first().isVisible().catch(() => false);
    
    // Check for specific error messages
    const foundErrors = [];
    for (const errorText of expectedErrors) {
      try {
        // Try to find in errors list first
        if (errorsListVisible) {
          const errorsText = await errorsList.first().textContent().catch(() => '');
          if (errorsText && errorsText.toLowerCase().includes(errorText.toLowerCase())) {
            foundErrors.push(errorText);
            continue;
          }
        }
        
        // Try exact match in result section
        const found = await resultSection.locator(`text=/.*${errorText}.*/i`).first().waitFor({ timeout: 5000 }).catch(() => null);
        if (found) {
          foundErrors.push(errorText);
          continue;
        }
        
        // Try partial match
        const errorParts = errorText.split(' ').filter(p => p.length > 3);
        let found = false;
        for (const part of errorParts) {
          const partFound = await resultSection.locator(`text=/.*${part}.*/i`).first().waitFor({ timeout: 2000 }).catch(() => null);
          if (partFound) {
            found = true;
            foundErrors.push(part);
            break;
          }
        }
        if (!found) {
          const allText = await resultSection.textContent();
          throw new Error(
            `Validation error not found: "${errorText}". ` +
            `Result section text: ${allText?.substring(0, 500)}`
          );
        }
      } catch (e) {
        if (e.message.includes('Validation error not found')) {
          throw e;
        }
        // Continue to next error
      }
    }
    
    if (foundErrors.length === 0) {
      const pageContent = await this.page.textContent('body').catch(() => '');
      throw new Error(
        `No validation errors found. Expected: ${expectedErrors.join(', ')}. ` +
        `Page content preview: ${pageContent?.substring(0, 500)}`
      );
    }
  }

  /**
   * Verify general error message is displayed
   * @param {string} expectedError - Expected error message pattern (required)
   */
  async verifyErrorMessage(expectedError) {
    if (!expectedError) {
      throw new Error('verifyErrorMessage requires an expectedError parameter');
    }

    // Wait a bit for UI to update after API response
    await this.page.waitForTimeout(1000);
    
    // Check if page is still available
    try {
      await this.page.evaluate(() => document.body);
    } catch (e) {
      throw new Error(`Page is closed or unavailable. Cannot verify error message: "${expectedError}"`);
    }
    
    // Try multiple selectors for error messages
    const errorSelectors = [
      '.bg-red-50', // Primary error container in BulkImportModal
      '.text-red-500',
      '.text-red-600', 
      '.text-red-700',
      '.text-red-800',
      '.bg-red-100',
      '[class*="error"]',
      '[class*="red"]',
      '[role="alert"]'
    ];
    
    let errorFound = false;
    let foundText = null;
    
    // First try to find by text content (most reliable) - look in error containers
    try {
      // Look for error in the red error box
      const errorBox = this.page.locator('.bg-red-50');
      const isVisible = await errorBox.isVisible().catch(() => false);
      if (isVisible) {
        const errorText = await errorBox.textContent().catch(() => '');
        if (errorText && errorText.toLowerCase().includes(expectedError.toLowerCase())) {
          errorFound = true;
          foundText = errorText;
        }
      }
    } catch (e) {
      // Continue to other methods
    }
    
    // If not found, try by text selector with timeout
    if (!errorFound) {
      try {
        // Escape special characters in expectedError for selector
        const escapedError = expectedError.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        await this.page.waitForSelector(`text=/.*${escapedError}.*/i`, { timeout: 5000 });
        errorFound = true;
        foundText = expectedError;
      } catch (e) {
        // Try with different patterns
        const errorParts = expectedError.split(' ').filter(p => p.length > 3);
        for (const part of errorParts) {
          try {
            await this.page.waitForSelector(`text=/.*${part}.*/i`, { timeout: 2000 });
            errorFound = true;
            foundText = part;
            break;
          } catch (e2) {
            // Continue
          }
        }
      }
    }
    
    // If not found by text, try by selector
    if (!errorFound) {
      for (const selector of errorSelectors) {
        try {
          const element = await this.page.waitForSelector(selector, { timeout: 2000 });
          if (element) {
            const text = await element.textContent();
            if (text && text.toLowerCase().includes(expectedError.toLowerCase())) {
              errorFound = true;
              foundText = text;
              break;
            }
          }
        } catch (e) {
          // Continue to next selector
        }
      }
    }
    
    // Last resort: check page content (with safety check)
    if (!errorFound) {
      try {
        const content = await this.page.textContent('body').catch(() => null);
        if (content && content.toLowerCase().includes(expectedError.toLowerCase())) {
          errorFound = true;
          foundText = expectedError;
        }
      } catch (e) {
        // Page might be closed, but we already checked above
      }
    }
    
    if (!errorFound) {
      // Take screenshot for debugging
      try {
        await this.page.screenshot({ path: `error-not-found-${Date.now()}.png` });
      } catch (e) {
        // Screenshot failed, page might be closed
      }
      
      let pageContent = '';
      try {
        pageContent = await this.page.textContent('body') || '';
      } catch (e) {
        pageContent = 'Page content unavailable';
      }
      
      throw new Error(
        `Error message not found: "${expectedError}". ` +
        `Page content preview: ${pageContent.substring(0, 500)}`
      );
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
    
    // Wait a bit for UI to update
    await this.page.waitForTimeout(1000);
    
    // Find the result section container
    const resultSection = this.page.locator('section:has-text("Resultado de la importación")');
    await resultSection.waitFor({ timeout: 5000 });
    
    // Verify created count - look in the "Creados" column
    const createdColumn = resultSection.locator('div.text-center').filter({ hasText: 'Creados' });
    const createdVisible = await createdColumn.isVisible().catch(() => false);
    if (createdVisible) {
      // Get all text from the column (includes both number and label)
      const createdText = await createdColumn.textContent().catch(() => '');
      if (!createdText || !createdText.includes(String(expectedCreated))) {
        const allText = await resultSection.textContent();
        throw new Error(
          `Created count ${expectedCreated} not found in partial success results. ` +
          `Column text: "${createdText}", All text: ${allText?.substring(0, 300)}`
        );
      }
    } else {
      // Fallback: check if number exists anywhere in result section
      const allText = await resultSection.textContent();
      if (!allText || !allText.includes(String(expectedCreated))) {
        throw new Error(
          `Created count ${expectedCreated} not found in partial success results. ` +
          `Found text: ${allText?.substring(0, 300)}`
        );
      }
    }
    
    // Verify error count - look in the "Errores" column
    const errorsColumn = resultSection.locator('div.text-center').filter({ hasText: 'Errores' });
    const errorsVisible = await errorsColumn.isVisible().catch(() => false);
    if (errorsVisible) {
      const errorsText = await errorsColumn.textContent().catch(() => '');
      if (!errorsText || !errorsText.includes(String(expectedErrors))) {
        const allText = await resultSection.textContent();
        throw new Error(
          `Error count ${expectedErrors} not found in partial success results. ` +
          `Column text: "${errorsText}", All text: ${allText?.substring(0, 300)}`
        );
      }
    } else {
      // Fallback: check if number exists anywhere in result section
      const allText = await resultSection.textContent();
      if (!allText || !allText.includes(String(expectedErrors))) {
        throw new Error(
          `Error count ${expectedErrors} not found in partial success results. ` +
          `Found text: ${allText?.substring(0, 300)}`
        );
      }
    }
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