import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.crisis.os',
  appName: 'Crisis OS',
  webDir: 'out',
  bundledWebRuntime: false,
  // WebView loads as https://localhost; calls to http://LAN must be allowed.
  android: {
    allowMixedContent: true,
  },
  plugins: {
    CapacitorHttp: {
      enabled: true,
    },
  },
};

export default config;