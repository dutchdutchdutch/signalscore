'use client';

import { useEffect } from 'react';
import { analytics, perf } from '@/lib/firebase';

export default function AnalyticsProvider() {
    useEffect(() => {
        analytics.then((a) => {
            if (a) {
                console.log('Firebase Analytics initialized');
            }
        });

        if (perf) {
            console.log('Firebase Performance Monitoring initialized');
        }
    }, []);

    return null;
}
