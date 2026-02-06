import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

type Article = {
    slug: string;
    frontmatter: Record<string, any>;
    content: string;
};

const ARTICLES_DIR = path.join(process.cwd(), '../../docs/articles');

// For now we only have one article, but nice to have a helper
// For now we only have one article, but nice to have a helper
export async function getMethodologyArticle(): Promise<Article | null> {
    try {
        const filePath = path.join(ARTICLES_DIR, 'scoring-methodology.md');
        const fileContent = await fs.promises.readFile(filePath, 'utf8');
        const { data, content } = matter(fileContent);

        return {
            slug: 'scoring-methodology',
            frontmatter: data,
            content,
        };
    } catch (error) {
        console.error('Error reading methodology article:', error);
        return null;
    }
}
