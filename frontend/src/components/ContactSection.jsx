import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle } from 'lucide-react';
import Button from './Button';
import { getWhatsAppLink } from '../services/api';

export default function ContactSection() {
  const [link, setLink] = useState('https://wa.me/919004001598');

  useEffect(() => {
    getWhatsAppLink()
      .then((data) => data?.url && setLink(data.url))
      .catch(() => {
        /* fall back to the default link above if the backend is unreachable */
      });
  }, []);

  return (
    <section className="px-6 py-24" id="contact">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl mx-auto rounded-[2.5rem] bg-lime text-night px-10 py-16 text-center relative overflow-hidden"
      >
        <div className="absolute -top-24 -right-24 w-72 h-72 bg-night/10 rounded-full blur-3xl" />
        <h2 className="font-display text-4xl sm:text-5xl font-bold mb-4">
          Have a portfolio to assess?
        </h2>
        <p className="text-night/70 max-w-md mx-auto mb-8">
          Message our team directly on WhatsApp — we'll walk you through onboarding your
          borrower data.
        </p>
        <Button
          variant="ghost"
          className="border-night/20 text-night hover:border-night hover:text-night bg-night/5"
          onClick={() => window.open(link, '_blank', 'noopener,noreferrer')}
        >
          <MessageCircle size={18} /> Chat on WhatsApp
        </Button>
      </motion.div>
    </section>
  );
}
