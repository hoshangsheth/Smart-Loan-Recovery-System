import Nav from '../components/Nav';
import Hero from '../components/Hero';
import WorkflowSection from '../components/WorkflowSection';
import FeaturesSection from '../components/FeaturesSection';
import ContactSection from '../components/ContactSection';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen bg-night">
      <Nav />
      <Hero />
      <WorkflowSection />
      <FeaturesSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
