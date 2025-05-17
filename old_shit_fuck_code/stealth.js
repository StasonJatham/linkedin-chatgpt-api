// navigator.webdriver = undefined
Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined,
});

// window.chrome spoof
window.chrome = { runtime: {} };

// navigator.plugins spoof
Object.defineProperty(navigator, 'plugins', {
  get: () => [1, 2, 3],
});

// navigator.languages spoof
Object.defineProperty(navigator, 'languages', {
  get: () => ['de-DE', 'de']
});

// permissions.query spoof
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
  parameters.name === 'notifications'
    ? Promise.resolve({ state: Notification.permission })
    : originalQuery(parameters);

// WebGL fingerprint spoof
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function (parameter) {
  if (parameter === 37445) return 'Intel Inc.';
  if (parameter === 37446) return 'Intel Iris OpenGL Engine';
  return getParameter.call(this, parameter);
};

// navigator.connection spoof
Object.defineProperty(navigator, 'connection', {
  get: () => ({
    rtt: 50,
    downlink: 10,
    effectiveType: '4g',
    saveData: false,
  }),
});
