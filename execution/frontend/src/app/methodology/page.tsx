import { Footer } from '@/components/ui/Footer';
import { getMethodologyArticle } from '@/lib/markdown';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default async function MethodologyPage() {
    const article = await getMethodologyArticle();
    const content = article?.content || '# Content Not Found\n\nUnable to load methodology content.';

    return (
        <main className="min-h-screen bg-surface flex flex-col items-center">
            {/* Navigation / Header - simple back link */}
            <div className="w-full max-w-3xl px-6 py-6">
                <a href="/" className="text-sm text-text-secondary hover:text-primary">← Back to SignalScore</a>
            </div>

            <article className="w-full max-w-3xl px-6 py-8 prose dark:prose-invert prose-headings:text-text-primary prose-p:text-text-secondary prose-li:text-text-secondary prose-strong:text-text-primary prose-th:text-text-primary prose-td:text-text-secondary prose-a:text-primary hover:prose-a:text-primary-hover">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            </article>

            <Footer />
        </main>
    );
}
