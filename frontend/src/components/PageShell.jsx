import Nav from './Nav';

export default function PageShell({ children, width = 'max-w-6xl' }) {
  return (
    <div className="min-h-screen bg-night">
      <Nav />
      <main className={`px-4 sm:px-6 pt-32 pb-24 mx-auto ${width}`}>{children}</main>
    </div>
  );
}
