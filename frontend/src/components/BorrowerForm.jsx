import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, Loader2, ShieldCheck } from 'lucide-react';
import GlassCard from './GlassCard';
import Button from './Button';
import { TextField, NumberField, SelectField, CheckboxField } from './FormFields';
import { LOAN_TYPE_DEFAULTS, LOAN_TYPES } from '../constants/loanTypes';
import {
  calculateEmi,
  calculateDaysPastDue,
  calculateCollectionAttempts,
} from '../utils/calculations';
import { formatCurrencyINR } from '../utils/risk';

const STEPS = ['Borrower Details', 'Financial Details', 'Review & Predict'];

const initialForm = {
  first_name: '',
  last_name: '',
  gender: 'Male',
  age: '',
  monthly_income: '',
  num_dependents: '',
  loan_type: '',
  custom_scheme: false,
  interest_rate: '',
  loan_tenure: '',
  loan_amount: '',
  collateral_value: '',
  outstanding_loan: '',
  missed_payments: '',
};

export default function BorrowerForm({ onSubmit, isLoading, error }) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(initialForm);

  const defaults = form.loan_type ? LOAN_TYPE_DEFAULTS[form.loan_type] : null;

  const effectiveRate = form.custom_scheme
    ? Number(form.interest_rate) || 0
    : defaults?.interestRate ?? 0;
  const effectiveTenure = form.custom_scheme
    ? Number(form.loan_tenure) || 0
    : defaults?.tenure ?? 0;

  const monthlyEmi = useMemo(
    () => calculateEmi(Number(form.loan_amount), effectiveRate, effectiveTenure),
    [form.loan_amount, effectiveRate, effectiveTenure]
  );
  const daysPastDue = calculateDaysPastDue(Number(form.missed_payments));
  const collectionAttempts = calculateCollectionAttempts(Number(form.missed_payments), daysPastDue);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function next() {
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  }
  function back() {
    setStep((s) => Math.max(s - 1, 0));
  }

  const isStep0Valid =
    form.first_name.trim() && form.last_name.trim() && form.age && form.monthly_income !== '' && form.num_dependents !== '';

  const isStep1Valid =
    form.loan_type &&
    form.loan_amount &&
    form.collateral_value !== '' &&
    form.outstanding_loan !== '' &&
    form.missed_payments !== '';

  function handleSubmit() {
    onSubmit({
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      gender: form.gender,
      age: Number(form.age),
      monthly_income: Number(form.monthly_income),
      num_dependents: Number(form.num_dependents),
      loan_type: form.loan_type,
      loan_amount: Number(form.loan_amount),
      collateral_value: Number(form.collateral_value),
      outstanding_loan: Number(form.outstanding_loan),
      missed_payments: Number(form.missed_payments),
      interest_rate: form.custom_scheme ? Number(form.interest_rate) : null,
      loan_tenure: form.custom_scheme ? Number(form.loan_tenure) : null,
    });
  }

  return (
    <GlassCard className="p-6 sm:p-10 max-w-2xl mx-auto">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {STEPS.map((label, i) => (
          <div key={label} className="flex items-center gap-2 flex-1">
            <div
              className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold shrink-0 transition-colors ${
                i <= step ? 'bg-lime text-night' : 'bg-line text-mute'
              }`}
            >
              {i + 1}
            </div>
            <span className={`text-xs hidden sm:inline ${i <= step ? 'text-white' : 'text-mute'}`}>{label}</span>
            {i < STEPS.length - 1 && <div className={`flex-1 h-px ${i < step ? 'bg-lime' : 'bg-line'}`} />}
          </div>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {step === 0 && (
          <motion.div key="step0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            <h2 className="font-display text-2xl font-semibold text-white mb-1">Borrower Details</h2>
            <p className="text-sm text-mute mb-6">The basics that shape every downstream calculation.</p>

            <div className="grid sm:grid-cols-2 gap-x-6">
              <TextField label="First Name" placeholder="e.g. Rahul" value={form.first_name} onChange={(e) => update('first_name', e.target.value)} />
              <TextField label="Last Name" placeholder="e.g. Sharma" value={form.last_name} onChange={(e) => update('last_name', e.target.value)} />
              <SelectField label="Gender" value={form.gender} onChange={(e) => update('gender', e.target.value)}>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </SelectField>
              <NumberField label="Age" placeholder="e.g. 35" min={18} max={100} value={form.age} onChange={(e) => update('age', e.target.value)} />
              <NumberField label="Monthly Income (₹)" placeholder="e.g. 50000" min={0} value={form.monthly_income} onChange={(e) => update('monthly_income', e.target.value)} />
              <NumberField label="Number of Dependents" placeholder="e.g. 2" min={0} value={form.num_dependents} onChange={(e) => update('num_dependents', e.target.value)} />
            </div>

            <div className="flex justify-end mt-4">
              <Button variant="primary" disabled={!isStep0Valid} onClick={next}>
                Continue <ArrowRight size={16} />
              </Button>
            </div>
          </motion.div>
        )}

        {step === 1 && (
          <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            <h2 className="font-display text-2xl font-semibold text-white mb-1">Financial Details</h2>
            <p className="text-sm text-mute mb-6">EMI and days past due are calculated automatically.</p>

            <SelectField label="Loan Type" value={form.loan_type} onChange={(e) => update('loan_type', e.target.value)}>
              <option value="">Select Loan Type</option>
              {LOAN_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </SelectField>

            {defaults && (
              <p className="text-xs text-lime/80 -mt-3 mb-4">
                Typical terms for a {form.loan_type} loan: {defaults.interestRate}% interest for {defaults.tenure} months
              </p>
            )}

            {form.loan_type && (
              <CheckboxField
                label="Loan applied during a special scheme or offer?"
                checked={form.custom_scheme}
                onChange={(e) => update('custom_scheme', e.target.checked)}
              />
            )}

            <div className="grid sm:grid-cols-2 gap-x-6">
              {form.custom_scheme ? (
                <>
                  <NumberField label="Custom Interest Rate (%)" min={0} max={100} step="0.1" value={form.interest_rate} onChange={(e) => update('interest_rate', e.target.value)} />
                  <NumberField label="Custom Tenure (Months)" min={1} max={360} value={form.loan_tenure} onChange={(e) => update('loan_tenure', e.target.value)} />
                </>
              ) : (
                form.loan_type && (
                  <>
                    <NumberField label="Interest Rate (%)" value={defaults.interestRate} disabled />
                    <NumberField label="Loan Tenure (Months)" value={defaults.tenure} disabled />
                  </>
                )
              )}
              <NumberField label="Loan Amount (₹)" placeholder="e.g. 300000" min={10000} value={form.loan_amount} onChange={(e) => update('loan_amount', e.target.value)} />
              <NumberField label="Collateral Value (₹)" placeholder="e.g. 200000" min={0} value={form.collateral_value} onChange={(e) => update('collateral_value', e.target.value)} />
              <NumberField label="Outstanding Loan Amount (₹)" placeholder="e.g. 150000" min={0} value={form.outstanding_loan} onChange={(e) => update('outstanding_loan', e.target.value)} />
              <NumberField label="Missed Payments" placeholder="e.g. 1" min={0} value={form.missed_payments} onChange={(e) => update('missed_payments', e.target.value)} />
              <NumberField label="Days Past Due (auto)" value={form.missed_payments !== '' ? daysPastDue : ''} disabled hint="1 missed payment = 30 days" />
              <NumberField label="Collection Attempts (auto)" value={form.missed_payments !== '' ? collectionAttempts : ''} disabled />
            </div>

            {monthlyEmi != null && (
              <p className="text-sm text-white mt-1 mb-2">
                <span className="text-mute">Auto-calculated EMI:</span>{' '}
                <span className="font-mono text-lime">{formatCurrencyINR(monthlyEmi)}</span>
              </p>
            )}

            <div className="flex justify-between mt-6">
              <Button variant="ghost" onClick={back}><ArrowLeft size={16} /> Back</Button>
              <Button variant="primary" disabled={!isStep1Valid} onClick={next}>
                Review <ArrowRight size={16} />
              </Button>
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            <h2 className="font-display text-2xl font-semibold text-white mb-1">Review &amp; Predict</h2>
            <p className="text-sm text-mute mb-6">Confirm the details below, then run the model.</p>

            <dl className="grid sm:grid-cols-2 gap-y-3 gap-x-6 text-sm mb-6">
              <ReviewRow label="Name" value={`${form.first_name} ${form.last_name}`} />
              <ReviewRow label="Age / Gender" value={`${form.age} / ${form.gender}`} />
              <ReviewRow label="Monthly Income" value={formatCurrencyINR(Number(form.monthly_income) || 0)} />
              <ReviewRow label="Dependents" value={form.num_dependents} />
              <ReviewRow label="Loan Type" value={form.loan_type} />
              <ReviewRow label="Loan Amount" value={formatCurrencyINR(Number(form.loan_amount) || 0)} />
              <ReviewRow label="Collateral Value" value={formatCurrencyINR(Number(form.collateral_value) || 0)} />
              <ReviewRow label="Outstanding Loan" value={formatCurrencyINR(Number(form.outstanding_loan) || 0)} />
              <ReviewRow label="Missed Payments" value={form.missed_payments} />
              <ReviewRow label="Estimated EMI" value={monthlyEmi != null ? formatCurrencyINR(monthlyEmi) : '—'} />
            </dl>

            {error && (
              <p className="text-sm text-risk-high bg-risk-high/10 border border-risk-high/30 rounded-xl px-4 py-3 mb-4">
                {error}
              </p>
            )}

            <div className="flex justify-between mt-6">
              <Button variant="ghost" onClick={back} disabled={isLoading}><ArrowLeft size={16} /> Back</Button>
              <Button variant="primary" onClick={handleSubmit} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" /> Predicting…
                  </>
                ) : (
                  <>
                    <ShieldCheck size={16} /> Predict Risk &amp; Strategy
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </GlassCard>
  );
}

function ReviewRow({ label, value }) {
  return (
    <div className="flex justify-between border-b border-line pb-2">
      <dt className="text-mute">{label}</dt>
      <dd className="text-white font-medium">{value || '—'}</dd>
    </div>
  );
}
