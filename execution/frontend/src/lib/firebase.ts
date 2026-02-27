import { initializeApp, getApps } from 'firebase/app';
import { getAnalytics, isSupported } from 'firebase/analytics';
import { getPerformance } from 'firebase/performance';

const firebaseConfig = {
    apiKey: "AIzaSyB1YMHiEbAHuJdSOHDJ0BxL_r0duOo2-j8",
    authDomain: "signalscore-alpha.firebaseapp.com",
    projectId: "signalscore-alpha",
    storageBucket: "signalscore-alpha.firebasestorage.app",
    messagingSenderId: "199018949052",
    appId: "1:199018949052:web:7c54d9e4c0a64984ad63b9",
    measurementId: "G-ECK5CGLC79",
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

const analytics = isSupported().then((supported) => (supported ? getAnalytics(app) : null));

const perf = typeof window !== 'undefined' ? getPerformance(app) : null;

export { app, analytics, perf };
