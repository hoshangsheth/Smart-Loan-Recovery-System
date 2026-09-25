import LegalPage from '../../components/LegalPage';
import { LEGAL_CONTACT_EMAIL, LEGAL_OPERATOR } from '../../constants/legal';

const mail = <a href={`mailto:${LEGAL_CONTACT_EMAIL}`}>{LEGAL_CONTACT_EMAIL}</a>;

const sections = [
  {
    heading: 'Who is responsible for your data',
    body: (
      <p>
        Recovia is operated by {LEGAL_OPERATOR}, who acts as the Data Fiduciary for account data under India's Digital
        Personal Data Protection Act, 2023 ("DPDP Act"). For borrower data you enter, you (or the lender you act for)
        decide why it is processed, and we process it to provide the service to you.
      </p>
    ),
  },
  {
    heading: 'What we collect',
    body: (
      <ul>
        <li>
          <strong>Account data:</strong> your email address and sign-in method (email/password or Google). Passwords
          are handled by our authentication provider; we never see them in plain text.
        </li>
        <li>
          <strong>Borrower data you enter:</strong> name, age, gender, income, dependents, loan amount and terms,
          collateral, missed payments, days past due and collection attempts, plus the risk scores and AI briefs
          generated from them.
        </li>
        <li>
          <strong>Records we keep for accountability:</strong> when you accepted our terms (with your browser's user
          agent), an audit log of actions on cases, and how many AI briefs you have used.
        </li>
      </ul>
    ),
  },
  {
    heading: 'Why we use it',
    body: (
      <ul>
        <li>to score recovery risk, save cases and show their history;</li>
        <li>to generate AI case briefs when you ask for one;</li>
        <li>to secure the service, enforce usage limits and prevent abuse;</li>
        <li>to meet legal obligations and respond to your requests.</li>
      </ul>
    ),
  },
  {
    heading: 'Using the public predictor without an account',
    body: (
      <p>
        If you are not signed in, the details you enter are used only to calculate the result on your screen and are
        not saved to our database.
      </p>
    ),
  },
  {
    heading: 'AI processing',
    body: (
      <p>
        AI case briefs are generated with Google's Gemini API. We send only loan and repayment figures, the model's
        risk outputs and case status. <strong>Borrower names, gender and contact details are never sent.</strong> The
        borrower's name is inserted into the draft message inside your browser.
      </p>
    ),
  },
  {
    heading: 'Service providers',
    body: (
      <>
        <p>We use these providers to run Recovia. They process data on our behalf:</p>
        <ul>
          <li>Supabase: database and user authentication;</li>
          <li>Render: application servers (API);</li>
          <li>Vercel: website hosting;</li>
          <li>Google: Gemini API for AI briefs, Google sign-in if you choose it, and web fonts.</li>
        </ul>
        <p>These providers may store or process data outside India. We don't sell personal data or use it for advertising.</p>
      </>
    ),
  },
  {
    heading: 'How long we keep it',
    body: (
      <p>
        Account data and saved cases are kept until you delete them or ask us to delete your account. Consent and
        audit records may be kept longer where needed to show compliance or resolve disputes.
      </p>
    ),
  },
  {
    heading: 'Security',
    body: (
      <p>
        Data is encrypted in transit (HTTPS). Each account can only see its own cases, and database access from the
        browser is blocked by row-level security. No system is perfectly secure, so please tell us at once if you
        suspect a problem.
      </p>
    ),
  },
  {
    heading: 'Your rights',
    body: (
      <>
        <p>Under the DPDP Act you can ask us to:</p>
        <ul>
          <li>tell you what personal data we hold about you and how it is processed;</li>
          <li>correct, complete or update it;</li>
          <li>erase it, and withdraw your consent (this ends your access to signed-in features);</li>
          <li>nominate another person to exercise these rights on your behalf.</li>
        </ul>
        <p>Email {mail} from the address on your account. Borrowers whose data was entered by a lender should contact that lender first.</p>
      </>
    ),
  },
  {
    heading: 'Browser storage and cookies',
    body: (
      <p>
        We store your sign-in session in your browser's local storage so you stay signed in. We don't use advertising
        or tracking cookies.
      </p>
    ),
  },
  {
    heading: 'Children',
    body: <p>Recovia is for professional use and is not intended for anyone under 18.</p>,
  },
  {
    heading: 'Grievance Officer and changes',
    body: (
      <p>
        Grievance Officer: {LEGAL_OPERATOR}, {mail}. We aim to respond within 30 days. If we change this policy
        materially we will ask you to accept the new version.
      </p>
    ),
  },
];

export default function Privacy() {
  return (
    <LegalPage
      title="Privacy Policy"
      intro="This policy explains what personal data Recovia collects, why, who it is shared with, and the rights you have over it."
      sections={sections}
    />
  );
}
