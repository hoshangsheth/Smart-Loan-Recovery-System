import { ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="px-6 py-10 border-t border-line">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-white font-display font-semibold">
          <ShieldCheck className="text-lime" size={18} />
          Recovia
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-2 text-sm text-mute">
          <span>
            ML-assisted risk scoring for internal collections use. Not a substitute
            for regulatory or legal advice.
          </span>

          <span className="hidden sm:inline">•</span>

          <span>
            Built by{" "}
            <a
              href="https://hoshangsheth.com"
              target="_blank"
              rel="noreferrer"
              className="text-lime hover:underline"
            >
              Hoshang Sheth
            </a>
          </span>
        </div>
      </div>
    </footer>
  );
}
