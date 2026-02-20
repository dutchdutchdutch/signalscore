import React from 'react';

const SAMPLE_DATA = {
    company: 'ACME Anvils',
    categories: [
        { name: 'AI Keywords', score: 92, weight: '15%', boost: '+13.8' },
        { name: 'Agentic Signals', score: 65, weight: '20%', boost: '+13.0' },
        { name: 'Modern Tool Stack', score: 88, weight: '20%', boost: '+17.6' },
        { name: 'AI in Non-Engineering Roles', score: 75, weight: '20%', boost: '+15.0' },
        { name: 'AI in IT', score: 80, weight: '25%', boost: '+20.0' },
    ],
};

export function SampleTable() {
    return (
        <div className="w-full max-w-2xl mx-auto mt-12 mb-16 px-4 group perspective-container">
            <div
                className="
          relative overflow-hidden
          bg-surface border border-gray-800 rounded-xl
          shadow-2xl shadow-purple-900/20
          transform-style-3d
          transition-all duration-700 ease-out
          hover:shadow-purple-700/30
          sample-table-tilt
        "
            >
                {/* Header */}
                <div className="p-6 border-b border-gray-800 bg-surface-alt/50 backdrop-blur-sm">
                    <div className="flex justify-between items-center">
                        <div>
                            <h3 className="text-xl font-bold text-white mb-1">{SAMPLE_DATA.company}</h3>
                            <div className="text-xs text-purple-400 font-mono">SCORED: 6 Feb 2026</div>
                        </div>
                        <div className="text-right">
                            <div className="text-3xl font-bold text-blue-400">85</div>
                            <div className="text-[10px] tracking-wider text-gray-500 uppercase">Advanced</div>
                        </div>
                    </div>
                </div>

                {/* Table Content */}
                <div className="p-6 bg-surface/90">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-left text-xs uppercase tracking-wider text-gray-500 border-b border-gray-800">
                                <th className="pb-3 pl-2 font-medium">Category</th>
                                <th className="pb-3 text-right font-medium">Score</th>
                                <th className="pb-3 text-right font-medium">Weight</th>
                                <th className="pb-3 text-right font-medium">Boost</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800/50">
                            {SAMPLE_DATA.categories.map((row) => (
                                <tr key={row.name} className="group/row transition-colors hover:bg-white/5">
                                    <td className="py-3 pl-2 text-gray-300 font-medium">{row.name}</td>
                                    <td className="py-3 text-right text-purple-300/90 font-mono">{row.score.toFixed(1)}</td>
                                    <td className="py-3 text-right text-gray-500">{row.weight}</td>
                                    <td className="py-3 text-right text-purple-400 font-mono font-bold">{row.boost}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Ambient Glow */}
                <div className="absolute inset-0 pointer-events-none bg-gradient-to-tr from-purple-900/10 via-transparent to-transparent opacity-50" />
            </div>

            <style jsx>{`
        .perspective-container {
          perspective: 800px; /* Lower value = more dramatic perspective */
        }
        .transform-style-3d {
          transform-style: preserve-3d;
        }
        .sample-table-tilt {
          /* Mobile: Slightly more pronounced than before */
          transform: rotateX(15deg) rotateY(5deg) rotateZ(-2deg) scale(0.95);
        }
        @media (min-width: 640px) {
          .sample-table-tilt {
            /* 
               Reversed slant & Intenional Tilt:
               rotateX(20deg): Top leans back / Bottom comes forward (standard table look).
               rotateY(10deg): Right side goes back, Left side comes forward.
               rotateZ(-4deg): Slight counter-clockwise tilt to lift the right side visually?
               
               User request: "top corner on the left side of the screen comes forward" -> rotateY(positive) brings LEFT forward? 
               Wait, rotateY(positive) moves RIGHT side away (into screen) and LEFT side forward (out of screen). Yes.
               
               "bottom right corner looks like it's pointed upwards" -> rotateZ? or rotateX/Y combo.
               
               Let's try a strong combo:
               rotateX(24deg)  -> Heavy perspective tilt back
               rotateY(12deg)  -> Left side forward, Right side back
               rotateZ(-6deg)  -> Lifts the right side, drops the left side
               
               + strong perspective on container
            */
            transform: rotateX(24deg) rotateY(12deg) rotateZ(-6deg) scale(0.9);
            box-shadow: -20px 20px 60px -10px rgba(88, 28, 135, 0.4); 
          }
        }
        .group:hover .sample-table-tilt {
          /* Flatten slightly on hover for readability */
          transform: rotateX(0deg) rotateY(0deg) scale(1);
        }
      `}</style>
        </div>
    );
}
