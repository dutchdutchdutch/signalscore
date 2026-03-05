import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

type Article = {
    slug: string;
    frontmatter: Record<string, any>;
    content: string;
};

// In production (standalone Docker), the file is copied to /app/content/articles/
// In development, resolve from the repo root via ../../docs/articles/
const ARTICLES_PATHS = [
    path.join(process.cwd(), 'content/articles'),
    path.join(process.cwd(), '../../docs/articles'),
];

export async function getMethodologyArticle(): Promise<Article | null> {
    const filename = 'scoring-methodology.md';

    for (const dir of ARTICLES_PATHS) {
        try {
            const filePath = path.join(dir, filename);
            const fileContent = await fs.promises.readFile(filePath, 'utf8');
            const { data, content } = matter(fileContent);

            return {
                slug: 'scoring-methodology',
                frontmatter: data,
                content,
            };
        } catch {
            // Try next path
        }
    }

    console.error('Error reading methodology article: file not found in any search path');
    return null;
}
