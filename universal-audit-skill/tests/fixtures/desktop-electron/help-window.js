const { BrowserWindow } = require('electron');
const path = require('path');

// NEGATIVE: isolated, sandboxed, local content only
module.exports = function helpWindow() {
  return new BrowserWindow({
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
};
