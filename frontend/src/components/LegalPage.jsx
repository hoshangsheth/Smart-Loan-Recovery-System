import { Link } from 'react-router-dom';
import PageShell from './PageShell';
import Footer from './Footer';
import { LEGAL_LAST_UPDATED, LEGAL_LINKS } from '../constants/legal';

/** Shared layout for policy pages. `sections` is [{ heading, body: ReactNode }]. */
export default function LegalPage({ title, intro, sections }) {
  return (
    <>
      <PageShell width="max-w-3xl">
        <p className="text-xs uppercase tracking-wider text-lime">Legal</p>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2">{title}</h1>
        <p className="text-sm text-mute mt-2">Last updated {LEGAL_LAST_UPDATED}</p>
        <nav aria-label="Policies" className="flex flex-wrap gap-2 mt-6">
          {LEGAL_LINKS.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="rounded-full border border-line px-3 py-1.5 text-xs text-mute hover:text-lime hover:border-lime/50"
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <p className="text-white/90 leading-relaxed mt-8">{intro}</p>
        <div className="mt-8 space-y-8">
          {sections.map((section, i) => (
            <section key={section.heading} aria-labelledby={`legal-${i}`}>
              <h2 id={`legal-${i}`} className="font-display text-xl font-semibold text-white mb-3">
                {i + 1}. {section.heading}
              </h2>
              <div className="space-y-3 text-sm text-mute leading-relaxed [&_li]:ml-5 [&_li]:list-disc [&_strong]:text-white [&_a]:text-lime">
                {section.body}
              </div>
            </section>
          ))}
        </div>
      </PageShell>
      <Footer />
    </>
  );
}
