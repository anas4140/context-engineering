import React from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import clsx from 'clsx';
import styles from './index.module.css';

const FEATURES = [
  {
    icon: '📚',
    title: '12 Modules, 37+ Lessons',
    body: 'From zero-shot prompting to multi-agent systems, extended thinking, async patterns, and prompt A/B testing.',
  },
  {
    icon: '⚡',
    title: 'Runnable Code for Every Lesson',
    body: 'Every concept has a working Python example. Clone the repo, add your API key, and run it in minutes.',
  },
  {
    icon: '🔑',
    title: 'Answer Keys + Hands-on Tasks',
    body: 'Every lesson has 3 hands-on exercises. Every task has a complete solution to compare against.',
  },
];

const MODULES = [
  { num: 1,  title: 'Foundations of Context Engineering', lessons: 3,  badge: 'Start here', path: '/docs/Module1/Lesson1_What_is_Context' },
  { num: 2,  title: 'Advanced Prompting Techniques',      lessons: 3,  badge: null,          path: '/docs/Module2/Lesson1_Prompt_Taxonomy' },
  { num: 3,  title: 'Retrieval-Augmented Generation',     lessons: 5,  badge: 'Hybrid search', path: '/docs/Module3/Lesson1_Introduction_to_RAG' },
  { num: 4,  title: 'Optimising the Context Window',      lessons: 3,  badge: null,          path: '/docs/Module4/Lesson1_Context_Window_Anatomy' },
  { num: 5,  title: 'From RAG to Agents',                 lessons: 4,  badge: 'Tool use',    path: '/docs/Module5/Lesson1_ReAct_Pattern' },
  { num: 6,  title: 'Evaluation, Testing & Security',     lessons: 3,  badge: null,          path: '/docs/Module6/Lesson1_Evaluation' },
  { num: 7,  title: 'The Future of Context (CWA)',        lessons: 5,  badge: 'Files API',   path: '/docs/Module7/Lesson1_Emerging_Patterns' },
  { num: 8,  title: 'Extended Thinking',                  lessons: 2,  badge: 'New',         path: '/docs/Module8/Lesson1_Extended_Thinking' },
  { num: 9,  title: 'Production at Scale',                lessons: 3,  badge: 'Batch API',   path: '/docs/Module9/Lesson1_Batch_API' },
  { num: 10, title: 'Model Context Protocol (MCP)',       lessons: 2,  badge: 'New',         path: '/docs/Module10/Lesson1_MCP_Introduction' },
  { num: 11, title: 'Async & Concurrent Patterns',       lessons: 2,  badge: 'New',         path: '/docs/Module11/Lesson1_Async_Basics' },
  { num: 12, title: 'Prompt Versioning & A/B Testing',   lessons: 2,  badge: 'New',         path: '/docs/Module12/Lesson1_Prompt_Versioning' },
];

function Hero() {
  return (
    <header className={clsx('hero hero--primary', styles.hero)}>
      <div className="container">
        <p className={styles.heroPre}>Free & Open Source</p>
        <h1 className="hero__title">Context Engineering<br />for AI</h1>
        <p className="hero__subtitle">
          The complete, hands-on course for building robust, reliable, and<br />
          cost-efficient AI applications with Claude — 12 modules, fully tested.
        </p>
        <div className={styles.heroButtons}>
          <Link className="button button--lg button--secondary" to="/setup">
            Setup Guide →
          </Link>
          <Link className="button button--lg button--outline button--secondary" to="/docs/Module1/Lesson1_What_is_Context">
            Start Lesson 1
          </Link>
        </div>
        <div className={styles.heroBadges}>
          <span>12 modules</span>
          <span>37 lessons</span>
          <span>268 tests</span>
          <span>Python + Anthropic SDK</span>
        </div>
      </div>
    </header>
  );
}

function Features() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FEATURES.map(({ icon, title, body }) => (
            <div key={title} className="col col--4">
              <div className="feature-card">
                <div className="feature-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function QuickStart() {
  return (
    <section className={styles.quickstartSection}>
      <div className="container">
        <p className="section-label">Quick Start</p>
        <h2>Up and running in 3 steps</h2>
        <div className="quickstart">
          <span className="comment"># 1. Clone and install</span>{'\n'}
          <span className="cmd">git clone</span> <span className="str">https://github.com/anas4140/context-engineering.git</span>{'\n'}
          <span className="cmd">pip install</span> -r requirements.txt{'\n\n'}
          <span className="comment"># 2. Add your Anthropic API key</span>{'\n'}
          <span className="cmd">cp</span> .env.example .env{'\n'}
          <span className="comment">#    → paste ANTHROPIC_API_KEY=sk-ant-... into .env</span>{'\n\n'}
          <span className="comment"># 3. Run your first lesson</span>{'\n'}
          <span className="cmd">python3</span> code/module1/lesson1_context_demo.py
        </div>
        <p style={{ fontSize: '0.9rem', color: 'var(--ifm-color-emphasis-600)' }}>
          Requires Python 3.10+ and an{' '}
          <a href="https://console.anthropic.com" target="_blank" rel="noopener">Anthropic API key</a>{' '}
          (free tier available). No prior AI or ML experience required.{' '}
          Need help? See the <Link to="/setup">Setup Guide</Link> or <Link to="/troubleshooting">Troubleshooting</Link>.
        </p>
      </div>
    </section>
  );
}

function ModuleGrid() {
  return (
    <section className={styles.modulesSection}>
      <div className="container">
        <p className="section-label">Curriculum</p>
        <h2>12 modules, structured for depth</h2>
        <div className="module-grid">
          {MODULES.map(({ num, title, lessons, badge, path }) => (
            <Link key={num} className="module-card" to={path}>
              <div className="module-num">
                Module {num}
                {badge && (
                  <span className={styles.badge}>{badge}</span>
                )}
              </div>
              <p className="module-title">{title}</p>
              <p className="module-meta">{lessons} lesson{lessons !== 1 ? 's' : ''}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalProject() {
  return (
    <section className={styles.projectSection}>
      <div className="container">
        <div className={styles.projectCard}>
          <div>
            <p className="section-label">Capstone</p>
            <h2>Build a production AI Research Assistant</h2>
            <p>
              The final project combines all 11 CWA layers, a ChromaDB RAG pipeline,
              streaming tool-calling agents, prompt caching, and an automated evaluation suite —
              in a single runnable Python file.
            </p>
            <Link className="button button--primary button--lg" to="/docs/Module7/Lesson4_CWA">
              Go to Final Project →
            </Link>
          </div>
          <div className={styles.projectStats}>
            {[
              ['11',   'CWA layers'],
              ['50%',  'Cost savings via prompt caching'],
              ['244',  'Automated tests'],
              ['10',   'Modules covered'],
            ].map(([stat, label]) => (
              <div key={label} className={styles.stat}>
                <span className={styles.statNum}>{stat}</span>
                <span className={styles.statLabel}>{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <Hero />
      <main>
        <Features />
        <QuickStart />
        <ModuleGrid />
        <FinalProject />
      </main>
    </Layout>
  );
}
