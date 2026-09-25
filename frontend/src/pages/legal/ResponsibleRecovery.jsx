import LegalPage from '../../components/LegalPage';
import { LEGAL_CONTACT_EMAIL } from '../../constants/legal';

const ASSET_CLASSES = [
  ['Standard', '0 days'],
  ['SMA-0', '1–30 days'],
  ['SMA-1', '31–60 days'],
  ['SMA-2', '61–90 days'],
  ['NPA', 'More than 90 days'],
];

const sections = [
  {
    heading: 'Why this matters',
    body: (
      <p>
        Recovia helps prioritise and plan recoveries, but the people and lenders who act on it are bound by Reserve
        Bank of India directions on fair practices in lending and recovery. Using Recovia means committing to follow
        them. This page is a practical summary, not legal advice. Always check the latest RBI circulars that apply to
        your organisation.
      </p>
    ),
  },
  {
    heading: 'How Recovia classifies accounts',
    body: (
      <>
        <p>
          Recovia shows each account's stage using RBI's early-stress (Special Mention Account) and Non-Performing
          Asset bands, based on days past due:
        </p>
        <table className="w-full text-left border-collapse my-2">
          <thead>
            <tr className="border-b border-line text-white">
              <th className="py-2 pr-4 font-medium">Class</th>
              <th className="py-2 font-medium">Days past due</th>
            </tr>
          </thead>
          <tbody>
            {ASSET_CLASSES.map(([name, dpd]) => (
              <tr key={name} className="border-b border-line/60">
                <td className="py-2 pr-4 font-mono text-white">{name}</td>
                <td className="py-2">{dpd}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p>
          The model's score can never place an NPA account below High Risk or an SMA-2 account below Medium Risk, and
          a case is only marked Critical when the model's estimate is very high <strong>and</strong> the account is an
          NPA.
        </p>
      </>
    ),
  },
  {
    heading: 'When contacting borrowers',
    body: (
      <ul>
        <li>
          <strong>Call only between 8:00 a.m. and 7:00 p.m.</strong>, as RBI's directions on recovery agents require.
        </li>
        <li>
          Never use intimidation or harassment of any kind, whether verbal or physical, including threatening,
          abusive, anonymous or persistent calls.
        </li>
        <li>
          Never publicly humiliate a borrower or intrude on the privacy of their family members, referees or friends.
        </li>
        <li>Never make false or misleading statements about the debt or its consequences.</li>
        <li>Identify yourself and the lender you represent, and keep contact respectful and courteous.</li>
        <li>Offer a chance to discuss restructuring or a repayment plan before escalating.</li>
      </ul>
    ),
  },
  {
    heading: 'Using AI drafts responsibly',
    body: (
      <p>
        Recovia's AI briefs are instructed to follow these principles, but they are drafts. Read and edit every
        message before sending it, check the facts against your records, and never send a draft that threatens,
        misstates the law or reveals the borrower's situation to anyone else.
      </p>
    ),
  },
  {
    heading: 'Escalation and legal action',
    body: (
      <p>
        Legal notices and proceedings are decisions for authorised staff under your organisation's board-approved
        recovery policy, never something to automate from a risk score. Recovia only suggests them for Critical cases,
        and a person must review every case before acting.
      </p>
    ),
  },
  {
    heading: 'Borrower grievances',
    body: (
      <p>
        Lenders must give borrowers a way to raise complaints about recovery practices. Complaints about a regulated
        entity that it hasn't resolved can be taken to the RBI under the Reserve Bank – Integrated Ombudsman Scheme.
        Concerns about how Recovia itself works can be sent to{' '}
        <a href={`mailto:${LEGAL_CONTACT_EMAIL}`}>{LEGAL_CONTACT_EMAIL}</a>.
      </p>
    ),
  },
];

export default function ResponsibleRecovery() {
  return (
    <LegalPage
      title="Responsible Recovery (RBI)"
      intro="The standards every Recovia user agrees to follow when acting on scores, strategies and AI drafts."
      sections={sections}
    />
  );
}
