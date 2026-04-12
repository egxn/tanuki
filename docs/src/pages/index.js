import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HeroSection() {
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">Tanuki</h1>
        <p className="hero__subtitle">
          A declarative Python DSL for procedural geometry that compiles to multiple backends.
        </p>
        <div className={styles.buttons}>
          <Link className="button button--secondary button--lg" to="/docs/quickstart">
            Get Started →
          </Link>
          <Link className="button button--outline button--secondary button--lg" to="/docs/dsl/overview" style={{ marginLeft: '1rem' }}>
            DSL Reference
          </Link>
        </div>
      </div>
    </header>
  );
}

const features = [
  {
    title: 'Declarative & Functional',
    description:
      'Build 3D geometry with pure Python functions. Models are composable IR trees — no side effects, no state.',
    code: `with model("bracket") as ctx:
    base = cube(20, 10, 3)
    hole = cylinder(2, 5) | translate(0, 0, 0)
    result = difference(base, [hole])
    output(result)`,
  },
  {
    title: 'Multiple Backends',
    description:
      'Compile the same DSL graph to Blender Geometry Nodes, OpenSCAD, JSCAD, or OpenCascade.js.',
    code: `render(graph, target="blender")      # → .py (bpy script)
render(graph, target="openscad")     # → .scad
render(graph, target="jscad")        # → .jscad
render(graph, target="opencascade")  # → .js (OCCT)`,
  },
  {
    title: 'Pipe Composition',
    description:
      'Chain transforms with the | operator. Models read like a description of the geometry they produce.',
    code: `part = (
    cylinder(3, 12, "pillar")
    | translate(0, 0, 7.5)
    | rotate(0, 0, 45)
    | scale_by(1.5, 1.5, 1.5)
)`,
  },
];

function FeatureCard({ title, description, code }) {
  return (
    <div className={clsx('col col--4', styles.featureCard)}>
      <h3>{title}</h3>
      <p>{description}</p>
      <pre className={styles.codeSnippet}><code>{code}</code></pre>
    </div>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <HeroSection />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((f, i) => <FeatureCard key={i} {...f} />)}
            </div>
          </div>
        </section>
        <section className={styles.backends}>
          <div className="container">
            <h2>Supported Backends</h2>
            <div className="row" style={{ textAlign: 'center' }}>
              {[
                { name: 'Blender', ext: '.py', desc: 'Geometry Nodes via bpy' },
                { name: 'OpenSCAD', ext: '.scad', desc: 'CSG with native OpenSCAD ops' },
                { name: 'JSCAD', ext: '.jscad', desc: '@jscad/modeling CommonJS module' },
                { name: 'OpenCascade.js', ext: '.js', desc: 'BREP solids via OCCT WASM' },
              ].map((b) => (
                <div key={b.name} className="col col--3">
                  <div className={styles.backendCard}>
                    <div className={styles.backendExt}>{b.ext}</div>
                    <strong>{b.name}</strong>
                    <p>{b.desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
              <Link className="button button--primary" to="/docs/backends/overview">
                Backend comparison →
              </Link>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
