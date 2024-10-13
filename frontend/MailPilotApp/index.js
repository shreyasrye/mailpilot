/**
 * @format
 */

import { AppRegistry } from 'react-native';
import App from './App';
import { name as appName } from './app.json';
import { Platform } from 'react-native';

AppRegistry.registerComponent(appName, () => App);
AppRegistry.runApplication(appName, {
  initialProps: {},
  rootTag: document.getElementById('root'),
});

if (Platform.OS === 'web') {
  const rootTag = document.getElementById('root') || document.createElement('div');
  AppRegistry.runApplication(appName, { initialProps: {}, rootTag });
} else {
  AppRegistry.registerComponent(appName, () => App);
}