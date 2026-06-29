import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Menu, X, ShieldCheck } from 'lucide-react';
import Button from './Button';

const LINKS = [
  { label: 'Overview', href: '/#overview' },
  { label: 'How it works', href: '/#workflow' },
  { label: 'Contact', href: '/#contact' },
];

export default function Nav() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="fixed top-4 inset-x-0 z-50 flex justify-center px-4">
      <motion.div
        initial={{ y: -24, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="flex w-full max-w-3xl items-center justify-between rounded-full border border-line bg-slate/70 backdrop-blur-xl px-5 py-2.5"
      >
        <Link to="/" className="flex items-center gap-2 font-display font-semibold text-white">
          <ShieldCheck className="text-lime" size={20} />
          <span>SLRS</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm text-mute">
          {LINKS.map((link) => (
            <a key={link.label} href={link.href} className="hover:text-white transition-colors">
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:block">
          <Button variant="primary" className="px-5 py-2 text-sm" onClick={() => navigate('/predictor')}>
            Launch Predictor
          </Button>
        </div>

        <button
          className="md:hidden text-white"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? 'Close menu' : 'Open menu'}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </motion.div>

      {open && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-16 w-[calc(100%-2rem)] max-w-3xl rounded-3xl border border-line bg-slate/95 backdrop-blur-xl p-5 md:hidden"
        >
          <div className="flex flex-col gap-4 text-sm text-mute">
            {LINKS.map((link) => (
              <a key={link.label} href={link.href} onClick={() => setOpen(false)} className="hover:text-white">
                {link.label}
              </a>
            ))}
            <Button
              variant="primary"
              className="w-full"
              onClick={() => {
                setOpen(false);
                navigate('/predictor');
              }}
            >
              Launch Predictor
            </Button>
          </div>
        </motion.div>
      )}
    </header>
  );
}
